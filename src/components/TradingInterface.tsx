import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import { ErrorMessage } from './ErrorMessage';
import { useWeb3 } from '../contexts/Web3Context';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useWebSocketWithRetry } from '../hooks/useWebSocketWithRetry';

interface PriceData {
  timestamp: number;
  price: number;
  volume: number;
}

interface Price {
  price: number;
  change: number;
}

interface PriceHistory {
  [pair: string]: PriceData[];
}

interface PriceState {
  [pair: string]: Price;
}

interface WebSocketMessage {
  type: string;
  data: PriceState;
}

const SUPPORTED_PAIRS = [
  "ETH/USD", "BTC/USD", "LINK/USD", 
  "MANA/USD", "EAI/USD", "XRP/USD", "XMR/USD", "AMP/USD"
];

const TradingInterface: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState<string>(SUPPORTED_PAIRS[0]);
  const [amount, setAmount] = useState<number>(0);
  const [orderType, setOrderType] = useState<'Market' | 'Limit' | 'Stop' | 'Stop Limit'>('Market');
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [priceData, setPriceData] = useState<PriceState>({});
  const { account } = useWeb3();

  // WebSocket connection
  const { isConnected, error: wsError, send } = useWebSocketWithRetry(
    `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:3001/ws/prices`,
    {
      onMessage: (message: WebSocketMessage) => {
        if (message.type === 'price_update') {
          setPriceData(message.data);
        }
      }
    }
  );

  // Price history query
  const { data: priceHistory, error: historyError } = useQuery<PriceHistory>({
    queryKey: ['price-history', selectedPair],
    queryFn: async () => {
      const response = await fetch(`/api/price-history/${selectedPair}`);
      if (!response.ok) throw new Error('Failed to fetch price history');
      return response.json();
    }
  });

  // Subscribe to price updates on mount
  useEffect(() => {
    if (isConnected) {
      send({ type: 'subscribe', pairs: SUPPORTED_PAIRS });
    }
    return () => {
      if (isConnected) {
        send({ type: 'unsubscribe', pairs: SUPPORTED_PAIRS });
      }
    };
  }, [isConnected, send]);

  const createPriceChart = (pair: string, history: PriceData[]) => {
    if (!history?.length) return null;

    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(156, 163, 175, 0.1)" />
          <XAxis 
            dataKey="timestamp" 
            type="number"
            domain={['auto', 'auto']}
            scale="time"
            tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
          />
          <YAxis yAxisId="price" orientation="left" />
          <YAxis yAxisId="volume" orientation="right" />
          <Tooltip />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="price"
            stroke="#10B981"
            dot={false}
          />
          <Line
            yAxisId="volume"
            type="monotone"
            dataKey="volume"
            stroke="rgba(16, 185, 129, 0.2)"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const isValidOrder = () => {
    return selectedPair && amount > 0 && orderType && tradeType;
  };

  if (wsError || historyError) {
    return <ErrorMessage error={wsError || historyError} />;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {SUPPORTED_PAIRS.map((pair) => (
          <div 
            key={pair}
            className={`bg-card text-card-foreground rounded-lg border shadow-sm p-4 cursor-pointer transition-all ${
              selectedPair === pair ? 'ring-2 ring-blue-500' : ''
            }`}
            onClick={() => setSelectedPair(pair)}
          >
            <div className="flex flex-col space-y-2">
              <span className="font-bold text-lg">{pair}</span>
              {priceData[pair] && (
                <>
                  <span className="text-2xl">
                    ${priceData[pair].price.toLocaleString(undefined, { 
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </span>
                  <span className={`${
                    priceData[pair].change >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {priceData[pair].change >= 0 ? '+' : ''}{priceData[pair].change.toFixed(2)}%
                  </span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card text-card-foreground rounded-lg border shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Price Chart</h2>
          {priceHistory?.[selectedPair] && createPriceChart(selectedPair, priceHistory[selectedPair])}
        </div>

        <div className="bg-card text-card-foreground rounded-lg border shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Place Order</h2>
          <div className="space-y-4">
            <div className="flex gap-4">
              <button
                className={`flex-1 py-2 px-4 rounded ${
                  tradeType === 'buy' 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}
                onClick={() => setTradeType('buy')}
              >
                Buy
              </button>
              <button
                className={`flex-1 py-2 px-4 rounded ${
                  tradeType === 'sell' 
                    ? 'bg-red-500 text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}
                onClick={() => setTradeType('sell')}
              >
                Sell
              </button>
            </div>

            <input
              type="number"
              min="0"
              step="0.01"
              value={amount || ''}
              onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
              placeholder="Amount"
            />

            <select
              value={orderType}
              onChange={(e) => setOrderType(e.target.value as any)}
              className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
            >
              <option value="Market">Market</option>
              <option value="Limit">Limit</option>
              <option value="Stop">Stop</option>
              <option value="Stop Limit">Stop Limit</option>
            </select>

            <button
              className="w-full py-2 px-4 bg-blue-500 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!isValidOrder() || !account}
            >
              {!account ? 'Connect Wallet to Trade' : 'Place Order'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingInterface;