import React, { useMemo } from 'react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import { usePerformanceMetrics } from '../services/performanceMetricsCollector';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PerformanceInsights: React.FC = () => {
  const { metrics, averages, trends } = usePerformanceMetrics(3600000); // Last hour

  const recommendations = useMemo(() => {
    const insights = [];

    if (averages.avgRenderTime > 16) {
      insights.push({
        type: 'warning',
        message: 'High render times detected. Consider implementing React.memo or useMemo for expensive components.'
      });
    }

    if (averages.avgNetworkLatency > 1000) {
      insights.push({
        type: 'warning',
        message: 'Network latency is high. Consider implementing request caching or reducing payload sizes.'
      });
    }

    if (trends.memoryUsageTrend > 20) {
      insights.push({
        type: 'error',
        message: 'Memory usage is trending upward significantly. Check for memory leaks in useEffect cleanup.'
      });
    }

    if (trends.errorCountTrend > 0) {
      insights.push({
        type: 'error',
        message: 'Error rate is increasing. Review error logs and implement additional error boundaries.'
      });
    }

    return insights;
  }, [averages, trends]);

  const formatTrend = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
  };

  const getTrendColor = (value: number) => {
    if (value <= -10) return 'text-green-500';
    if (value >= 10) return 'text-red-500';
    return 'text-yellow-500';
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-xl font-bold mb-4">Performance Insights</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Render Time</p>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{averages.avgRenderTime.toFixed(1)}ms</span>
              <span className={`text-sm ${getTrendColor(trends.renderTimeTrend)}`}>
                {formatTrend(trends.renderTimeTrend)}
              </span>
            </div>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Network Latency</p>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{averages.avgNetworkLatency.toFixed(1)}ms</span>
              <span className={`text-sm ${getTrendColor(trends.networkLatencyTrend)}`}>
                {formatTrend(trends.networkLatencyTrend)}
              </span>
            </div>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Memory Usage</p>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{(averages.avgMemoryUsage / 1024 / 1024).toFixed(1)}MB</span>
              <span className={`text-sm ${getTrendColor(trends.memoryUsageTrend)}`}>
                {formatTrend(trends.memoryUsageTrend)}
              </span>
            </div>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Error Rate</p>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{averages.avgErrorRate.toFixed(2)}/min</span>
              <span className={`text-sm ${getTrendColor(trends.errorCountTrend)}`}>
                {formatTrend(trends.errorCountTrend)}
              </span>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Performance Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  formatter={(value: number) => value.toFixed(2)}
                />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="renderTime"
                  stroke="#3B82F6"
                  name="Render Time (ms)"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="networkLatency"
                  stroke="#10B981"
                  name="Network Latency (ms)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {recommendations.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
            <div className="space-y-2">
              {recommendations.map((rec, index) => (
                <div 
                  key={index} 
                  className={`p-3 rounded-lg ${
                    rec.type === 'error' ? 'bg-red-50 text-red-700' : 
                    rec.type === 'warning' ? 'bg-yellow-50 text-yellow-700' : 
                    'bg-blue-50 text-blue-700'
                  }`}
                >
                  {rec.message}
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default PerformanceInsights;