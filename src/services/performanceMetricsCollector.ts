import { errorTracker } from './errorTracking';

interface PerformanceMetrics {
  timestamp: number;
  renderTime: number;
  networkLatency: number;
  memoryUsage: number;
  errorCount: number;
  resourceCount: number;
  resourceSize: number;
}

class PerformanceMetricsCollector {
  private static instance: PerformanceMetricsCollector;
  private metrics: PerformanceMetrics[] = [];
  private interval: NodeJS.Timeout | null = null;
  private readonly MAX_ENTRIES = 1000;

  private constructor() {
    this.startCollecting();
  }

  static getInstance(): PerformanceMetricsCollector {
    if (!PerformanceMetricsCollector.instance) {
      PerformanceMetricsCollector.instance = new PerformanceMetricsCollector();
    }
    return PerformanceMetricsCollector.instance;
  }

  private startCollecting() {
    this.interval = setInterval(() => {
      const now = Date.now();
      
      // Collect performance metrics
      const perfEntries = performance.getEntriesByType('measure');
      const renderTimes = perfEntries
        .filter(entry => entry.name.startsWith('render_'))
        .map(entry => entry.duration);
      
      const avgRenderTime = renderTimes.length > 0
        ? renderTimes.reduce((sum, time) => sum + time, 0) / renderTimes.length
        : 0;

      // Collect network metrics
      const networkEntries = performance.getEntriesByType('resource');
      const networkLatencies = networkEntries.map(entry => entry.duration);
      const avgNetworkLatency = networkLatencies.length > 0
        ? networkLatencies.reduce((sum, time) => sum + time, 0) / networkLatencies.length
        : 0;

      // Collect memory usage
      const memoryUsage = performance.memory?.usedJSHeapSize || 0;

      // Get error count from error tracker
      const errorStats = errorTracker.getErrorStats();
      const recentErrorCount = errorStats.recentCount;

      // Resource metrics
      const resourceStats = {
        count: networkEntries.length,
        size: networkEntries.reduce((sum, entry) => sum + (entry as any).transferSize, 0)
      };

      const metrics: PerformanceMetrics = {
        timestamp: now,
        renderTime: avgRenderTime,
        networkLatency: avgNetworkLatency,
        memoryUsage,
        errorCount: recentErrorCount,
        resourceCount: resourceStats.count,
        resourceSize: resourceStats.size
      };

      this.addMetrics(metrics);
    }, 60000); // Collect metrics every minute
  }

  private addMetrics(metrics: PerformanceMetrics) {
    this.metrics.push(metrics);
    if (this.metrics.length > this.MAX_ENTRIES) {
      this.metrics.shift();
    }
  }

  getMetrics(timeRange: number = 3600000): PerformanceMetrics[] {
    const cutoff = Date.now() - timeRange;
    return this.metrics.filter(metric => metric.timestamp >= cutoff);
  }

  getAverages(timeRange: number = 3600000): {
    avgRenderTime: number;
    avgNetworkLatency: number;
    avgMemoryUsage: number;
    avgErrorRate: number;
  } {
    const metrics = this.getMetrics(timeRange);
    if (metrics.length === 0) {
      return {
        avgRenderTime: 0,
        avgNetworkLatency: 0,
        avgMemoryUsage: 0,
        avgErrorRate: 0
      };
    }

    return {
      avgRenderTime: metrics.reduce((sum, m) => sum + m.renderTime, 0) / metrics.length,
      avgNetworkLatency: metrics.reduce((sum, m) => sum + m.networkLatency, 0) / metrics.length,
      avgMemoryUsage: metrics.reduce((sum, m) => sum + m.memoryUsage, 0) / metrics.length,
      avgErrorRate: metrics.reduce((sum, m) => sum + m.errorCount, 0) / metrics.length
    };
  }

  getTrends(timeRange: number = 3600000): {
    renderTimeTrend: number;
    networkLatencyTrend: number;
    memoryUsageTrend: number;
    errorCountTrend: number;
  } {
    const metrics = this.getMetrics(timeRange);
    if (metrics.length < 2) {
      return {
        renderTimeTrend: 0,
        networkLatencyTrend: 0,
        memoryUsageTrend: 0,
        errorCountTrend: 0
      };
    }

    const calculateTrend = (values: number[]): number => {
      const first = values[0];
      const last = values[values.length - 1];
      return ((last - first) / first) * 100;
    };

    return {
      renderTimeTrend: calculateTrend(metrics.map(m => m.renderTime)),
      networkLatencyTrend: calculateTrend(metrics.map(m => m.networkLatency)),
      memoryUsageTrend: calculateTrend(metrics.map(m => m.memoryUsage)),
      errorCountTrend: calculateTrend(metrics.map(m => m.errorCount))
    };
  }

  destroy() {
    if (this.interval) {
      clearInterval(this.interval);
    }
  }
}

export const performanceCollector = PerformanceMetricsCollector.getInstance();

// Hook for components to access performance metrics
export function usePerformanceMetrics(timeRange?: number) {
  return {
    metrics: performanceCollector.getMetrics(timeRange),
    averages: performanceCollector.getAverages(timeRange),
    trends: performanceCollector.getTrends(timeRange)
  };
}