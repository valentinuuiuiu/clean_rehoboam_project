import React from 'react';

/**
 * Button component for user interactions
 */
export const Button = ({ children, className = '', disabled = false, ...props }) => {
  return (
    <button
      className={`px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};