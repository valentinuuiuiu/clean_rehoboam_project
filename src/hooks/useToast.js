import { useState } from 'react';

/**
 * A simple hook for creating toast notifications.
 * 
 * @returns {Object} Toast functionality
 */
export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  /**
   * Add a new toast notification
   * 
   * @param {Object} toast Toast configuration
   * @param {string} toast.title The toast title
   * @param {string} toast.description The toast description
   * @param {string} toast.variant The toast variant (default, destructive)
   * @param {number} toast.duration Duration in ms before auto-dismiss (default 3000)
   */
  const toast = ({ 
    title, 
    description, 
    variant = 'default', 
    duration = 3000 
  }) => {
    const id = Date.now().toString();
    
    // Add the new toast to the array
    setToasts(prevToasts => [
      ...prevToasts,
      { id, title, description, variant, duration }
    ]);
    
    // Auto-dismiss after duration
    setTimeout(() => {
      dismiss(id);
    }, duration);
    
    return id;
  };

  /**
   * Dismiss a specific toast by id
   * 
   * @param {string} id The toast id to dismiss
   */
  const dismiss = (id) => {
    setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
  };

  /**
   * Dismiss all toasts
   */
  const dismissAll = () => {
    setToasts([]);
  };

  // Return the hook interface
  return {
    toasts,
    toast,
    dismiss,
    dismissAll
  };
};

export default useToast;