import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketConfig {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onConnected?: () => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export const useWebSocketWithRetry = (url: string, config: WebSocketConfig) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);
  const reconnectTimeout = useRef<NodeJS.Timeout>();

  const {
    onMessage,
    onError,
    onConnected,
    reconnectAttempts = 5,
    reconnectInterval = 2000
  } = config;

  const connect = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectCount.current = 0;
        onConnected?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (err) {
          console.error('WebSocket message parsing error:', err);
        }
      };

      wsRef.current.onerror = (event) => {
        setError(new Error('WebSocket connection error'));
        onError?.(event);
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        if (reconnectCount.current < reconnectAttempts) {
          reconnectCount.current += 1;
          reconnectTimeout.current = setTimeout(() => {
            connect();
          }, reconnectInterval * reconnectCount.current);
        } else {
          setError(new Error('Max reconnection attempts reached'));
        }
      };
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to create WebSocket connection'));
    }
  }, [url, onMessage, onError, onConnected, reconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      throw new Error('WebSocket is not connected');
    }
  }, []);

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
    reconnect: connect
  };
};