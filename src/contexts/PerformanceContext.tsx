import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useNotification } from './NotificationContext';

interface PerformanceMetric {
  componentName: string;
  renderTime: number;
  timestamp: number;
  type: 'render' | 'fetch' | 'computation';
}

interface PerformanceStats {
  avgRenderTime: number;
  slowestComponent: string;
  totalRenders: number;
  lastUpdate: number;
}

interface PerformanceContextType {
  recordMetric: (metric: Omit<PerformanceMetric, 'timestamp'>) => void;
  getStats: () => PerformanceStats;
  clearMetrics: () => void;
  isPerformanceIssue: (componentName: string) => boolean;
}

const PerformanceContext = createContext<PerformanceContextType | null>(null);

const PERFORMANCE_THRESHOLD = 16; // 60fps threshold in ms
const METRICS_RETENTION_PERIOD = 5 * 60 * 1000; // 5 minutes

export const PerformanceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const { addNotification } = useNotification();

  // Clean up old metrics periodically
  useEffect(() => {
    const cleanup = () => {
      const cutoff = Date.now() - METRICS_RETENTION_PERIOD;
      setMetrics(prev => prev.filter(metric => metric.timestamp > cutoff));
    };

    const interval = setInterval(cleanup, 60000); // Clean up every minute
    return () => clearInterval(interval);
  }, []);

  const recordMetric = useCallback(({ componentName, renderTime, type }: Omit<PerformanceMetric, 'timestamp'>) => {
    const metric: PerformanceMetric = {
      componentName,
      renderTime,
      type,
      timestamp: Date.now()
    };

    setMetrics(prev => [...prev, metric]);

    if (renderTime > PERFORMANCE_THRESHOLD) {
      addNotification('warning', `Performance issue detected in ${componentName}`);
      console.warn(`Slow ${type} detected in ${componentName}: ${renderTime}ms`);
    }
  }, [addNotification]);

  const getStats = useCallback((): PerformanceStats => {
    if (metrics.length === 0) {
      return {
        avgRenderTime: 0,
        slowestComponent: '',
        totalRenders: 0,
        lastUpdate: Date.now()
      };
    }

    const recentMetrics = metrics.filter(m => 
      m.timestamp > Date.now() - METRICS_RETENTION_PERIOD
    );

    const totalTime = recentMetrics.reduce((sum, m) => sum + m.renderTime, 0);
    const slowest = recentMetrics.reduce((prev, curr) => 
      prev.renderTime > curr.renderTime ? prev : curr
    );

    return {
      avgRenderTime: totalTime / recentMetrics.length,
      slowestComponent: slowest.componentName,
      totalRenders: recentMetrics.length,
      lastUpdate: Date.now()
    };
  }, [metrics]);

  const clearMetrics = useCallback(() => {
    setMetrics([]);
  }, []);

  const isPerformanceIssue = useCallback((componentName: string): boolean => {
    const recentMetrics = metrics.filter(m => 
      m.componentName === componentName &&
      m.timestamp > Date.now() - 60000 // Last minute
    );

    if (recentMetrics.length === 0) return false;

    const avgTime = recentMetrics.reduce((sum, m) => sum + m.renderTime, 0) / recentMetrics.length;
    return avgTime > PERFORMANCE_THRESHOLD;
  }, [metrics]);

  return (
    <PerformanceContext.Provider value={{
      recordMetric,
      getStats,
      clearMetrics,
      isPerformanceIssue
    }}>
      {children}
    </PerformanceContext.Provider>
  );
};

export const usePerformance = () => {
  const context = useContext(PerformanceContext);
  if (!context) {
    throw new Error('usePerformance must be used within a PerformanceProvider');
  }
  return context;
};

// HOC to automatically track component performance
export const withPerformanceTracking = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName: string
) => {
  return function PerformanceTrackedComponent(props: P) {
    const { recordMetric } = usePerformance();
    const startTime = Date.now();

    useEffect(() => {
      const renderTime = Date.now() - startTime;
      recordMetric({
        componentName,
        renderTime,
        type: 'render'
      });
    });

    return <WrappedComponent {...props} />;
  };
};