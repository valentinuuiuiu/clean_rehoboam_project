import React from 'react';

const LoadingSpinner = ({ size = 'md', color = 'blue', className = '' }) => {
  // Map size names to actual pixel sizes
  const sizeMap = {
    xs: 'h-4 w-4',
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  };

  // Map color names to tailwind classes
  const colorMap = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    red: 'border-red-500',
    yellow: 'border-yellow-500',
    purple: 'border-purple-500',
    gray: 'border-gray-500',
    white: 'border-white',
  };

  // Get the correct size class or default to medium
  const sizeClass = sizeMap[size] || sizeMap.md;
  // Get the correct color class or default to blue
  const colorClass = colorMap[color] || colorMap.blue;

  return (
    <div className={`${className} inline-block`}>
      <div className={`${sizeClass} animate-spin rounded-full border-4 ${colorClass} border-t-transparent`}></div>
    </div>
  );
};

export default LoadingSpinner;