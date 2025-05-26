import React from 'react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import { useResourceMonitor } from '../hooks/useResourceMonitor';
import { useNetworkTracker } from '../utils/networkTracker';
import WebSocketMonitor from './WebSocketMonitor';
import { usePerformance } from '../contexts/PerformanceContext';

const SystemMonitor: React.FC = () => {
  const { stats: resourceStats, formatSize, formatDuration } = useResourceMonitor();
  const { getMetrics, getAverageResponseTime, getErrorRate } = useNetworkTracker();
  const { getStats } = usePerformance();
  const perfStats = getStats();

  return (
    <div className="space-y-6">
      {/* Overall System Health */}
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-500">Memory Usage</p>
            <div className="mt-1">
              <Progress 
                value={(performance.memory?.usedJSHeapSize || 0) / (performance.memory?.jsHeapSizeLimit || 1) * 100} 
                className={`${
                  (performance.memory?.usedJSHeapSize || 0) / (performance.memory?.jsHeapSizeLimit || 1) > 0.8 
                    ? 'bg-red-200' 
                    : 'bg-green-200'
                }`}
              />
              <p className="text-sm mt-1">{formatSize(performance.memory?.usedJSHeapSize || 0)}</p>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-500">Average Response Time</p>
            <div className="mt-1">
              <Progress 
                value={Math.min(getAverageResponseTime() / 1000 * 100, 100)}
                className={`${
                  getAverageResponseTime() > 1000 ? 'bg-red-200' : 'bg-green-200'
                }`}
              />
              <p className="text-sm mt-1">{formatDuration(getAverageResponseTime())}</p>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-500">Error Rate</p>
            <div className="mt-1">
              <Progress 
                value={getErrorRate()}
                className={`${
                  getErrorRate() > 5 ? 'bg-red-200' : 'bg-green-200'
                }`}
              />
              <p className="text-sm mt-1">{getErrorRate().toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Resource Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-4">Resource Usage</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-sm text-gray-500 mb-2">Slowest Resources</h4>
              <div className="space-y-2">
                {resourceStats.slowestResources.map((resource, index) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <span className="truncate flex-1 mr-4">{resource.name.split('/').pop()}</span>
                    <span className={`${
                      resource.duration > 1000 ? 'text-red-500' : 'text-green-500'
                    }`}>
                      {formatDuration(resource.duration)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-sm text-gray-500 mb-2">Largest Resources</h4>
              <div className="space-y-2">
                {resourceStats.largestResources.map((resource, index) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <span className="truncate flex-1 mr-4">{resource.name.split('/').pop()}</span>
                    <span className={`${
                      resource.transferSize > 1024 * 1024 ? 'text-yellow-500' : 'text-green-500'
                    }`}>
                      {formatSize(resource.transferSize)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-4">Network Activity</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-sm text-gray-500 mb-2">Recent Requests</h4>
              <div className="space-y-2">
                {getMetrics().slice(-5).map((metric, index) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <div className="flex items-center space-x-2 flex-1 mr-4">
                      <span className={`w-2 h-2 rounded-full ${
                        metric.status < 400 ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                      <span className="truncate">{metric.url.split('/').pop()}</span>
                    </div>
                    <span>{formatDuration(metric.duration)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Request Types</p>
                <div className="space-y-1 mt-2">
                  {Object.entries(resourceStats.resourceCounts).map(([type, count]) => (
                    <div key={type} className="flex justify-between text-sm">
                      <span>{type}</span>
                      <span>{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500">Performance</p>
                <div className="space-y-1 mt-2">
                  <div className="flex justify-between text-sm">
                    <span>Avg Render Time</span>
                    <span>{perfStats.avgRenderTime.toFixed(1)}ms</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Total Renders</span>
                    <span>{perfStats.totalRenders}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* WebSocket Status */}
      <WebSocketMonitor />
    </div>
  );
};

export default SystemMonitor;