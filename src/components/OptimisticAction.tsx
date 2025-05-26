import React, { useState, ReactNode } from 'react';
import LoadingSpinner from './ui/LoadingSpinner';

interface OptimisticActionProps {
  action: () => Promise<any>;
  children: ReactNode;
  onSuccess?: (result: any) => void;
  onError?: (error: any) => void;
  loadingText?: string;
  successNode?: ReactNode;
  errorNode?: ReactNode;
  revertDelay?: number;
  className?: string;
  disabled?: boolean;
}

const OptimisticAction: React.FC<OptimisticActionProps> = ({
  action,
  children,
  onSuccess,
  onError,
  loadingText = 'Processing...',
  successNode = <span className="text-green-500">Success!</span>,
  errorNode,
  revertDelay = 2000,
  className = '',
  disabled = false,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<any>(null);
  const [isErrorVisible, setIsErrorVisible] = useState(false);

  const handleClick = async () => {
    if (disabled || isLoading) return;

    setIsLoading(true);
    setError(null);
    setIsErrorVisible(false);

    try {
      // Simulate optimistic update
      setIsSuccess(true);
      
      // Call the actual action
      const result = await action();
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      // Keep success UI for a moment then revert
      setTimeout(() => {
        setIsSuccess(false);
        setIsLoading(false);
      }, revertDelay);
    } catch (err) {
      // Handle error
      setIsSuccess(false);
      setError(err);
      setIsErrorVisible(true);
      setIsLoading(false);
      
      if (onError) {
        onError(err);
      }
      
      // Hide error after delay
      setTimeout(() => {
        setIsErrorVisible(false);
      }, 5000);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={handleClick}
        disabled={disabled || isLoading}
        className={`relative ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
      >
        {isLoading ? (
          <span className="flex items-center">
            <LoadingSpinner size="sm" className="mr-2" />
            {loadingText}
          </span>
        ) : isSuccess ? (
          successNode
        ) : (
          children
        )}
      </button>
      
      {isErrorVisible && error && (
        <div className="absolute left-0 top-full mt-2 bg-red-900 text-white px-3 py-2 rounded shadow-lg text-sm z-10">
          {errorNode || (
            <span>
              Error: {error.message || 'Unknown error occurred'}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default OptimisticAction;