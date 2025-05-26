import React, { useEffect, useState } from 'react';
import { useReconnectingWebSocket } from '../hooks/useReconnectingWebSocket';
import { usePerformance } from '../contexts/PerformanceContext';
import { Card } from './ui/card';

interface WebSocketMetrics {
  latency: number;
  messageCount: number;
  reconnections: number;
  lastMessageTime: number;
}

const WebSocketMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<WebSocketMetrics>({
    latency: 0,
    messageCount: 0,
    reconnections: 0,
    lastMessageTime: Date.now()
  });

  const { recordMetric } = usePerformance();
  
  const { isConnected, error, reconnectAttempts } = useReconnectingWebSocket({
    url: `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:3001/ws/monitoring`,
    onMessage: (data) => {
      const receiveTime = Date.now();
      const latency = receiveTime - data.timestamp;
      
      setMetrics(prev => ({
        latency: (prev.latency + latency) / 2, // Running average
        messageCount: prev.messageCount + 1,
        reconnections: reconnectAttempts,
        lastMessageTime: receiveTime
      }));

      recordMetric({
        componentName: 'WebSocket',
        renderTime: latency,
        type: 'fetch'
      });
    },
    maxRetries: 5
  });

  const getLatencyColor = (latency: number) => {
    if (latency < 100) return 'text-green-500';
    if (latency < 300) return 'text-yellow-500';
    return 'text-red-500';
  };

  const timeSinceLastMessage = Date.now() - metrics.lastMessageTime;
  const isStale = timeSinceLastMessage > 10000; // 10 seconds

  return (
    <Card className="p-4">
      <h3 className="text-lg font-semibold mb-4">WebSocket Status</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-sm text-gray-500">Connection Status</p>
          <div className="flex items-center mt-1">
            <span className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            } mr-2`} />
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>

        <div>
          <p className="text-sm text-gray-500">Average Latency</p>
          <p className={`font-semibold ${getLatencyColor(metrics.latency)}`}>
            {Math.round(metrics.latency)}ms
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">Messages Received</p>
          <p className="font-semibold">{metrics.messageCount}</p>
        </div>

        <div>
          <p className="text-sm text-gray-500">Reconnections</p>
          <p className={`font-semibold ${
            metrics.reconnections > 0 ? 'text-yellow-500' : 'text-green-500'
          }`}>
            {metrics.reconnections}
          </p>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-2 bg-red-100 text-red-700 rounded">
          {error.message}
        </div>
      )}

      {isStale && (
        <div className="mt-4 p-2 bg-yellow-100 text-yellow-700 rounded">
          No messages received in the last {Math.round(timeSinceLastMessage / 1000)} seconds
        </div>
      )}
    </Card>
  );
};

export default WebSocketMonitor;