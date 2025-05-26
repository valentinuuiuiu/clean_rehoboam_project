/**
 * Trading platform system monitor page component
 */
import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';


const SystemMonitor = () => {
  const [systemState, setSystemState] = useState({
    health: {},
    metrics: {},
    alerts: []
  });

  const { marketData } = useMarketDataSocket();
  const { tradeUpdates } = useTradingSocket();
  const { portfolio } = usePortfolioSocket();
  const { emotions } = useMarketEmotions();

  function useMarketEmotions() {
    const [emotions, setEmotions] = useState(null);

    useEffect(() => {
        const socket = new WebSocket(`ws://${window.location.hostname}:8765/ws/market-emotions`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setEmotions(data);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            socket.close();
        };
    }, []);

    return { emotions };
  }

  // System monitoring websocket
  const { isConnected, error } = useWebSocket(
    `ws://${window.location.hostname}:8765/ws/system`,
    {
      onMessage: (message) => {
        switch (message.type) {
          case 'system_health':
            setSystemState(prev => ({ ...prev, health: message.data }));
            break;
          case 'websocket_metrics':
            setSystemState(prev => ({ ...prev, metrics: message.data }));
            break;
          case 'alerts':
            setSystemState(prev => ({ ...prev, alerts: message.data }));
            break;
        }
      }
    }
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-semibold text-gray-900">System Monitor</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Connection Status */}
        <div className="mb-6">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="font-medium">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <h3 className="text-red-800 font-medium">Connection Error</h3>
            <p className="text-red-600">{error.message}</p>
          </div>
        )}

        {/* Monitoring Dashboard */}
        <div className="space-y-6">
          <MonitoringDashboard
            systemHealth={systemState.health}
            websocketMetrics={systemState.metrics}
            alerts={systemState.alerts}
          />
        </div>

        {/* Real-time Data Feeds */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Market Data Feed */}
          <DataFeed
            title="Market Data Stream"
            data={marketData}
            isActive={!!marketData}
          />

          {/* Trade Updates Feed */}
          <DataFeed
            title="Trade Updates"
            data={tradeUpdates}
            isActive={!!tradeUpdates?.length}
          />

          {/* Portfolio Updates Feed */}
          <DataFeed
            title="Portfolio Updates"
            data={portfolio}
            isActive={!!portfolio}
          />

          {/* Market Emotions Feed */}
          <DataFeed
            title="Market Emotions"
            data={emotions}
            isActive={!!emotions}
          />
        </div>

        {/* Active Alerts */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Active Alerts</h2>
          <div className="space-y-4">
            {systemState.alerts.map((alert, index) => (
              <AlertCard key={index} alert={alert} />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

interface DataFeedProps {
  title: string;
  data: any;
  isActive: boolean;
}

const DataFeed: React.FC<DataFeedProps> = ({ title, data, isActive }) => (
  <div className="bg-white shadow rounded-lg p-4">
    <div className="flex items-center justify-between mb-4">
      <h3 className="font-medium">{title}</h3>
      <span className={`px-2 py-1 rounded-full text-xs ${
        isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
      }`}>
        {isActive ? 'Active' : 'Inactive'}
      </span>
    </div>
    <pre className="bg-gray-50 p-3 rounded text-sm overflow-auto max-h-40">
      {JSON.stringify(data, null, 2)}
    </pre>
  </div>
);

interface Alert {
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  value: number;
  threshold: number;
  timestamp: number;
}

const AlertCard = ({ alert }: { alert: Alert }) => {
  const severityColors = {
    info: 'blue',
    warning: 'yellow',
    error: 'red',
    critical: 'red'
  };
  
  const color = severityColors[alert.severity] || 'gray';

  return (
    <div className={`bg-${color}-50 border border-${color}-200 rounded-md p-4`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <span className={`inline-block w-2 h-2 rounded-full bg-${color}-500 mr-2`} />
          <h4 className={`font-medium text-${color}-900`}>{alert.message}</h4>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs bg-${color}-100 text-${color}-800`}>
          {alert.severity}
        </span>
      </div>
      <div className="mt-2 text-sm text-gray-600">
        <p>Value: {alert.value}</p>
        <p>Threshold: {alert.threshold}</p>
        <p>Time: {new Date(alert.timestamp).toLocaleString()}</p>
      </div>
    </div>
  );
};

export default SystemMonitor;
function useMarketDataSocket() {
    const [marketData, setMarketData] = useState(null);

    useEffect(() => {
        const socket = new WebSocket(`ws://${window.location.hostname}:8765/ws/market-data`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMarketData(data);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            socket.close();
        };
    }, []);

    return { marketData };
}
function useTradingSocket() {
    const [tradeUpdates, setTradeUpdates] = useState<any[]|null>(null);

    useEffect(() => {
        const socket = new WebSocket(`ws://${window.location.hostname}:8765/ws/trade-updates`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setTradeUpdates(data);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            socket.close();
        };
    }, []);

    return { tradeUpdates };
}
function usePortfolioSocket() {
    const [portfolio, setPortfolio] = useState(null);

    useEffect(() => {
        const socket = new WebSocket(`ws://${window.location.hostname}:8765/ws/portfolio`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setPortfolio(data);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            socket.close();
        };
    }, []);

    return { portfolio };
}

interface MonitoringDashboardProps {
  systemHealth: object;
  websocketMetrics: object;
  alerts: any[];
}

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({ systemHealth, websocketMetrics }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <DataFeed title="System Health" data={systemHealth} isActive={Object.keys(systemHealth).length > 0} />
      <DataFeed title="WebSocket Metrics" data={websocketMetrics} isActive={Object.keys(websocketMetrics).length > 0} />
    </div>
  );

};