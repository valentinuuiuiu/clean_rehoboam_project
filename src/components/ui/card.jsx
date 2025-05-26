import React from 'react';

/**
 * Card component for containing content
 */
export const Card = ({ children, className = '', ...props }) => {
  return (
    <div
      className={`bg-gray-800 rounded-lg shadow-md border border-gray-700 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

/**
 * Card header for title section
 */
export const CardHeader = ({ children, className = '', ...props }) => {
  return (
    <div className={`p-4 ${className}`} {...props}>
      {children}
    </div>
  );
};

/**
 * Card title component
 */
export const CardTitle = ({ children, className = '', ...props }) => {
  return (
    <h3 className={`text-xl font-bold ${className}`} {...props}>
      {children}
    </h3>
  );
};

/**
 * Card description component
 */
export const CardDescription = ({ children, className = '', ...props }) => {
  return (
    <p className={`text-gray-400 mt-1 ${className}`} {...props}>
      {children}
    </p>
  );
};

/**
 * Card content component
 */
export const CardContent = ({ children, className = '', ...props }) => {
  return (
    <div className={`p-4 pt-0 ${className}`} {...props}>
      {children}
    </div>
  );
};

/**
 * Card footer component
 */
export const CardFooter = ({ children, className = '', ...props }) => {
  return (
    <div className={`p-4 border-t border-gray-700 ${className}`} {...props}>
      {children}
    </div>
  );
};