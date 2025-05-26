import { useEffect, useRef, useCallback } from 'react';
import { useNotification } from '../contexts/NotificationContext';

type WorkerMessage = {
  type: string;
  data?: any;
  error?: string;
};

type WorkerTask = {
  type: string;
  data: any;
  resolve: (value: any) => void;
  reject: (reason: any) => void;
};

export function useTradingWorker() {
  const workerRef = useRef<Worker | null>(null);
  const taskQueueRef = useRef<WorkerTask[]>([]);
  const { addNotification } = useNotification();

  useEffect(() => {
    workerRef.current = new Worker(
      new URL('../workers/trading.worker.ts', import.meta.url),
      { type: 'module' }
    );

    workerRef.current.onmessage = (event: MessageEvent<WorkerMessage>) => {
      const currentTask = taskQueueRef.current[0];
      if (!currentTask) return;

      if (event.data.error) {
        currentTask.reject(new Error(event.data.error));
        addNotification('error', `Calculation error: ${event.data.error}`);
      } else if (event.data.type.includes('complete')) {
        currentTask.resolve(event.data.data);
      }

      // Remove completed task and process next
      taskQueueRef.current.shift();
      processNextTask();
    };

    workerRef.current.onerror = (error) => {
      const currentTask = taskQueueRef.current[0];
      if (currentTask) {
        currentTask.reject(error);
        addNotification('error', 'Worker error occurred');
      }
      taskQueueRef.current.shift();
      processNextTask();
    };

    return () => {
      workerRef.current?.terminate();
    };
  }, [addNotification]);

  const processNextTask = useCallback(() => {
    if (taskQueueRef.current.length === 0) return;
    
    const nextTask = taskQueueRef.current[0];
    workerRef.current?.postMessage({
      type: nextTask.type,
      data: nextTask.data
    });
  }, []);

  const executeTask = useCallback(<T>(type: string, data: any): Promise<T> => {
    return new Promise((resolve, reject) => {
      const task: WorkerTask = { type, data, resolve, reject };
      const isFirstTask = taskQueueRef.current.length === 0;
      
      taskQueueRef.current.push(task);
      
      if (isFirstTask) {
        processNextTask();
      }
    });
  }, [processNextTask]);

  const analyzeMarketData = useCallback((data: any) => {
    return executeTask('analyze_market_data', data);
  }, [executeTask]);

  const calculateArbitrage = useCallback((data: any) => {
    return executeTask('calculate_arbitrage', data);
  }, [executeTask]);

  const assessRisk = useCallback((data: any) => {
    return executeTask('risk_assessment', data);
  }, [executeTask]);

  return {
    analyzeMarketData,
    calculateArbitrage,
    assessRisk
  };
}