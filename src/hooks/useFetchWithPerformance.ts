import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { usePerformance } from '../contexts/PerformanceContext';
import { useNotification } from '../contexts/NotificationContext';

interface UseFetchOptions<TData> extends Omit<UseQueryOptions<TData, Error>, 'queryKey' | 'queryFn'> {
  componentName: string;
  cacheTime?: number;
  retryDelay?: number;
  successMessage?: string;
  errorMessage?: string;
}

export function useFetchWithPerformance<TData>(
  queryKey: string[],
  fetchFn: () => Promise<TData>,
  {
    componentName,
    cacheTime = 5 * 60 * 1000, // 5 minutes
    retryDelay = 1000,
    successMessage,
    errorMessage,
    ...options
  }: UseFetchOptions<TData>
) {
  const { recordMetric } = usePerformance();
  const { addNotification } = useNotification();

  return useQuery<TData, Error>({
    queryKey,
    queryFn: async () => {
      const startTime = performance.now();
      try {
        const data = await fetchFn();
        const fetchTime = performance.now() - startTime;
        
        recordMetric({
          componentName,
          renderTime: fetchTime,
          type: 'fetch'
        });

        if (successMessage) {
          addNotification('success', successMessage);
        }

        return data;
      } catch (error) {
        const fetchTime = performance.now() - startTime;
        recordMetric({
          componentName,
          renderTime: fetchTime,
          type: 'fetch'
        });

        addNotification('error', errorMessage || error.message || 'Failed to fetch data');
        throw error;
      }
    },
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error.response?.status && error.response.status >= 400 && error.response.status < 500) {
        return false;
      }
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * Math.pow(2, attemptIndex), 30000),
    cacheTime,
    ...options
  });
}