import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebSocketOptions {
  url: string;
  autoConnect?: boolean;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Error) => void;
  onMessage?: (data: any) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

/**
 * Custom hook for WebSocket connections that ensures:
 * - Proper relative URL handling
 * - Automatic reconnection
 * - JSON message parsing
 */
export const useWebSocket = (
  urlOrOptions: string | UseWebSocketOptions,
  optionsObj?: Partial<UseWebSocketOptions>
) => {
  // Handle both function signatures:
  // 1. useWebSocket(url, options)
  // 2. useWebSocket(options)
  const options = typeof urlOrOptions === 'string' 
    ? { url: urlOrOptions, ...optionsObj } 
    : urlOrOptions;
    
  const {
    url,
    autoConnect = true,
    onOpen,
    onClose,
    onError,
    onMessage,
    onConnected,
    onDisconnected,
    reconnectInterval = 5000,
    maxReconnectAttempts = 3, // Reduced from 5 to prevent excessive reconnects
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [manualClose, setManualClose] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  
  const connect = useCallback(() => {
    // Reset error state on new connection attempt
    setError(null);
    
    // Close any existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    try {
      // Fix: Ensure we're using the same host and port for WebSocket connections
      // This is the critical fix - we must NOT add the port (3000) to the URL
      let wsUrl = '';
      
      if (url.startsWith('/')) {
        // Use current protocol (ws/wss) and host
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        
        // Get just the hostname without any port number for Replit
        const hostWithoutPort = window.location.host.split(':')[0];
        
        // Use the Replit URL format without additional port
        wsUrl = `${protocol}//${hostWithoutPort}${url}`;
      } else if (url.match(/^wss?:\/\//)) {
        // If it's already a full WebSocket URL, use it directly
        wsUrl = url;
      } else {
        // Default to adding it to the current host with proper protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        
        // Get just the hostname without any port number for Replit
        const hostWithoutPort = window.location.host.split(':')[0];
        
        // Use the Replit URL format without additional port
        wsUrl = `${protocol}//${hostWithoutPort}/${url}`;
      }
      
      console.log('Connecting to WebSocket at:', wsUrl);
      
      // Create new WebSocket connection
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      setManualClose(false);
      
      // Connection opened
      ws.onopen = () => {
        console.log('WebSocket connection established to', wsUrl);
        setIsConnected(true);
        setReconnectAttempts(0);
        if (onOpen) onOpen();
        if (onConnected) onConnected();
      };
      
      // Listen for messages
      ws.onmessage = (event) => {
        try {
          const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
          setLastMessage(data);
          if (onMessage) onMessage(data);
        } catch (error) {
          console.log('Received non-JSON message:', event.data);
          // If it's not JSON, just set the raw data
          setLastMessage(event.data);
          if (onMessage) onMessage(event.data);
        }
      };
      
      // Listen for connection close
      ws.onclose = (event) => {
        console.log(`WebSocket connection closed with code ${event.code}:`, event.reason);
        setIsConnected(false);
        if (onClose) onClose();
        if (onDisconnected) onDisconnected();
        
        // Clear reference to closed connection
        wsRef.current = null;
        
        // Attempt to reconnect if it wasn't manually closed and we haven't exceeded max attempts
        if (!manualClose && reconnectAttempts < maxReconnectAttempts) {
          // Increment attempts for display purposes but don't affect state yet
          // This helps prevent rapid reconnection loops
          const nextAttempt = reconnectAttempts + 1;
          console.log(`Attempting to reconnect (${nextAttempt}/${maxReconnectAttempts})...`);
          
          // Increase delay with each attempt (exponential backoff)
          const delay = reconnectInterval * Math.pow(1.5, reconnectAttempts);
          
          setTimeout(() => {
            // Only increment if still mounted
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, delay);
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          console.log('Maximum reconnection attempts reached. WebSocket connection failed.');
        }
      };
      
      // Listen for connection error
      ws.onerror = (event) => {
        const wsError = new Error(`WebSocket error connecting to ${wsUrl}`);
        console.error('WebSocket error:', event);
        setError(wsError);
        if (onError) onError(wsError);
      };
    } catch (error) {
      const connectionError = error instanceof Error 
        ? error 
        : new Error('Failed to create WebSocket connection');
      console.error('Connection error:', connectionError);
      setError(connectionError);
      if (onError) onError(connectionError);
    }
  }, [url, manualClose, reconnectAttempts, maxReconnectAttempts, reconnectInterval, onOpen, onClose, onError, onMessage, onConnected, onDisconnected]);
  
  // Handle reconnection
  const reconnect = useCallback(() => {
    setReconnectAttempts(0);
    connect();
  }, [connect]);
  
  // Establish connection on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        setManualClose(true);
        wsRef.current.close();
      }
    };
  }, [connect, autoConnect]);
  
  // Disconnect function
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      setManualClose(true);
      wsRef.current.close();
    }
  }, []);
  
  // Send message function
  const send = useCallback((message: string | object) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const formattedMessage = typeof message === 'string' ? message : JSON.stringify(message);
      wsRef.current.send(formattedMessage);
      return true;
    }
    console.warn('Cannot send message: WebSocket not open', wsRef.current?.readyState);
    return false;
  }, []);
  
  // Subscribe to topics
  const subscribe = useCallback((subscriptionData: { topics?: string[], networks?: string[] }) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('Cannot subscribe: WebSocket not connected');
      return false;
    }
    
    const subscribeMessage = {
      type: 'subscribe',
      data: subscriptionData
    };
    
    return send(subscribeMessage);
  }, [send]);
  
  return {
    isConnected,
    lastMessage,
    error,
    send,
    subscribe,
    connect,
    reconnect,
    disconnect,
    reconnectAttempts
  };
};