import React from 'react';

/**
 * Separator component for visual division of content
 */
export const Separator = ({ className = '', ...props }) => {
  return (
    <div className={`h-px bg-gray-700 my-4 ${className}`} {...props} />
  );
};