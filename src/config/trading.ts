import { z } from 'zod';

export const SUPPORTED_PAIRS = [
  'ETH/USD', 'BTC/USD', 'LINK/USD',
  'DOT/USD', 'SOL/USD', 'AVAX/USD',
  'MATIC/USD', 'UNI/USD', 'AAVE/USD',
  'ATOM/USD', 'LTC/USD', 'NEAR/USD',
  'ICP/USD', 'ALGO/USD'
] as const;

export const OrderType = {
  MARKET: 'market',
  LIMIT: 'limit',
  STOP: 'stop',
  STOP_LIMIT: 'stop-limit'
} as const;

export const TradeType = {
  BUY: 'buy',
  SELL: 'sell'
} as const;

// Zod schemas for type validation
export const PriceDataSchema = z.object({
  price: z.number(),
  change: z.number()
});

export const TradeOrderSchema = z.object({
  pair: z.enum(SUPPORTED_PAIRS),
  type: z.enum(['buy', 'sell']),
  orderType: z.enum(['market', 'limit', 'stop', 'stop-limit']),
  amount: z.number().positive(),
  price: z.number().optional(), // Required for limit and stop orders
  stopPrice: z.number().optional() // Required for stop and stop-limit orders
});

// Types derived from schemas
export type PriceData = z.infer<typeof PriceDataSchema>;
export type TradeOrder = z.infer<typeof TradeOrderSchema>;
export type TradingPair = typeof SUPPORTED_PAIRS[number];
export type OrderTypeValue = typeof OrderType[keyof typeof OrderType];
export type TradeTypeValue = typeof TradeType[keyof typeof TradeType];

// Initial trading state
export const initialPrices: Record<TradingPair, PriceData> = {
  'ETH/USD': { price: 2500.00, change: 2.5 },
  'BTC/USD': { price: 42000.00, change: 1.2 },
  'LINK/USD': { price: 15.00, change: -0.8 },
  'DOT/USD': { price: 7.50, change: 0.5 },
  'SOL/USD': { price: 105.00, change: 3.2 },
  'AVAX/USD': { price: 45.00, change: -1.5 },
  'MATIC/USD': { price: 0.85, change: 1.8 },
  'UNI/USD': { price: 6.20, change: -0.3 },
  'AAVE/USD': { price: 95.00, change: 2.1 },
  'ATOM/USD': { price: 11.50, change: -1.2 },
  'LTC/USD': { price: 72.00, change: 0.9 },
  'NEAR/USD': { price: 3.20, change: 1.5 },
  'ICP/USD': { price: 12.80, change: -2.1 },
  'ALGO/USD': { price: 0.18, change: 0.7 }
};

export const TRADING_PAIRS = [
  'ETHUSDT',
  'BTCUSDT',
  'LINKUSDT',
  'DOTUSDT',
  'SOLUSDT',
  'AVAXUSDT'
] as const;

export const SUPPORTED_CHAINS = {
  ethereum: {
    name: 'Ethereum',
    chainId: 1,
    rpcUrl: import.meta.env.VITE_ETHEREUM_RPC_URL,
    explorer: 'https://etherscan.io'
  },
  arbitrum: {
    name: 'Arbitrum',
    chainId: 42161,
    rpcUrl: import.meta.env.VITE_ARBITRUM_RPC_URL,
    explorer: 'https://arbiscan.io'
  },
  optimism: {
    name: 'Optimism',
    chainId: 10,
    rpcUrl: import.meta.env.VITE_OPTIMISM_RPC_URL,
    explorer: 'https://optimistic.etherscan.io'
  },
  polygon: {
    name: 'Polygon',
    chainId: 137,
    rpcUrl: import.meta.env.VITE_POLYGON_RPC_URL,
    explorer: 'https://polygonscan.com'
  }
} as const;

export const TRADING_CONFIG = {
  minProfitPercent: 0.5,
  maxSlippagePercent: 0.1,
  maxPositionSize: 0.1, // Max 0.1 ETH per trade
  stopLossPercent: 1.0,
  refreshInterval: 5000, // 5 seconds
  reconnectAttempts: 5,
  reconnectInterval: 5000
} as const;