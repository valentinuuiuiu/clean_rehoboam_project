import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNotification } from '../contexts/NotificationContext';

interface OptimisticUpdateConfig<T> {
  queryKey: string[];
  mutationFn: (data: T) => Promise<any>;
  optimisticUpdate: (oldData: any, newData: T) => any;
  rollbackOnError?: boolean;
  successMessage?: string;
  errorMessage?: string;
}

export function useOptimisticMutation<T>({
  queryKey,
  mutationFn,
  optimisticUpdate,
  rollbackOnError = true,
  successMessage,
  errorMessage
}: OptimisticUpdateConfig<T>) {
  const queryClient = useQueryClient();
  const { addNotification } = useNotification();

  return useMutation({
    mutationFn,
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey });

      // Snapshot the previous value
      const previousData = queryClient.getQueryData(queryKey);

      // Optimistically update to the new value
      queryClient.setQueryData(queryKey, (old: any) => optimisticUpdate(old, newData));

      // Return context with the snapshot
      return { previousData };
    },
    onError: (err, newData, context: any) => {
      if (rollbackOnError) {
        // Rollback to the snapshot on error
        queryClient.setQueryData(queryKey, context.previousData);
      }
      
      // Show error notification
      addNotification(
        'error',
        errorMessage || err.message || 'An error occurred while processing your request'
      );
    },
    onSuccess: () => {
      if (successMessage) {
        addNotification('success', successMessage);
      }
    },
    onSettled: () => {
      // Always refetch after error or success to ensure data consistency
      queryClient.invalidateQueries({ queryKey });
    },
  });
}