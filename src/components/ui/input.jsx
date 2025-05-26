import React from 'react';

/**
 * Input component for user text entry
 */
export const Input = ({ className = '', ...props }) => {
  return (
    <input
      className={`w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
      {...props}
    />
  );
};