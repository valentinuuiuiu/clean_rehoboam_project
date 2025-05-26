import { usePerformance } from '../contexts/PerformanceContext';

interface RequestMetrics {
  url: string;
  method: string;
  duration: number;
  status: number;
  timestamp: number;
}

class NetworkTracker {
  private static instance: NetworkTracker;
  private metrics: RequestMetrics[] = [];
  private listeners = new Set<(metrics: RequestMetrics[]) => void>();

  private constructor() {
    this.setupXHRInterceptor();
    this.setupFetchInterceptor();
  }

  static getInstance(): NetworkTracker {
    if (!NetworkTracker.instance) {
      NetworkTracker.instance = new NetworkTracker();
    }
    return NetworkTracker.instance;
  }

  private setupXHRInterceptor() {
    const XHR = XMLHttpRequest.prototype;
    const open = XHR.open;
    const send = XHR.send;
    const metrics = this.metrics;
    const notifyListeners = () => this.notifyListeners();

    XHR.open = function(method: string, url: string) {
      (this as any)._networkMetrics = {
        method,
        url,
        startTime: Date.now()
      };
      return open.apply(this, arguments as any);
    };

    XHR.send = function() {
      this.addEventListener('loadend', function() {
        const duration = Date.now() - (this as any)._networkMetrics.startTime;
        metrics.push({
          ...(this as any)._networkMetrics,
          duration,
          status: this.status,
          timestamp: Date.now()
        });
        
        // Keep only last 100 requests
        if (metrics.length > 100) {
          metrics.shift();
        }
        
        notifyListeners();
      });
      return send.apply(this, arguments as any);
    };
  }

  private setupFetchInterceptor() {
    const originalFetch = window.fetch;
    const metrics = this.metrics;
    const notifyListeners = () => this.notifyListeners();

    window.fetch = async function(input: RequestInfo | URL, init?: RequestInit) {
      const startTime = Date.now();
      const url = typeof input === 'string' ? input : input.url;
      const method = init?.method || 'GET';

      try {
        const response = await originalFetch(input, init);
        const duration = Date.now() - startTime;
        
        metrics.push({
          url,
          method,
          duration,
          status: response.status,
          timestamp: Date.now()
        });

        if (metrics.length > 100) {
          metrics.shift();
        }

        notifyListeners();
        return response;
      } catch (error) {
        const duration = Date.now() - startTime;
        metrics.push({
          url,
          method,
          duration,
          status: 0,
          timestamp: Date.now()
        });

        if (metrics.length > 100) {
          metrics.shift();
        }

        notifyListeners();
        throw error;
      }
    };
  }

  subscribe(listener: (metrics: RequestMetrics[]) => void) {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.getMetrics()));
  }

  getMetrics(): RequestMetrics[] {
    return [...this.metrics];
  }

  getAverageResponseTime(): number {
    if (this.metrics.length === 0) return 0;
    const sum = this.metrics.reduce((acc, metric) => acc + metric.duration, 0);
    return sum / this.metrics.length;
  }

  getErrorRate(): number {
    if (this.metrics.length === 0) return 0;
    const errorCount = this.metrics.filter(m => m.status >= 400 || m.status === 0).length;
    return (errorCount / this.metrics.length) * 100;
  }
}

export const useNetworkTracker = () => {
  const tracker = NetworkTracker.getInstance();
  const { recordMetric } = usePerformance();

  const trackRequest = (metric: RequestMetrics) => {
    recordMetric({
      componentName: 'Network',
      renderTime: metric.duration,
      type: 'fetch'
    });
  };

  return {
    getMetrics: () => tracker.getMetrics(),
    getAverageResponseTime: () => tracker.getAverageResponseTime(),
    getErrorRate: () => tracker.getErrorRate(),
    subscribe: tracker.subscribe.bind(tracker),
    trackRequest
  };
};