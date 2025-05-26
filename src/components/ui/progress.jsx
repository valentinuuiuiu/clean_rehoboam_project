import React from 'react';

/**
 * Progress component for displaying progress bars
 */
export const Progress = ({ value = 0, max = 100, className = '', ...props }) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  return (
    <div className={`w-full bg-gray-700 rounded-full h-2.5 ${className}`} {...props}>
      <div 
        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};