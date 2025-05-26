import React, { useState } from 'react';
import { FiRefreshCw, FiAlertTriangle } from 'react-icons/fi';
import { TRADING_PAIRS } from '../config/trading';
import { useWebSocketWithRetry } from '../hooks/useWebSocketWithRetry';
import { formatPrice, formatChange, formatVolume } from '../services/binanceService';
import { Card } from './ui/card';
import { ErrorMessage } from './ErrorMessage';

const PriceFeedConfig: React.FC = () => {
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const { isConnected, error: wsError, send, reconnect } = useWebSocketWithRetry(
    `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:3001/ws/price-feed`,
    {
      onMessage: (data) => {
        if (data.type === 'prices' && data.data.prices) {
          setPrices(data.data.prices);
          setIsLoading(false);
        }
      },
      onConnected: () => {
        console.log('WebSocket connected, subscribing to price updates');
        send({ type: 'subscribe', data: { pairs: TRADING_PAIRS } });
      },
      onError: () => setError('Connection error occurred'),
      reconnectAttempts: 5,
      reconnectInterval: 2000
    }
  );

  if (error || wsError) {
    return (
      <Card className="p-6">
        <ErrorMessage 
          error={error || wsError?.message || 'WebSocket connection error'} 
          className="mb-4"
        />
        <button
          onClick={reconnect}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center"
        >
          <FiRefreshCw className="mr-2" />
          Retry Connection
        </button>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      {/* Status Bar */}
      <div className="mb-6 flex justify-between items-center">
        <div className="flex items-center gap-3">
          {isLoading ? (
            <div className="flex items-center gap-2">
              <FiRefreshCw className="animate-spin text-yellow-500" size={24} />
              <span className="text-yellow-500 font-semibold">Connecting to market data...</span>
            </div>
          ) : isConnected ? (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-green-500 font-semibold">Live Market Data</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-red-500 rounded-full"></span>
              <span className="text-red-500 font-semibold">Connection Lost</span>
            </div>
          )}
        </div>
      </div>

      {/* Price Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {TRADING_PAIRS.map(pair => {
          const data = prices[pair] || {};
          const priceChange = data.priceChange24h || 0;
          const isPositiveChange = priceChange >= 0;

          return (
            <Card key={pair} className="p-4">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold">{pair}</h3>
                <span className={`text-sm font-medium ${
                  isPositiveChange ? 'text-green-500' : 'text-red-500'
                }`}>
                  {formatChange(priceChange)}%
                </span>
              </div>
              <div className="text-2xl font-bold mb-2">
                {formatPrice(data.price)}
              </div>
              <div className="text-sm text-gray-500">
                Volume: {formatVolume(data.volume24h)}
              </div>
            </Card>
          );
        })}
      </div>
    </Card>
  );
};

export default PriceFeedConfig;