// Trading configuration constants
export const TRADING_PAIRS = [
  'BTCUSDT',   // Bitcoin
  'ETHUSDT',   // Ethereum
  'LINKUSDT',  // Chainlink
  'UMAUSDT',   // UMA
  'MANAUSDT',  // Decentraland
  'SHIBUSDT',  // Shiba Inu
  'AAVEUSDT',  // Aave
  'XMRUSDT',   // Monero
  'EAIUSDT'    // Eternal AI
];

export const DISPLAY_PAIRS = [
  {
    id: 'BTCUSDT',
    name: 'BTC/USDT',
    symbol: 'BTCUSDT',
    baseAsset: 'BTC',
    quoteAsset: 'USDT',
    description: 'Bitcoin'
  },
  {
    id: 'ETHUSDT',
    name: 'ETH/USDT',
    symbol: 'ETHUSDT',
    baseAsset: 'ETH',
    quoteAsset: 'USDT',
    description: 'Ethereum'
  },
  {
    id: 'LINKUSDT',
    name: 'LINK/USDT',
    symbol: 'LINKUSDT',
    baseAsset: 'LINK',
    quoteAsset: 'USDT',
    description: 'Chainlink'
  },
  {
    id: 'UMAUSDT',
    name: 'UMA/USDT',
    symbol: 'UMAUSDT',
    baseAsset: 'UMA',
    quoteAsset: 'USDT',
    description: 'UMA Protocol'
  },
  {
    id: 'MANAUSDT',
    name: 'MANA/USDT',
    symbol: 'MANAUSDT',
    baseAsset: 'MANA',
    quoteAsset: 'USDT',
    description: 'Decentraland'
  },
  {
    id: 'SHIBUSDT',
    name: 'SHIB/USDT',
    symbol: 'SHIBUSDT',
    baseAsset: 'SHIB',
    quoteAsset: 'USDT',
    description: 'Shiba Inu'
  },
  {
    id: 'AAVEUSDT',
    name: 'AAVE/USDT',
    symbol: 'AAVEUSDT',
    baseAsset: 'AAVE',
    quoteAsset: 'USDT',
    description: 'Aave Protocol'
  },
  {
    id: 'XMRUSDT',
    name: 'XMR/USDT',
    symbol: 'XMRUSDT',
    baseAsset: 'XMR',
    quoteAsset: 'USDT',
    description: 'Monero'
  },
  {
    id: 'EAIUSDT',
    name: 'EAI/USDT',
    symbol: 'EAIUSDT',
    baseAsset: 'EAI',
    quoteAsset: 'USDT',
    description: 'Eternal AI'
  },
  {
    id: 'HAIUSDT',
    name: 'HAI/USDT',
    symbol: 'HAIUSDT',
    baseAsset: 'HAI',
    quoteAsset: 'USDT',
    description: 'HackerAI - Network Consciousness Token'
  },
  {
    id: 'MINAUSDT',
    name: 'MINA/USDT',
    symbol: 'MINAUSDT',
    baseAsset: 'MINA',
    quoteAsset: 'USDT',
    description: 'Mina Protocol - Zero Knowledge Blockchain'
  }
];

// WebSocket configuration
export const WS_CONFIG = {
  PING_INTERVAL: 30000,        // Send ping every 30 seconds
  RECONNECT_DELAY: 3000,       // Initial reconnect delay of 3 seconds
  MAX_RECONNECT_ATTEMPTS: 5,   // Maximum number of reconnection attempts
  SUBSCRIPTION_ID: 'trading_platform_1'
};

// Formatting helpers
export const formatPrice = (price) => {
  if (!price || typeof price !== 'number') return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: price < 1 ? 8 : 2,  // Show more decimals for low-value coins like SHIB
    maximumFractionDigits: price < 1 ? 8 : 2
  }).format(price);
};

export const formatChange = (change) => {
  if (!change || typeof change !== 'number') return '0.00%';
  return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
};

export const formatVolume = (volume) => {
  if (!volume || typeof volume !== 'number') return '0';
  if (volume >= 1_000_000) return `${(volume / 1_000_000).toFixed(2)}M`;
  if (volume >= 1_000) return `${(volume / 1_000).toFixed(2)}K`;
  return volume.toFixed(2);
};

// Categories for filtering and organization
export const PAIR_CATEGORIES = {
  ALL: TRADING_PAIRS,
  DEFI: ['AAVEUSDT', 'UMAUSDT', 'LINKUSDT'],
  MEME: ['SHIBUSDT'],
  PRIVACY: ['XMRUSDT'],
  MAIN: ['BTCUSDT', 'ETHUSDT']
};