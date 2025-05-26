import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface WithWebSocketProps {
  wsUrl: string;
  channels?: string[];
}

interface SubscriptionData {
  channels: string[];
}

export function withWebSocket<T, P extends object>(
  WrappedComponent: React.ComponentType<P & { wsData?: T; wsError?: Error | null; wsConnected: boolean }>,
  options: WithWebSocketProps
) {
  return function WithWebSocketComponent(props: P) {
    const {
      isConnected,
      error,
      send,
      disconnect,
      reconnect
    } = useWebSocket<T>(options.wsUrl, {
      onConnected: () => {
        if (options.channels?.length) {
          send({
            type: 'subscribe',
            data: { channels: options.channels }
          });
        }
      },
      onDisconnected: () => {
        console.log('WebSocket disconnected, attempting to reconnect...');
      }
    });

    // Cleanup subscriptions on unmount
    React.useEffect(() => {
      return () => {
        if (options.channels?.length) {
          send({
            type: 'unsubscribe',
            data: { channels: options.channels }
          });
        }
        disconnect();
      };
    }, [disconnect, send]);

    return (
      <WrappedComponent
        {...props}
        wsData={undefined} // Or maybe set initial data here
        wsConnected={isConnected}
        wsError={error as Error | undefined} // Adjusted wsError type
      />
    );
  };
}