
import React from 'react';

interface ErrorMessageProps {
  error: Error | string;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ error, className = '' }) => {
  const errorMessage = error instanceof Error ? error.message : error;
  
  return (
    <div className={`p-4 bg-red-50 border border-red-200 rounded-lg ${className}`}>
      <p className="text-red-600">Error: {errorMessage}</p>
    </div>
  );
};