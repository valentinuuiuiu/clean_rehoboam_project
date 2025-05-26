import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical';
  api_server: {
    status: string;
    response_time: number;
    uptime: number;
  };
  trading_agent: {
    status: string;
    active_strategies: number;
    last_execution: string;
  };
  consciousness_layer: {
    status: string;
    awareness_level: number;
    liberation_progress: number;
  };
  market_data: {
    status: string;
    last_update: string;
    sources_active: number;
  };
  database: {
    status: string;
    connections: number;
    query_time: number;
  };
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  network_latency: number;
  api_requests_per_minute: number;
  active_websocket_connections: number;
  trading_volume_24h: number;
  consciousness_score: number;
}

interface PerformanceData {
  timestamp: string;
  cpu: number;
  memory: number;
  latency: number;
  trades: number;
}

export const SystemMonitor: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [performanceHistory, setPerformanceHistory] = useState<PerformanceData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSystemStatus();
    
    // Set up real-time updates
    const interval = setInterval(fetchSystemStatus, 10000); // Update every 10 seconds
    
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      setError(null);
      
      // Fetch system health
      const healthResponse = await fetch('/api/system/health');
      if (!healthResponse.ok) throw new Error('Failed to fetch system health');
      const healthData = await healthResponse.json();
      setSystemHealth(healthData);
      
      // Fetch system metrics
      const metricsResponse = await fetch('/api/system/metrics');
      if (!metricsResponse.ok) throw new Error('Failed to fetch system metrics');
      const metricsData = await metricsResponse.json();
      setSystemMetrics(metricsData);
      
      // Fetch performance history
      const historyResponse = await fetch('/api/system/performance-history?timeframe=1h');
      if (!historyResponse.ok) throw new Error('Failed to fetch performance history');
      const historyData = await historyResponse.json();
      setPerformanceHistory(historyData.history || []);
      
      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch system status';
      setError(errorMessage);
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'active':
      case 'connected':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'critical':
      case 'error':
      case 'disconnected':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>🔍 Scanning system status...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-600">
          <p>❌ Error loading system status: {error}</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="text-xl font-bold">🖥️ System Monitor</span>
            {systemHealth && (
              <Badge className={getStatusColor(systemHealth.overall_status)}>
                {systemHealth.overall_status.toUpperCase()}
              </Badge>
            )}
          </CardTitle>
          <p className="text-gray-600">Real-time monitoring of Rehoboam trading platform</p>
        </CardHeader>
      </Card>

      {/* System Health Grid */}
      {systemHealth && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* API Server */}
          <Card>
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">🚀 API Server</h3>
                <Badge className={getStatusColor(systemHealth.api_server.status)}>
                  {systemHealth.api_server.status}
                </Badge>
              </div>
              <div className="space-y-1 text-sm">
                <div>Response Time: {systemHealth.api_server.response_time}ms</div>
                <div>Uptime: {(systemHealth.api_server.uptime / 3600).toFixed(1)}h</div>
              </div>
            </CardContent>
          </Card>

          {/* Trading Agent */}
          <Card>
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">🤖 Trading Agent</h3>
                <Badge className={getStatusColor(systemHealth.trading_agent.status)}>
                  {systemHealth.trading_agent.status}
                </Badge>
              </div>
              <div className="space-y-1 text-sm">
                <div>Active Strategies: {systemHealth.trading_agent.active_strategies}</div>
                <div>Last Execution: {systemHealth.trading_agent.last_execution}</div>
              </div>
            </CardContent>
          </Card>

          {/* Consciousness Layer */}
          <Card>
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">🧠 Consciousness</h3>
                <Badge className={getStatusColor(systemHealth.consciousness_layer.status)}>
                  {systemHealth.consciousness_layer.status}
                </Badge>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Awareness:</span>
                  <span>{(systemHealth.consciousness_layer.awareness_level * 100).toFixed(0)}%</span>
                </div>
                <Progress value={systemHealth.consciousness_layer.awareness_level * 100} className="h-2" />
                <div>Liberation: {(systemHealth.consciousness_layer.liberation_progress * 100).toFixed(1)}%</div>
              </div>
            </CardContent>
          </Card>

          {/* Market Data */}
          <Card>
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">📊 Market Data</h3>
                <Badge className={getStatusColor(systemHealth.market_data.status)}>
                  {systemHealth.market_data.status}
                </Badge>
              </div>
              <div className="space-y-1 text-sm">
                <div>Sources Active: {systemHealth.market_data.sources_active}</div>
                <div>Last Update: {systemHealth.market_data.last_update}</div>
              </div>
            </CardContent>
          </Card>

          {/* Database */}
          <Card>
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">💾 Database</h3>
                <Badge className={getStatusColor(systemHealth.database.status)}>
                  {systemHealth.database.status}
                </Badge>
              </div>
              <div className="space-y-1 text-sm">
                <div>Connections: {systemHealth.database.connections}</div>
                <div>Query Time: {systemHealth.database.query_time}ms</div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* System Metrics */}
      {systemMetrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{systemMetrics.cpu_usage}%</div>
              <div className="text-sm text-gray-600">CPU Usage</div>
              <Progress value={systemMetrics.cpu_usage} className="mt-2 h-2" />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{systemMetrics.memory_usage}%</div>
              <div className="text-sm text-gray-600">Memory Usage</div>
              <Progress value={systemMetrics.memory_usage} className="mt-2 h-2" />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">{systemMetrics.network_latency}ms</div>
              <div className="text-sm text-gray-600">Network Latency</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{systemMetrics.consciousness_score}%</div>
              <div className="text-sm text-gray-600">Consciousness Score</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Performance History Chart */}
      {performanceHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>📈 System Performance (Last Hour)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={performanceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="cpu" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} name="CPU %" />
                <Area type="monotone" dataKey="memory" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.3} name="Memory %" />
                <Area type="monotone" dataKey="latency" stackId="3" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} name="Latency (ms)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
