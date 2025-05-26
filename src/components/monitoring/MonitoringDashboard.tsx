import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar, ResponsiveContainer
} from 'recharts';
import { Card } from '../ui/card';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';

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

interface StatusCardProps {
  title: string;
  value: string | number;
  status: 'success' | 'error' | 'warning' | 'info';
}

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

const MonitoringDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics>({
    connections: { current: 0, byChannel: {} },
    latency: [],
    errors: [],
    messageRate: []
  });

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectInterval: NodeJS.Timeout;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(`ws://${window.location.hostname}:8765/ws/system`);
        
        ws.onopen = () => {
          setIsConnected(true);
          setError(null);
          console.log('Monitoring WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (message.type === 'metrics_update') {
              updateMetrics(message.data);
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          console.log('Monitoring WebSocket disconnected');
          // Auto-reconnect after 5 seconds
          reconnectInterval = setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = (err) => {
          setError(new Error('WebSocket connection failed'));
          console.error('WebSocket error:', err);
        };
      } catch (err) {
        setError(new Error('Failed to establish WebSocket connection'));
      }
    };

    // Fetch initial system health data
    fetchSystemHealth();
    
    // Connect WebSocket
    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectInterval) {
        clearTimeout(reconnectInterval);
      }
    };
  }, []);

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/system/health');
      if (response.ok) {
        const healthData = await response.json();
        // Update metrics with initial health data
        setMetrics(prev => ({
          ...prev,
          connections: healthData.connections || prev.connections,
          latency: healthData.latency ? [healthData.latency] : prev.latency,
          errors: healthData.errors ? [healthData.errors] : prev.errors,
          messageRate: healthData.messageRate ? [healthData.messageRate] : prev.messageRate
        }));
      }
    } catch (err) {
      console.error('Error fetching system health:', err);
    }
  };

  const updateMetrics = (data: MetricsUpdateData) => {
    setMetrics(prev => ({
      ...prev,
      connections: data.connections,
      latency: [...prev.latency.slice(-29), data.metrics.latency],
      errors: [...prev.errors.slice(-29), data.metrics.errors],
      messageRate: [...prev.messageRate.slice(-29), data.metrics.messageRate]
    }));
  };

  const formatChartData = (values: number[]) => {
    return values.map((value, index) => ({
      time: `${index}s`,
      value
    }));
  };

  const formatChannelData = (byChannel: Record<string, number>) => {
    return Object.entries(byChannel).map(([channel, subscribers]) => ({
      channel,
      subscribers
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            System Monitoring Dashboard
          </h1>
          <p className="text-purple-300">
            Real-time monitoring of Rehoboam consciousness layers and trading systems
          </p>
        </div>

        {/* Connection Status */}
        <div className="mb-6">
          <Alert variant={isConnected ? 'success' : 'destructive'}>
            <AlertTitle>WebSocket Status</AlertTitle>
            <AlertDescription>
              {isConnected ? 'Connected to monitoring system' : 'Disconnected from monitoring system'}
            </AlertDescription>
          </Alert>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="Active Connections"
            value={metrics.connections.current}
            status={metrics.connections.current > 0 ? 'success' : 'warning'}
          />
          <StatusCard
            title="Avg Latency"
            value={`${metrics.latency.slice(-1)[0] || 0}ms`}
            status={metrics.latency.slice(-1)[0] > 1000 ? 'error' : 'success'}
          />
          <StatusCard
            title="Error Rate"
            value={`${metrics.errors.slice(-1)[0] || 0}/min`}
            status={metrics.errors.slice(-1)[0] > 5 ? 'error' : 'success'}
          />
          <StatusCard
            title="Message Rate"
            value={`${metrics.messageRate.slice(-1)[0] || 0}/s`}
            status='info'
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartCard title="System Latency">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formatChartData(metrics.latency)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Message Rate">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formatChartData(metrics.messageRate)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Error Rate">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formatChartData(metrics.errors)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#EF4444" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Channel Subscriptions">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={formatChannelData(metrics.connections.byChannel)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="channel" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Bar dataKey="subscribers" fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>System Error</AlertTitle>
            <AlertDescription>{error.message}</AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
};

const StatusCard: React.FC<StatusCardProps> = ({ title, value, status }) => {
  const statusColors: Record<string, string> = {
    success: 'bg-green-900/30 text-green-300 border-green-500/50',
    error: 'bg-red-900/30 text-red-300 border-red-500/50',
    warning: 'bg-yellow-900/30 text-yellow-300 border-yellow-500/50',
    info: 'bg-blue-900/30 text-blue-300 border-blue-500/50'
  };

  const colorClass = statusColors[status] || statusColors.info;

  return (
    <Card className={`p-6 border ${colorClass} backdrop-blur-sm`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-70">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <Badge className={colorClass}>
          {status.toUpperCase()}
        </Badge>
      </div>
    </Card>
  );
};

const ChartCard: React.FC<ChartCardProps> = ({ title, children }) => {
  return (
    <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      {children}
    </Card>
  );
};

export default MonitoringDashboard;
