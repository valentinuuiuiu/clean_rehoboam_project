import React from 'react';

/**
 * TabsList component
 */
export const TabsList = ({ children, className = '', ...props }) => {
  return (
    <div className={`flex space-x-2 mb-4 ${className}`} {...props}>
      {children}
    </div>
  );
};

/**
 * TabsTrigger component
 */
export const TabsTrigger = ({ 
  children, 
  value, 
  active, 
  onClick, 
  className = '', 
  ...props 
}) => {
  return (
    <button
      className={`px-4 py-2 font-medium rounded-md ${
        active 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
      } ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

/**
 * TabsContent component
 */
export const TabsContent = ({ 
  children, 
  value, 
  activeTab,
  className = '', 
  ...props 
}) => {
  if (value !== activeTab) return null;
  
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
};

/**
 * Tabs component
 */
export const Tabs = ({ 
  children, 
  defaultValue, 
  onChange, 
  className = '', 
  ...props 
}) => {
  const [value, setValue] = React.useState(defaultValue);
  
  const handleValueChange = (newValue) => {
    setValue(newValue);
    if (onChange) {
      onChange(newValue);
    }
  };
  
  // Create a new context to pass down value and onChange
  const contextValue = {
    value,
    onChange: handleValueChange,
  };
  
  return (
    <div className={className} {...props}>
      {React.Children.map(children, (child) => {
        // Pass props to children
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            active: child.props.value === value,
            activeTab: value,
            onClick: () => handleValueChange(child.props.value),
          });
        }
        return child;
      })}
    </div>
  );
};