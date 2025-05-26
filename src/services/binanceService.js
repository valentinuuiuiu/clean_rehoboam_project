import { useState, useEffect } from 'react';
import { TRADING_PAIRS } from '../config/trading';

// Cache configuration
const CACHE_DURATION = 30000; // 30 seconds
const priceCache = new Map();
const SCREENSHOT_INTERVAL = 300000; // Take screenshots every 5 minutes
const MAX_RETRIES = 3;

// API configuration
const API_ENDPOINTS = {
  coingecko: {
    url: 'https://api.coingecko.com/api/v3/simple/price',
    rateLimit: 50 // requests per minute
  },
  binance: {
    url: 'https://api.binance.com/api/v3/ticker/price',
    rateLimit: 1200
  },
  etherscan: {
    url: 'https://api.etherscan.io/api',
    rateLimit: 100000, // 100k calls per day
    dailyResetTime: new Date().setHours(0, 0, 0, 0), // Reset at midnight
    currentCalls: 0
  }
};

// Rate limiting tracker
const rateLimits = new Map();
let lastEtherscanReset = new Date().setHours(0, 0, 0, 0);

const isRateLimited = (endpoint) => {
  const limit = rateLimits.get(endpoint);
  if (!limit) return false;

  // Special handling for Etherscan daily limit
  if (endpoint === 'etherscan') {
    const now = Date.now();
    // Reset counter if it's a new day
    if (now > lastEtherscanReset + 86400000) { // 24 hours in milliseconds
      API_ENDPOINTS.etherscan.currentCalls = 0;
      lastEtherscanReset = new Date().setHours(0, 0, 0, 0);
    }
    // Check if we've exceeded daily limit
    if (API_ENDPOINTS.etherscan.currentCalls >= API_ENDPOINTS.etherscan.rateLimit) {
      console.warn('Etherscan daily limit reached');
      return true;
    }
    API_ENDPOINTS.etherscan.currentCalls++;
    return false;
  }

  // Regular rate limiting for other APIs
  return Date.now() - limit.timestamp < (60000 / limit.rate);
};

const updateRateLimit = (endpoint) => {
  const config = API_ENDPOINTS[endpoint];
  rateLimits.set(endpoint, {
    timestamp: Date.now(),
    rate: config.rateLimit
  });
};

// DuckDuckGo price scraping helper
const scrapeDDGPrice = async (symbol) => {
  try {
    const query = `${symbol} price USD`;
    const response = await fetch(`https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json`);

    if (!response.ok) {
      throw new Error('DDG API error');
    }

    const data = await response.json();
    // Extract price from DDG response
    const priceMatch = data.AbstractText.match(/\$[\d,]+\.?\d*/);
    if (priceMatch) {
      return parseFloat(priceMatch[0].replace('$', '').replace(',', ''));
    }
    return null;
  } catch (error) {
    console.error('DDG price fetch error:', error);
    return null;
  }
};

const fetchFromCoingecko = async () => {
  if (isRateLimited('coingecko')) {
    console.warn('CoinGecko rate limit reached, waiting and retrying');
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2s before retry
  }

  const params = new URLSearchParams({
    ids: TRADING_PAIRS.map(pair => pair.toLowerCase().replace('usdt', '')).join(','),
    vs_currencies: 'usd',
    include_24hr_vol: 'true',
    include_24hr_change: 'true'
  });

  const response = await fetch(`${API_ENDPOINTS.coingecko.url}?${params}`);
  updateRateLimit('coingecko');

  if (!response.ok) {
    throw new Error(`CoinGecko error: ${response.status}`);
  }

  const data = await response.json();
  if (!data || Object.keys(data).length === 0) {
    throw new Error('Invalid data from CoinGecko');
  }

  return data;
};

const fetchFromBinance = async (symbol) => {
  if (isRateLimited('binance')) {
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s before retry
  }

  const response = await fetch(`${API_ENDPOINTS.binance.url}?symbol=${symbol}`);
  updateRateLimit('binance');

  if (!response.ok) {
    throw new Error(`Binance error: ${response.status}`);
  }

  const data = await response.json();
  if (!data || !data.price) {
    throw new Error('Invalid data from Binance');
  }

  return data;
};

const fetchFromEtherscan = async (tokenAddress) => {
  if (isRateLimited('etherscan')) {
    throw new Error('Rate limited: Etherscan daily limit reached');
  }

  try {
    const response = await fetch(
      `${API_ENDPOINTS.etherscan.url}?module=stats&action=tokensupply&contractaddress=${tokenAddress}&apikey=${process.env.ETHERSCAN_API_KEY}`
    );
    updateRateLimit('etherscan');

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error('Etherscan rate limit exceeded');
      }
      throw new Error(`Etherscan error: ${response.status}`);
    }

    const data = await response.json();
    if (data.status === '0') {
      throw new Error(`Etherscan API error: ${data.message}`);
    }

    return data;
  } catch (error) {
    console.error('Etherscan fetch error:', error);
    throw error;
  }
};

// Price fetching with improved rate limit handling
const fetchPrices = async () => {
  // Check cache first
  const cachedData = priceCache.get('prices');
  if (isCacheValid(cachedData)) {
    return cachedData.data;
  }

  const prices = {};
  let errors = [];

  // Try CoinGecko first with rate limit aware retry logic
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      if (!isRateLimited('coingecko')) {
        const coingeckoData = await fetchFromCoingecko();
        TRADING_PAIRS.forEach(pair => {
          const baseAsset = pair.replace('USDT', '').toLowerCase();
          const info = coingeckoData[baseAsset];

          if (info) {
            prices[pair] = {
              price: info.usd,
              change24h: info.usd_24h_change || 0,
              volume: info.usd_24h_vol || 0,
              high24h: info.high_24h || info.usd * 1.05,
              low24h: info.low_24h || info.usd * 0.95,
              lastUpdate: Date.now(),
              source: 'coingecko'
            };
          }
        });
        break; // Success, exit retry loop
      } else {
        await new Promise(resolve => setTimeout(resolve, 2000 * attempt)); // Exponential backoff
      }
    } catch (error) {
      console.warn(`CoinGecko attempt ${attempt} failed:`, error);
      errors.push(error);
      if (attempt === MAX_RETRIES) {
        console.error('All CoinGecko attempts failed, falling back to Binance');
      }
    }
  }

  // Fallback to Binance for missing or failed prices
  for (const pair of TRADING_PAIRS) {
    if (!prices[pair] || !prices[pair].price) {
      try {
        if (!isRateLimited('binance')) {
          const binanceData = await fetchFromBinance(pair);
          if (binanceData.price) {
            prices[pair] = {
              price: parseFloat(binanceData.price),
              change24h: 0,
              volume: 0,
              lastUpdate: Date.now(),
              source: 'binance'
            };
          }
        } else {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } catch (error) {
        console.warn(`Binance fetch failed for ${pair}:`, error);
        errors.push(error);
      }
    }
  }

  // Update cache if we have any valid prices
  if (Object.keys(prices).length > 0) {
    priceCache.set('prices', {
      timestamp: Date.now(),
      data: prices
    });
  } else {
    console.error('All price feeds failed:', errors);
    throw new Error('Unable to fetch prices from any source');
  }

  return prices;
};

const captureScreenshot = async (prices) => {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const significantChanges = Object.entries(prices).filter(([_, data]) =>
      Math.abs(data.change24h) >= 5 // Capture when price change >= 5%
    );

    if (significantChanges.length > 0) {
      console.log(`Captured trading snapshot at ${timestamp}`);
      significantChanges.forEach(([pair, data]) => {
        console.log(`${pair}: ${data.change24h}% change, Price: ${data.price}`);
      });
    }
  } catch (error) {
    console.error('Error capturing screenshot:', error);
  }
};

const isCacheValid = (cacheEntry) => {
  return cacheEntry && Date.now() - cacheEntry.timestamp < CACHE_DURATION;
};

export const useBinancePrices = () => {
  const [prices, setPrices] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    let intervalId;
    let screenshotIntervalId;
    let retryCount = 0;

    const updatePrices = async () => {
      if (!mounted) return;

      try {
        setIsLoading(true);
        const data = await fetchPrices();

        if (!mounted) return;

        if (Object.keys(data).length === 0) {
          throw new Error('No price data available');
        }

        setPrices(data);
        setError(null);
        retryCount = 0; // Reset retry count on success
      } catch (err) {
        console.error('Price feed error:', err);
        retryCount++;

        if (retryCount <= MAX_RETRIES) {
          // Exponential backoff for retries
          const delay = Math.min(1000 * Math.pow(2, retryCount), 10000);
          console.log(`Retrying after ${delay}ms (attempt ${retryCount}/${MAX_RETRIES})`);
          setTimeout(updatePrices, delay);
        } else {
          setError('Unable to fetch latest prices');
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    // Initial fetch
    updatePrices();

    // Set up polling for prices
    intervalId = setInterval(updatePrices, CACHE_DURATION);

    // Set up periodic screenshots
    screenshotIntervalId = setInterval(() => {
      if (prices && Object.keys(prices).length > 0) {
        captureScreenshot(prices);
      }
    }, SCREENSHOT_INTERVAL);

    return () => {
      mounted = false;
      if (intervalId) clearInterval(intervalId);
      if (screenshotIntervalId) clearInterval(screenshotIntervalId);
    };
  }, []);

  return {
    prices,
    error,
    isLoading,
    isLive: !error && !isLoading
  };
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

export { TRADING_PAIRS };