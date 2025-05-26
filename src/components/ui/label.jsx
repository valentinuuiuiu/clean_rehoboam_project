import React from 'react';

/**
 * Label component for form inputs
 */
export const Label = ({ children, className = '', ...props }) => {
  return (
    <label className={`text-sm font-medium text-gray-300 ${className}`} {...props}>
      {children}
    </label>
  );
};