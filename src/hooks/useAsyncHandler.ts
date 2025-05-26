import { useState, useCallback } from 'react';
import { useNotification } from '../contexts/NotificationContext';
import { useLoading } from '../contexts/LoadingContext';

interface UseAsyncHandlerOptions {
  loadingKey: string;
  successMessage?: string;
  errorMessage?: string;
}

export function useAsyncHandler<T>({ 
  loadingKey, 
  successMessage, 
  errorMessage 
}: UseAsyncHandlerOptions) {
  const [error, setError] = useState<Error | null>(null);
  const { addNotification } = useNotification();
  const { startLoading, stopLoading } = useLoading();

  const handleAsync = useCallback(async (
    asyncFn: () => Promise<T>,
    onSuccess?: (result: T) => void
  ) => {
    setError(null);
    startLoading(loadingKey);
    
    try {
      const result = await asyncFn();
      if (successMessage) {
        addNotification('success', successMessage);
      }
      onSuccess?.(result);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(err instanceof Error ? err : new Error(message));
      addNotification('error', errorMessage || message);
      throw err;
    } finally {
      stopLoading(loadingKey);
    }
  }, [loadingKey, successMessage, errorMessage, addNotification, startLoading, stopLoading]);

  return {
    error,
    setError,
    handleAsync
  };
}