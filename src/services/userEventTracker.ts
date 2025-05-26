import { performanceCollector } from './performanceMetricsCollector';

interface UserEvent {
  type: string;
  timestamp: number;
  duration?: number;
  metadata?: Record<string, any>;
  performanceSnapshot?: {
    memoryUsage: number;
    renderTime: number;
    networkLatency: number;
  };
}

class UserEventTracker {
  private static instance: UserEventTracker;
  private events: UserEvent[] = [];
  private readonly MAX_EVENTS = 1000;
  private startTimes: Map<string, number> = new Map();

  private constructor() {}

  static getInstance(): UserEventTracker {
    if (!UserEventTracker.instance) {
      UserEventTracker.instance = new UserEventTracker();
    }
    return UserEventTracker.instance;
  }

  trackEvent(type: string, metadata?: Record<string, any>) {
    const event: UserEvent = {
      type,
      timestamp: Date.now(),
      metadata,
      performanceSnapshot: {
        memoryUsage: performance.memory?.usedJSHeapSize || 0,
        renderTime: performanceCollector.getAverages(60000).avgRenderTime,
        networkLatency: performanceCollector.getAverages(60000).avgNetworkLatency
      }
    };

    this.events.push(event);
    if (this.events.length > this.MAX_EVENTS) {
      this.events.shift();
    }
  }

  startTracking(eventType: string) {
    this.startTimes.set(eventType, performance.now());
  }

  endTracking(eventType: string, metadata?: Record<string, any>) {
    const startTime = this.startTimes.get(eventType);
    if (startTime) {
      const duration = performance.now() - startTime;
      this.trackEvent(eventType, { ...metadata, duration });
      this.startTimes.delete(eventType);
    }
  }

  getEvents(timeRange?: number): UserEvent[] {
    if (!timeRange) return [...this.events];
    const cutoff = Date.now() - timeRange;
    return this.events.filter(event => event.timestamp >= cutoff);
  }

  getEventAnalytics(timeRange?: number) {
    const events = this.getEvents(timeRange);
    const analytics = {
      eventCounts: {} as Record<string, number>,
      averageDurations: {} as Record<string, number>,
      impactfulEvents: [] as { type: string; avgMemoryDelta: number; avgRenderTimeDelta: number }[]
    };

    // Calculate event counts and average durations
    events.forEach(event => {
      analytics.eventCounts[event.type] = (analytics.eventCounts[event.type] || 0) + 1;
      if (event.duration) {
        analytics.averageDurations[event.type] = analytics.averageDurations[event.type] || 0;
        analytics.averageDurations[event.type] += event.duration;
      }
    });

    // Calculate averages for durations
    Object.keys(analytics.averageDurations).forEach(type => {
      analytics.averageDurations[type] /= analytics.eventCounts[type];
    });

    // Analyze performance impact
    const eventTypes = new Set(events.map(e => e.type));
    eventTypes.forEach(type => {
      const typeEvents = events.filter(e => e.type === type);
      if (typeEvents.length < 2) return;

      const memoryDeltas = [];
      const renderTimeDeltas = [];

      for (let i = 1; i < typeEvents.length; i++) {
        const prev = typeEvents[i - 1].performanceSnapshot!;
        const curr = typeEvents[i].performanceSnapshot!;
        
        memoryDeltas.push(curr.memoryUsage - prev.memoryUsage);
        renderTimeDeltas.push(curr.renderTime - prev.renderTime);
      }

      const avgMemoryDelta = memoryDeltas.reduce((sum, delta) => sum + delta, 0) / memoryDeltas.length;
      const avgRenderTimeDelta = renderTimeDeltas.reduce((sum, delta) => sum + delta, 0) / renderTimeDeltas.length;

      if (Math.abs(avgMemoryDelta) > 1024 * 1024 || Math.abs(avgRenderTimeDelta) > 16) {
        analytics.impactfulEvents.push({
          type,
          avgMemoryDelta,
          avgRenderTimeDelta
        });
      }
    });

    return analytics;
  }

  clear() {
    this.events = [];
    this.startTimes.clear();
  }
}

export const userEventTracker = UserEventTracker.getInstance();

// React hook for components to track events
export function useEventTracking() {
  return {
    trackEvent: (type: string, metadata?: Record<string, any>) => 
      userEventTracker.trackEvent(type, metadata),
    startTracking: (eventType: string) => 
      userEventTracker.startTracking(eventType),
    endTracking: (eventType: string, metadata?: Record<string, any>) => 
      userEventTracker.endTracking(eventType, metadata),
    getEvents: (timeRange?: number) => 
      userEventTracker.getEvents(timeRange),
    getEventAnalytics: (timeRange?: number) => 
      userEventTracker.getEventAnalytics(timeRange)
  };
}