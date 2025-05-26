import React, { useEffect, useState } from 'react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import { usePerformance } from '../contexts/PerformanceContext';

interface MetricsSnapshot {
  timestamp: number;
  avgRenderTime: number;
  totalRenders: number;
  slowComponents: string[];
}

const PerformanceMonitor: React.FC = () => {
  const { getStats, isPerformanceIssue } = usePerformance();
  const [metricsHistory, setMetricsHistory] = useState<MetricsSnapshot[]>([]);
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      const stats = getStats();
      const snapshot: MetricsSnapshot = {
        timestamp: Date.now(),
        avgRenderTime: stats.avgRenderTime,
        totalRenders: stats.totalRenders,
        slowComponents: Object.entries(stats)
          .filter(([name]) => isPerformanceIssue(name))
          .map(([name]) => name)
      };

      setMetricsHistory(prev => {
        const newHistory = [...prev, snapshot];
        if (newHistory.length > 50) { // Keep last 50 snapshots
          newHistory.shift();
        }
        return newHistory;
      });
      
      setLastUpdate(Date.now());
    }, 1000);

    return () => clearInterval(interval);
  }, [getStats, isPerformanceIssue]);

  const stats = getStats();
  const timeSinceUpdate = Date.now() - lastUpdate;

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Performance Monitor</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold mb-2">Average Render Time</h3>
          <div className="flex items-center space-x-2">
            <Progress 
              value={Math.min(100, (stats.avgRenderTime / 16) * 100)} 
              className={stats.avgRenderTime > 16 ? 'bg-red-200' : 'bg-green-200'} 
            />
            <span>{stats.avgRenderTime.toFixed(2)}ms</span>
          </div>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Total Renders</h3>
          <p className="text-2xl font-bold">{stats.totalRenders}</p>
          <p className="text-sm text-gray-500">Last update: {Math.round(timeSinceUpdate / 1000)}s ago</p>
        </div>

        {stats.slowestComponent && (
          <div className="col-span-2">
            <h3 className="font-semibold mb-2">Performance Issues</h3>
            <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
              <p className="text-yellow-800">
                Slowest component: {stats.slowestComponent} ({stats.avgRenderTime.toFixed(2)}ms)
              </p>
            </div>
          </div>
        )}

        <div className="col-span-2">
          <h3 className="font-semibold mb-2">Recent Performance History</h3>
          <div className="h-48 relative">
            {metricsHistory.map((snapshot, index) => {
              const height = `${Math.min(100, (snapshot.avgRenderTime / 16) * 100)}%`;
              const left = `${(index / 50) * 100}%`;
              const backgroundColor = snapshot.avgRenderTime > 16 ? '#FCA5A5' : '#86EFAC';
              
              return (
                <div
                  key={snapshot.timestamp}
                  className="absolute bottom-0 w-1.5"
                  style={{
                    height,
                    left,
                    backgroundColor,
                    transform: 'translateX(-50%)'
                  }}
                  title={`${snapshot.avgRenderTime.toFixed(2)}ms at ${new Date(snapshot.timestamp).toLocaleTimeString()}`}
                />
              );
            })}
            <div className="absolute bottom-0 w-full border-t border-gray-300" />
            <div className="absolute left-0 h-full border-l border-gray-300" />
          </div>
          <div className="mt-2 flex justify-between text-sm text-gray-500">
            <span>50s ago</span>
            <span>Now</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default PerformanceMonitor;