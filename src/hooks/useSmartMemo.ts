import { useRef, useCallback, useEffect, useMemo } from 'react';
import { usePerformance } from '../contexts/PerformanceContext';

interface UseMemoOptions {
  maxAge?: number;
  componentName: string;
}

export function useSmartMemo<T>(
  factory: () => T,
  dependencies: any[],
  { maxAge = 30000, componentName }: UseMemoOptions
) {
  const cache = useRef<{ value: T; timestamp: number } | null>(null);
  const { recordMetric } = usePerformance();
  
  const getValue = useCallback(() => {
    const now = Date.now();
    const isStale = !cache.current || now - cache.current.timestamp > maxAge;
    
    if (isStale) {
      const start = performance.now();
      const newValue = factory();
      const computeTime = performance.now() - start;
      
      recordMetric({
        componentName,
        renderTime: computeTime,
        type: 'computation'
      });
      
      cache.current = {
        value: newValue,
        timestamp: now
      };
    }
    
    return cache.current.value;
  }, [factory, maxAge, componentName, recordMetric]);
  
  return useMemo(() => getValue(), dependencies);
}

interface UseRenderOptimizationOptions {
  componentName: string;
  renderThreshold?: number;
}

export function useRenderOptimization({ 
  componentName,
  renderThreshold = 16 
}: UseRenderOptimizationOptions) {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(performance.now());
  const { recordMetric } = usePerformance();
  
  useEffect(() => {
    const currentTime = performance.now();
    const renderDuration = currentTime - lastRenderTime.current;
    renderCount.current++;
    
    recordMetric({
      componentName,
      renderTime: renderDuration,
      type: 'render'
    });
    
    if (renderDuration > renderThreshold) {
      console.warn(
        `Slow render detected in ${componentName}: ${renderDuration.toFixed(2)}ms`,
        `Render count: ${renderCount.current}`
      );
    }
    
    lastRenderTime.current = currentTime;
  });
  
  return {
    renderCount: renderCount.current,
    lastRenderDuration: performance.now() - lastRenderTime.current
  };
}

interface DebouncedFunction<T extends (...args: any[]) => any> {
  (...args: Parameters<T>): void;
  cancel: () => void;
}

export function useSmartDebounce<T extends (...args: any[]) => any>(
  fn: T,
  wait: number,
  { componentName }: { componentName: string }
): DebouncedFunction<T> {
  const { recordMetric } = usePerformance();
  const timeout = useRef<NodeJS.Timeout>();
  const lastCall = useRef<number>(0);
  
  const debouncedFn = useCallback((...args: Parameters<T>) => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCall.current;
    
    if (timeout.current) {
      clearTimeout(timeout.current);
    }
    
    if (timeSinceLastCall >= wait) {
      lastCall.current = now;
      const start = performance.now();
      fn(...args);
      const duration = performance.now() - start;
      
      recordMetric({
        componentName,
        renderTime: duration,
        type: 'computation'
      });
    } else {
      timeout.current = setTimeout(() => {
        lastCall.current = Date.now();
        const start = performance.now();
        fn(...args);
        const duration = performance.now() - start;
        
        recordMetric({
          componentName,
          renderTime: duration,
          type: 'computation'
        });
      }, wait - timeSinceLastCall);
    }
  }, [fn, wait, componentName, recordMetric]) as DebouncedFunction<T>;
  
  debouncedFn.cancel = useCallback(() => {
    if (timeout.current) {
      clearTimeout(timeout.current);
    }
  }, []);
  
  useEffect(() => {
    return () => {
      if (timeout.current) {
        clearTimeout(timeout.current);
      }
    };
  }, []);
  
  return debouncedFn;
}