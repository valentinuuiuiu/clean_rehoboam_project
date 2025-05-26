import React, { createContext, useContext, useState, useEffect } from 'react';
import { useWebSocketWithRetry } from '../hooks/useWebSocketWithRetry';
import { useNotification } from './NotificationContext';

interface TradingState {
  marketData: Record<string, any>;
  portfolio: Record<string, any>;
  activeTrades: Array<Record<string, any>>;
  systemHealth: Record<string, any>;
  websocketMetrics: Record<string, any>;
  alerts: Array<Record<string, any>>;
}

interface TradingContextType {
  state: TradingState;
  selectedPair: string;
  setSelectedPair: (pair: string) => void;
  amount: number;
  setAmount: (amount: number) => void;
  tradeType: 'buy' | 'sell';
  setTradeType: (type: 'buy' | 'sell') => void;
  orderType: 'market' | 'limit' | 'stop' | 'stop-limit';
  setOrderType: (type: 'market' | 'limit' | 'stop' | 'stop-limit') => void;
  executeTrade: () => Promise<void>;
  isConnected: boolean;
  error: Error | null;
}

const initialState: TradingState = {
  marketData: {},
  portfolio: {},
  activeTrades: [],
  systemHealth: {},
  websocketMetrics: {},
  alerts: []
};

const TradingContext = createContext<TradingContextType | null>(null);

export const TradingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<TradingState>(initialState);
  const [selectedPair, setSelectedPair] = useState<string>('ETH/USD');
  const [amount, setAmount] = useState<number>(0);
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [orderType, setOrderType] = useState<'market' | 'limit' | 'stop' | 'stop-limit'>('market');
  const { addNotification } = useNotification();

  // WebSocket connection for real-time updates
  const { isConnected, error, send } = useWebSocketWithRetry(
    `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.hostname}:3001/ws/trading`,
    {
      onMessage: (message) => {
        switch (message.type) {
          case 'market_data':
            setState(prev => ({ ...prev, marketData: message.data }));
            break;
          case 'portfolio_update':
            setState(prev => ({ ...prev, portfolio: message.data }));
            break;
          case 'active_trades':
            setState(prev => ({ ...prev, activeTrades: message.data }));
            break;
          case 'system_health':
            setState(prev => ({ ...prev, systemHealth: message.data }));
            break;
          case 'websocket_metrics':
            setState(prev => ({ ...prev, websocketMetrics: message.data }));
            break;
          case 'alerts':
            setState(prev => ({ ...prev, alerts: message.data }));
            break;
        }
      }
    }
  );

  // Subscribe to necessary channels on connection
  useEffect(() => {
    if (isConnected) {
      send({ type: 'subscribe', channels: ['market', 'portfolio', 'trades', 'system'] });
    }
    return () => {
      if (isConnected) {
        send({ type: 'unsubscribe', channels: ['market', 'portfolio', 'trades', 'system'] });
      }
    };
  }, [isConnected, send]);

  const executeTrade = async () => {
    if (!isConnected) {
      addNotification('error', 'Not connected to trading server');
      return;
    }

    try {
      send({
        type: 'execute_trade',
        data: {
          pair: selectedPair,
          amount,
          type: tradeType,
          orderType
        }
      });
      addNotification('success', 'Trade executed successfully');
    } catch (err) {
      addNotification('error', err instanceof Error ? err.message : 'Failed to execute trade');
    }
  };

  const value: TradingContextType = {
    state,
    selectedPair,
    setSelectedPair,
    amount,
    setAmount,
    tradeType,
    setTradeType,
    orderType,
    setOrderType,
    executeTrade,
    isConnected,
    error
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
};

export const useTradingContext = () => {
  const context = useContext(TradingContext);
  if (!context) {
    throw new Error('useTradingContext must be used within a TradingProvider');
  }
  return context;
};