import { useState, useCallback } from 'react';

interface ErrorRecord {
  id: string;
  timestamp: number;
  error: Error;
  componentName: string;
  context: Record<string, any>;
}

class ErrorTrackingService {
  private static instance: ErrorTrackingService;
  private errors: ErrorRecord[] = [];
  private listeners: Set<(errors: ErrorRecord[]) => void> = new Set();

  private constructor() {}

  static getInstance(): ErrorTrackingService {
    if (!ErrorTrackingService.instance) {
      ErrorTrackingService.instance = new ErrorTrackingService();
    }
    return ErrorTrackingService.instance;
  }

  trackError(error: Error, componentName: string, context: Record<string, any> = {}) {
    const errorRecord: ErrorRecord = {
      id: Math.random().toString(36).substring(2),
      timestamp: Date.now(),
      error,
      componentName,
      context
    };

    this.errors.push(errorRecord);
    // Keep last 100 errors
    if (this.errors.length > 100) {
      this.errors.shift();
    }

    this.notifyListeners();

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.group('Error Tracked:');
      console.error(error);
      console.log('Component:', componentName);
      console.log('Context:', context);
      console.groupEnd();
    }
  }

  getErrors(): ErrorRecord[] {
    return [...this.errors];
  }

  subscribe(listener: (errors: ErrorRecord[]) => void) {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.getErrors()));
  }

  getErrorStats() {
    const stats = {
      total: this.errors.length,
      byComponent: {} as Record<string, number>,
      byType: {} as Record<string, number>,
      recentCount: 0, // last 5 minutes
    };

    const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;

    this.errors.forEach(error => {
      // Count by component
      stats.byComponent[error.componentName] = (stats.byComponent[error.componentName] || 0) + 1;

      // Count by error type
      const errorType = error.error.name || 'Unknown';
      stats.byType[errorType] = (stats.byType[errorType] || 0) + 1;

      // Count recent errors
      if (error.timestamp > fiveMinutesAgo) {
        stats.recentCount++;
      }
    });

    return stats;
  }
}

export const useErrorTracking = () => {
  const [errors, setErrors] = useState<ErrorRecord[]>([]);
  const errorService = ErrorTrackingService.getInstance();

  const trackError = useCallback((error: Error, componentName: string, context: Record<string, any> = {}) => {
    errorService.trackError(error, componentName, context);
  }, []);

  const getErrorStats = useCallback(() => {
    return errorService.getErrorStats();
  }, []);

  useState(() => {
    const unsubscribe = errorService.subscribe(setErrors);
    return unsubscribe;
  });

  return {
    errors,
    trackError,
    getErrorStats
  };
};

export const errorTracker = ErrorTrackingService.getInstance();