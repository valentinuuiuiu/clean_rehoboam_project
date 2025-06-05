import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';

// Types
export interface MarketAnalysis {
  recommendation: 'buy' | 'sell' | 'hold';
  confidence: number;
  sentiment: number;
  volatility?: number;
  trend_strength?: number;
  prediction?: {
    price_24h?: number;
    direction?: string;
    support?: number;
    resistance?: number;
  };
  arbitrage?: {
    buyNetwork: string;
    sellNetwork: string;
    profit: number;
    confidence: number;
  };
}

export interface TradingStrategy {
  id: string;
  name: string;
  description: string;
  token: string;
  recommendation: 'buy' | 'sell' | 'hold';
  confidence: number;
  risk_level: 'low' | 'moderate' | 'high';
  expected_return: number;
  timeframe: string;
  reasoning: string;
  networks: string[];
  timestamp: string;
}

export interface PriceData {
  price: number;
  change24h: number;
  high24h: number;
  low24h: number;
  volume: number;
  lastUpdate: string;
  networks: {
    [network: string]: {
      price: number;
      gasPrice?: number;
      liquidity?: string;
    };
  };
  ai?: MarketAnalysis;
}

export interface MarketData {
  prices: {
    [symbol: string]: PriceData;
  };
  timestamp: string;
  ai_enabled: boolean;
}

export interface TradeResult {
  token: string;
  amount: number;
  side: 'buy' | 'sell';
  network: string;
  success: boolean;
  timestamp: string;
  transaction_hash?: string;
  error?: string;
}

export interface ArbitrageOpportunity {
  id: string;
  token: string;
  buyNetwork: string;
  sellNetwork: string;
  profit: number;
  confidence: number;
  estimatedGasCost: number;
  executionSpeed: string;
}

export interface NetworkRecommendation {
  token: string;
  transaction_type: string;
  recommended_network: string;
  reasons: string[];
  alternatives: {
    network: string;
    score: number;
  }[];
  gas_savings: number;
}

interface UseAITradingServiceProps {
  autoConnect?: boolean;
  onMarketUpdate?: (data: MarketData) => void;
  onTradeComplete?: (result: TradeResult) => void;
  onArbitrageUpdate?: (opportunities: ArbitrageOpportunity[]) => void;
  onStrategiesUpdate?: (strategies: TradingStrategy[]) => void;
}

export const useAITradingService = ({
  autoConnect = true,
  onMarketUpdate,
  onTradeComplete,
  onArbitrageUpdate,
  onStrategiesUpdate
}: UseAITradingServiceProps = {}) => {
  // State
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [tradeHistory, setTradeHistory] = useState<TradeResult[]>([]);
  const [arbitrageOpportunities, setArbitrageOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [strategies, setStrategies] = useState<TradingStrategy[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Get WebSocket URLs
  const getMarketWebSocketUrl = () => {
    // Use the /ws/market endpoint for market data
    return `/ws/market`;
  };
  
  const getStrategiesWebSocketUrl = () => {
    // Use the dedicated /ws/strategies endpoint for trading strategies
    return `/ws/strategies`;
  };
  
  // Connect to Market WebSocket
  const {
    isConnected: isMarketConnected,
    lastMessage: lastMarketMessage,
    send: sendMarket,
    connect: connectMarket,
    disconnect: disconnectMarket,
    error: marketError
  } = useWebSocket({
    url: getMarketWebSocketUrl(),
    autoConnect,
    reconnectInterval: 3000,
    maxReconnectAttempts: 10,
    onMessage: (data) => {
      // Handle market data message
      if (data && data.type === 'market_data') {
        setMarketData(data.data);
        if (onMarketUpdate) onMarketUpdate(data.data);
      } else if (data && data.type === 'trade_result') {
        setTradeHistory(prev => [data.data, ...prev].slice(0, 10));
        if (onTradeComplete) onTradeComplete(data.data);
      } else if (data && data.type === 'arbitrage') {
        setArbitrageOpportunities(data.data);
        if (onArbitrageUpdate) onArbitrageUpdate(data.data);
      }
    },
    onConnected: () => console.log('Connected to market websocket'),
    onDisconnected: () => console.log('Disconnected from market websocket'),
    onError: (error) => console.error('Market websocket error:', error)
  });
  
  // Connect to Strategies WebSocket
  const {
    isConnected: isStrategiesConnected,
    lastMessage: lastStrategiesMessage,
    send: sendStrategies,
    connect: connectStrategies,
    disconnect: disconnectStrategies,
    error: strategiesError
  } = useWebSocket({
    url: getStrategiesWebSocketUrl(),
    autoConnect,
    reconnectInterval: 3000,
    maxReconnectAttempts: 10,
    onMessage: (data) => {
      // Handle strategies message
      if (data && data.type === 'strategies') {
        setStrategies(data.data);
        if (onStrategiesUpdate) onStrategiesUpdate(data.data);
      }
    },
    onConnected: () => console.log('Connected to strategies websocket'),
    onDisconnected: () => console.log('Disconnected from strategies websocket'),
    onError: (error) => console.error('Strategies websocket error:', error)
  });
  
  // Handle Market WebSocket messages
  useEffect(() => {
    if (!lastMarketMessage) return;
    
    try {
      const message = typeof lastMarketMessage === 'string' 
        ? JSON.parse(lastMarketMessage) 
        : lastMarketMessage;
      
      // Handle different message types
      switch (message.type) {
        case 'prices':
          const newMarketData: MarketData = {
            prices: message.data.prices || {},
            timestamp: message.data.timestamp || new Date().toISOString(),
            ai_enabled: message.data.ai_enabled || false
          };
          
          setMarketData(newMarketData);
          if (onMarketUpdate) onMarketUpdate(newMarketData);
          break;
          
        case 'tradeResult':
          const newTrade: TradeResult = message.data;
          setTradeHistory(prev => [newTrade, ...prev.slice(0, 9)]);
          if (onTradeComplete) onTradeComplete(newTrade);
          break;
          
        case 'arbitrageOpportunities':
          const opportunities: ArbitrageOpportunity[] = message.data.opportunities || [];
          setArbitrageOpportunities(opportunities);
          if (onArbitrageUpdate) onArbitrageUpdate(opportunities);
          break;
      }
    } catch (error) {
      console.error('Error handling Market WebSocket message:', error);
    }
  }, [lastMarketMessage, onMarketUpdate, onTradeComplete, onArbitrageUpdate]);
  
  // Handle Strategies WebSocket messages
  useEffect(() => {
    if (!lastStrategiesMessage) return;
    
    try {
      const message = typeof lastStrategiesMessage === 'string' 
        ? JSON.parse(lastStrategiesMessage) 
        : lastStrategiesMessage;
      
      // Handle strategies-specific message types
      switch (message.type) {
        case 'strategies_update':
          const strategyData = message.data || {};
          const receivedStrategies: TradingStrategy[] = strategyData.strategies || [];
          
          if (receivedStrategies.length > 0) {
            setStrategies(receivedStrategies);
            if (onStrategiesUpdate) onStrategiesUpdate(receivedStrategies);
          }
          break;
          
        case 'strategies':
          const strategyList: TradingStrategy[] = message.data.strategies || [];
          
          if (strategyList.length > 0) {
            setStrategies(strategyList);
            if (onStrategiesUpdate) onStrategiesUpdate(strategyList);
          }
          break;
      }
    } catch (error) {
      console.error('Error handling Strategies WebSocket message:', error);
    }
  }, [lastStrategiesMessage, onStrategiesUpdate]);
  
  // Subscribe to relevant topics on market connection
  useEffect(() => {
    if (isMarketConnected) {
      // Subscribe to topics
      sendMarket({
        type: 'subscribe',
        data: {
          topics: ['prices', 'gasPrices', 'arbitrage', 'networks'],
          networks: ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync', 'mina']
        }
      });
      
      // Request initial data
      sendMarket({
        type: 'getNetworks'
      });
      
      sendMarket({
        type: 'getGasPrices'
      });
      
      sendMarket({
        type: 'getArbitrageOpportunities'
      });
    }
  }, [isMarketConnected, sendMarket]);
  
  // Subscribe to strategies channel
  useEffect(() => {
    if (isStrategiesConnected) {
      // Subscribe to strategies channel
      sendStrategies({
        action: 'subscribe',
        channel: 'strategies'
      });
    }
  }, [isStrategiesConnected, sendStrategies]);
  
  // Combined connection status
  const isConnected = isMarketConnected && isStrategiesConnected;
  
  // Execute trading strategy
  const executeStrategy = useCallback((
    strategyIdOrToken: string,
    action?: 'buy' | 'sell' | 'hold',
    confidence?: number
  ) => {
    if (!isMarketConnected) {
      console.error('Cannot execute strategy: not connected to trading service');
      return false;
    }
    
    setIsLoading(true);
    
    sendMarket({
      type: 'executeStrategy',
      data: {
        strategyIdOrToken,
        action,
        confidence,
        timestamp: new Date().toISOString()
      }
    });
    
    // In a real implementation, we would wait for a response
    // For now, simulate a delay and then set loading to false
    setTimeout(() => setIsLoading(false), 2000);
    
    return true;
  }, [isMarketConnected, sendMarket]);
  
  // Recommend network for a transaction
  const recommendNetwork = useCallback((
    token: string,
    transactionType: string,
    amount: number
  ): Promise<NetworkRecommendation> => {
    return new Promise((resolve, reject) => {
      if (!isMarketConnected) {
        reject(new Error('Not connected to trading service'));
        return;
      }
      
      // In a real implementation, we would send a request and wait for a response
      // For now, return simulated data
      setTimeout(() => {
        const recommendation: NetworkRecommendation = {
          token,
          transaction_type: transactionType,
          recommended_network: 'arbitrum',
          reasons: [
            'Lower gas fees compared to Ethereum mainnet',
            'High liquidity for the selected token',
            'Fast transaction confirmation times'
          ],
          alternatives: [
            { network: 'optimism', score: 0.85 },
            { network: 'base', score: 0.82 },
            { network: 'polygon', score: 0.75 }
          ],
          gas_savings: 0.95
        };
        
        resolve(recommendation);
      }, 500);
    });
  }, [isMarketConnected]);
  
  // Get trading strategies for a token
  const getStrategies = useCallback((token: string, riskProfile: string = 'moderate') => {
    if (!isStrategiesConnected) {
      console.error('Cannot get strategies: not connected to strategies service');
      return false;
    }
    
    setIsLoading(true);
    
    // Request strategies via WebSocket
    sendStrategies({
      action: 'get_strategies',
      token,
      risk_profile: riskProfile
    });
    
    // For REST API approach as fallback
    fetch(`/api/trading/strategies?token=${token}&risk_profile=${riskProfile}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Error fetching strategies: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        if (data && data.strategies) {
          setStrategies(data.strategies);
          if (onStrategiesUpdate) onStrategiesUpdate(data.strategies);
        }
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error getting strategies:', error);
        setIsLoading(false);
      });
    
    return true;
  }, [isStrategiesConnected, sendStrategies, onStrategiesUpdate]);
  
  // Combined connect/disconnect functions
  const connect = useCallback(() => {
    connectMarket();
    connectStrategies();
  }, [connectMarket, connectStrategies]);
  
  const disconnect = useCallback(() => {
    disconnectMarket();
    disconnectStrategies();
  }, [disconnectMarket, disconnectStrategies]);
  
  return {
    isConnected,
    marketData,
    tradeHistory,
    arbitrageOpportunities,
    strategies,
    getStrategies,
    executeStrategy,
    recommendNetwork,
    isLoading,
    connect,
    disconnect
  };
};