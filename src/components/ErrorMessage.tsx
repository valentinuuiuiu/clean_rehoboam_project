import React from 'react';

interface ErrorMessageProps {
  error: Error | string | null;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ error }) => {
  if (!error) return null;
  
  const errorMessage = error instanceof Error ? error.message : error;
  
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong className="font-bold">Error: </strong>
      <span className="block sm:inline">{errorMessage}</span>
    </div>
  );
};