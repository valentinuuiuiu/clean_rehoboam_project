import React, { createContext, useContext, useCallback, useState } from 'react';
import { useNotification } from './NotificationContext';

interface Task {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  error?: Error;
  startTime?: number;
  endTime?: number;
}

interface BackgroundTaskContextType {
  tasks: Task[];
  startTask: (name: string) => string;
  updateTaskProgress: (id: string, progress: number) => void;
  completeTask: (id: string) => void;
  failTask: (id: string, error: Error) => void;
  getTaskStatus: (id: string) => Task | undefined;
}

const BackgroundTaskContext = createContext<BackgroundTaskContextType | null>(null);

export const BackgroundTaskProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const { addNotification } = useNotification();

  const startTask = useCallback((name: string) => {
    const id = Math.random().toString(36).substring(2);
    const task: Task = {
      id,
      name,
      status: 'running',
      startTime: Date.now()
    };

    setTasks(prev => [...prev, task]);
    addNotification('info', `Started task: ${name}`);
    return id;
  }, [addNotification]);

  const updateTaskProgress = useCallback((id: string, progress: number) => {
    setTasks(prev => prev.map(task => 
      task.id === id ? { ...task, progress } : task
    ));
  }, []);

  const completeTask = useCallback((id: string) => {
    setTasks(prev => prev.map(task => {
      if (task.id === id) {
        const duration = Date.now() - (task.startTime || 0);
        addNotification('success', `${task.name} completed in ${(duration / 1000).toFixed(1)}s`);
        return { ...task, status: 'completed', endTime: Date.now() };
      }
      return task;
    }));
  }, [addNotification]);

  const failTask = useCallback((id: string, error: Error) => {
    setTasks(prev => prev.map(task => {
      if (task.id === id) {
        addNotification('error', `${task.name} failed: ${error.message}`);
        return { ...task, status: 'failed', error, endTime: Date.now() };
      }
      return task;
    }));
  }, [addNotification]);

  const getTaskStatus = useCallback((id: string) => {
    return tasks.find(task => task.id === id);
  }, [tasks]);

  const value = {
    tasks,
    startTask,
    updateTaskProgress,
    completeTask,
    failTask,
    getTaskStatus
  };

  return (
    <BackgroundTaskContext.Provider value={value}>
      {children}
    </BackgroundTaskContext.Provider>
  );
};

export const useBackgroundTask = () => {
  const context = useContext(BackgroundTaskContext);
  if (!context) {
    throw new Error('useBackgroundTask must be used within a BackgroundTaskProvider');
  }
  return context;
};