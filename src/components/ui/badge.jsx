import React from 'react';

/**
 * Badge component for displaying status or labels
 */
export const Badge = ({ children, className = '', ...props }) => {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs bg-blue-900/30 text-blue-300 ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};