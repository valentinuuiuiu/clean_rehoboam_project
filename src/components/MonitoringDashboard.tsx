import React from 'react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import WebSocketMonitor from './WebSocketMonitor';
import { useBackgroundTask } from '../contexts/BackgroundTaskContext';
import { usePerformance } from '../contexts/PerformanceContext';

const MonitoringDashboard: React.FC = () => {
  const { tasks } = useBackgroundTask();
  const { getStats } = usePerformance();
  const stats = getStats();

  const activeTasks = tasks.filter(task => task.status === 'running');
  const completedTasks = tasks.filter(task => task.status === 'completed');
  const failedTasks = tasks.filter(task => task.status === 'failed');

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* WebSocket Status */}
        <WebSocketMonitor />

        {/* Performance Metrics */}
        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-500">Average Render Time</span>
                <span className={`font-semibold ${
                  stats.avgRenderTime > 16 ? 'text-red-500' : 'text-green-500'
                }`}>
                  {stats.avgRenderTime.toFixed(1)}ms
                </span>
              </div>
              <Progress 
                value={Math.min((stats.avgRenderTime / 16) * 100, 100)} 
                className={stats.avgRenderTime > 16 ? 'bg-red-200' : 'bg-green-200'}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Total Renders</p>
                <p className="font-semibold">{stats.totalRenders}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Memory Usage</p>
                <p className="font-semibold">
                  {(performance as any).memory ? Math.round((performance as any).memory.usedJSHeapSize / 1048576) : 'N/A'} MB
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Background Tasks */}
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">Background Tasks</h3>
        
        {activeTasks.length > 0 && (
          <div className="space-y-4 mb-6">
            <h4 className="font-medium text-sm text-gray-500">Active Tasks</h4>
            {activeTasks.map(task => (
              <div key={task.id} className="bg-blue-50 p-3 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="font-medium">{task.name}</span>
                  <span className="text-sm text-blue-600">
                    {task.progress ? `${Math.round(task.progress)}%` : 'Running...'}
                  </span>
                </div>
                {task.progress !== undefined && (
                  <Progress value={task.progress} className="bg-blue-200" />
                )}
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Completed Tasks */}
          <div>
            <h4 className="font-medium text-sm text-gray-500 mb-3">Recently Completed</h4>
            <div className="space-y-2">
              {completedTasks.slice(-3).map(task => (
                <div key={task.id} className="bg-green-50 p-3 rounded-lg">
                  <div className="flex justify-between">
                    <span>{task.name}</span>
                    <span className="text-sm text-green-600">
                      {task.endTime && task.startTime
                        ? `${((task.endTime - task.startTime) / 1000).toFixed(1)}s`
                        : 'Completed'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Failed Tasks */}
          <div>
            <h4 className="font-medium text-sm text-gray-500 mb-3">Recent Failures</h4>
            <div className="space-y-2">
              {failedTasks.slice(-3).map(task => (
                <div key={task.id} className="bg-red-50 p-3 rounded-lg">
                  <div className="flex justify-between">
                    <span>{task.name}</span>
                    <span className="text-sm text-red-600">Failed</span>
                  </div>
                  {task.error && (
                    <p className="text-sm text-red-500 mt-1">{task.error.message}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default MonitoringDashboard;