import React from 'react';
import { useWebSocket } from '../hooks/useReconnectingWebSocket';
import { usePerformance } from '../contexts/PerformanceContext';
import { useWeb3 } from '../contexts/Web3Context';

const StatusBar: React.FC = () => {
  const { isConnected: wsConnected } = useWebSocket(
    `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:3001/ws/price-feed`,
    { onMessage: () => {} }
  );
  const { getStats } = usePerformance();
  const { account } = useWeb3();
  const stats = getStats();

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 p-2">
      <div className="container mx-auto flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          {/* WebSocket Status */}
          <div className="flex items-center space-x-2">
            <span className={`w-2 h-2 rounded-full ${
              wsConnected ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-gray-400">WebSocket</span>
          </div>

          {/* Web3 Status */}
          <div className="flex items-center space-x-2">
            <span className={`w-2 h-2 rounded-full ${
              account ? 'bg-green-500' : 'bg-yellow-500'
            }`} />
            <span className="text-gray-400">
              {account ? 'Connected' : 'Not Connected'}
            </span>
          </div>

          {/* Performance */}
          <div className="flex items-center space-x-2">
            <span className={`w-2 h-2 rounded-full ${
              stats.avgRenderTime > 16 ? 'bg-red-500' : 'bg-green-500'
            }`} />
            <span className="text-gray-400">
              {stats.avgRenderTime.toFixed(1)}ms
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Total Renders */}
          <div className="text-gray-400">
            Renders: {stats.totalRenders}
          </div>

          {/* Memory Usage */}
          <div className="text-gray-400">
            Memory: {Math.round(performance.memory?.usedJSHeapSize / 1048576)}MB
          </div>

          {/* Network Status */}
          <div className="flex items-center space-x-2">
            <span className={`w-2 h-2 rounded-full ${
              navigator.onLine ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-gray-400">
              {navigator.onLine ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusBar;