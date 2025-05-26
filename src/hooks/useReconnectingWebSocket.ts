import { useEffect, useRef, useState, useCallback } from 'react';
import { useNotification } from '../contexts/NotificationContext';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: any) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
  initialRetryDelayMs?: number;
  maxRetryDelayMs?: number;
  maxRetries?: number;
}

export function useReconnectingWebSocket({
  url,
  onMessage,
  onConnected,
  onDisconnected,
  initialRetryDelayMs = 1000,
  maxRetryDelayMs = 30000,
  maxRetries = 5
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const { addNotification } = useNotification();

  const connect = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        onConnected?.();
        addNotification('success', 'WebSocket connected');
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        onDisconnected?.();

        if (reconnectAttempts.current < maxRetries) {
          const delay = Math.min(
            initialRetryDelayMs * Math.pow(2, reconnectAttempts.current),
            maxRetryDelayMs
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);

          addNotification('warning', `Connection lost. Retrying in ${Math.round(delay / 1000)}s...`);
        } else {
          setError(new Error('Maximum reconnection attempts reached'));
          addNotification('error', 'Failed to establish connection after multiple attempts');
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      wsRef.current.onerror = (event) => {
        const error = new Error('WebSocket error occurred');
        setError(error);
        addNotification('error', 'Connection error occurred');
      };
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to create WebSocket connection'));
      addNotification('error', 'Failed to create WebSocket connection');
    }
  }, [url, onMessage, onConnected, onDisconnected, initialRetryDelayMs, maxRetryDelayMs, maxRetries, addNotification]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttempts.current = 0;
  }, []);

  const send = useCallback((data: any) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    try {
      wsRef.current.send(JSON.stringify(data));
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to send message');
      setError(error);
      addNotification('error', 'Failed to send message');
      throw error;
    }
  }, [addNotification]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    error,
    send,
    disconnect,
    reconnect: connect,
    reconnectAttempts: reconnectAttempts.current
  };
}