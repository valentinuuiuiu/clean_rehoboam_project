import { useEffect, useState } from 'react';
import { usePerformance } from '../contexts/PerformanceContext';

interface ResourceTiming {
  name: string;
  initiatorType: string;
  duration: number;
  transferSize: number;
  timestamp: number;
}

interface ResourceStats {
  totalSize: number;
  totalDuration: number;
  resourceCounts: Record<string, number>;
  slowestResources: ResourceTiming[];
  largestResources: ResourceTiming[];
}

export function useResourceMonitor() {
  const [stats, setStats] = useState<ResourceStats>({
    totalSize: 0,
    totalDuration: 0,
    resourceCounts: {},
    slowestResources: [],
    largestResources: []
  });

  const { recordMetric } = usePerformance();

  useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries() as PerformanceResourceTiming[];
      
      const resourceTimings: ResourceTiming[] = entries.map(entry => ({
        name: entry.name,
        initiatorType: entry.initiatorType,
        duration: entry.duration,
        transferSize: entry.transferSize,
        timestamp: Date.now()
      }));

      // Record performance metrics
      resourceTimings.forEach(resource => {
        recordMetric({
          componentName: `Resource-${resource.initiatorType}`,
          renderTime: resource.duration,
          type: 'computation'
        });
      });

      // Calculate statistics
      const totalSize = resourceTimings.reduce((sum, r) => sum + r.transferSize, 0);
      const totalDuration = resourceTimings.reduce((sum, r) => sum + r.duration, 0);
      
      const resourceCounts = resourceTimings.reduce((counts, r) => {
        counts[r.initiatorType] = (counts[r.initiatorType] || 0) + 1;
        return counts;
      }, {} as Record<string, number>);

      const slowestResources = [...resourceTimings]
        .sort((a, b) => b.duration - a.duration)
        .slice(0, 5);

      const largestResources = [...resourceTimings]
        .sort((a, b) => b.transferSize - a.transferSize)
        .slice(0, 5);

      setStats({
        totalSize,
        totalDuration,
        resourceCounts,
        slowestResources,
        largestResources
      });
    });

    observer.observe({ 
      entryTypes: ['resource'],
      buffered: true
    });

    return () => observer.disconnect();
  }, [recordMetric]);

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return {
    stats,
    formatSize,
    formatDuration
  };
}