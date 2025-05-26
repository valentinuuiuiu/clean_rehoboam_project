/** Real-time monitoring dashboard for WebSocket system */
import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar, ResponsiveContainer
} from 'recharts';
import { useWebSocket } from '../hooks/useWebSocket';

interface MetricsUpdateData {
    connections: Metrics['connections'];
    metrics: {
        latency: number;
        errors: number;
        messageRate: number;
    };
}

interface Metrics {
    connections: {
        current: number;
        byChannel: Record<string, number>;
    };
    latency: number[];
    errors: number[];
    messageRate: number[];
}

const MonitoringDashboard = () => {
  const [metrics, setMetrics] = useState<Metrics>({
    connections: { current: 0, byChannel: {} },
    latency: [],
    errors: [],
    messageRate: []
  });

  const { isConnected, error } = useWebSocket(
    `ws://${window.location.hostname}:8765/ws/system`,
    {
      onMessage: (message) => {
        if (message.type === 'metrics_update') {
          updateMetrics(message.data);
        }
      }
    }
  );

const updateMetrics = (data: MetricsUpdateData) => {
    setMetrics(prev => ({
        ...prev,
        connections: data.connections,
        latency: [...prev.latency.slice(-20), data.metrics.latency],
        errors: [...prev.errors.slice(-20), data.metrics.errors],
        messageRate: [...prev.messageRate.slice(-20), data.metrics.messageRate]
    }));
};

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">System Monitoring</h1>
      
      {/* Connection Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatusCard
          title="Connection Status"
          value={isConnected ? 'Connected' : 'Disconnected'}
          status={isConnected ? 'success' : 'error'}
        />
        <StatusCard
          title="Active Connections"
          value={metrics.connections.current}
          status="info"
        />
        <StatusCard
          title="Error Rate"
          value={`${metrics.errors[metrics.errors.length - 1] || 0}/min`}
          status={getErrorStatus(metrics.errors[metrics.errors.length - 1])}
        />
        <StatusCard
          title="Avg Latency"
          value={`${getAverageLatency(metrics.latency)}ms`}
          status={getLatencyStatus(getAverageLatency(metrics.latency))}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <ChartCard title="Message Rate">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={formatChartData(metrics.messageRate)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Error Rate">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={formatChartData(metrics.errors)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#ff4d4f" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Channel Subscriptions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Channel Subscriptions</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={formatChannelData(metrics.connections.byChannel)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="channel" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="subscribers" fill="#1890ff" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Error Log */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-8">
          <h3 className="text-red-800 font-medium">Error</h3>
          <p className="text-red-600">{error.message}</p>
        </div>
      )}
    </div>
  );
};

const StatusCard: React.FC<StatusCardProps> = ({ title, value, status }) => {
  const statusColors: Record<string, string> = {
    success: 'bg-green-100 text-green-800 border-green-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200'
  };

  const colorClass = statusColors[status] || statusColors.info;

  return (
    <div className={`p-4 rounded-lg border ${colorClass}`}>
      <h3 className="font-medium mb-2">{title}</h3>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
};

const ChartCard: React.FC<ChartCardProps> = ({ title, children }) => (
  <div className="bg-white p-4 rounded-lg border border-gray-200">
    <h3 className="font-medium mb-4">{title}</h3>
    {children}
  </div>
);

const getErrorStatus = (errorRate: number): 'success' | 'warning' | 'error' => {
    if (errorRate === 0) return 'success';
    if (errorRate < 5) return 'warning';
    return 'error';
};

interface StatusCardProps {
    title: string;
    value: string | number;
    status: 'success' | 'error' | 'warning' | 'info';
}

interface ChartCardProps {
    title: string;
    children: React.ReactNode;
}

const getLatencyStatus = (latency: number): 'success' | 'warning' | 'error' => {
    if (latency < 100) return 'success';
    if (latency < 300) return 'warning';
    return 'error';
};

const getAverageLatency = (latencyData: number[]): number => {
  if (latencyData.length === 0) return 0;
  const sum = latencyData.reduce((a, b) => a + b, 0);
  return Math.round(sum / latencyData.length);
};

const formatChartData = (data: number[]): { time: string; value: number }[] => {
  return data.map((value, index) => ({
    time: new Date(Date.now() - (data.length - index) * 15000).toLocaleTimeString(),
    value
  }));
};

const formatChannelData = (channelData: Record<string, number>): { channel: string; subscribers: number }[] => {
  return Object.entries(channelData).map(([channel, subscribers]) => ({
    channel,
    subscribers
  }));
};

export default MonitoringDashboard;