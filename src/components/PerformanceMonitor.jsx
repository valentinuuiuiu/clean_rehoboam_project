import React from 'react';
import { usePerformance } from '../contexts/PerformanceContext';

const PerformanceMonitor = () => {
  const { metrics } = usePerformance();
  
  const getCPUClass = (value) => {
    if (value < 30) return 'bg-green-500';
    if (value < 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  const getMemoryClass = (value) => {
    if (value < 40) return 'bg-green-500';
    if (value < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg">
      <h3 className="text-lg font-semibold mb-3">System Performance</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm">CPU Usage</span>
            <span className="text-sm">{metrics.cpuUsage.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-gray-700 rounded overflow-hidden">
            <div 
              className={`h-full ${getCPUClass(metrics.cpuUsage)}`} 
              style={{ width: `${Math.min(metrics.cpuUsage, 100)}%` }}
            />
          </div>
        </div>
        
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm">Memory Usage</span>
            <span className="text-sm">{metrics.memoryUsage.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-gray-700 rounded overflow-hidden">
            <div 
              className={`h-full ${getMemoryClass(metrics.memoryUsage)}`} 
              style={{ width: `${Math.min(metrics.memoryUsage, 100)}%` }}
            />
          </div>
        </div>
        
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm">API Response Time</span>
            <span className="text-sm">{metrics.responseTime || 0} ms</span>
          </div>
          <div className="h-2 bg-gray-700 rounded overflow-hidden">
            <div 
              className={`h-full ${metrics.responseTime > 300 ? 'bg-red-500' : metrics.responseTime > 100 ? 'bg-yellow-500' : 'bg-green-500'}`} 
              style={{ width: `${Math.min((metrics.responseTime || 0) / 5, 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMonitor;