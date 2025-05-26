/**
 * Calculate Relative Strength Index (RSI)
 * @param {Array} prices - Array of price data
 * @param {number} period - RSI period (default 14)
 */
export const calculateRSI = (prices, period = 14) => {
  if (prices.length < period + 1) return null;

  let gains = 0;
  let losses = 0;

  // Calculate initial average gain/loss
  for (let i = 1; i <= period; i++) {
    const change = prices[i] - prices[i - 1];
    if (change >= 0) gains += change;
    else losses -= change;
  }

  gains /= period;
  losses /= period;

  // Calculate RSI using smoothed averages
  for (let i = period + 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1];
    if (change >= 0) {
      gains = (gains * 13 + change) / 14;
      losses = (losses * 13) / 14;
    } else {
      gains = (gains * 13) / 14;
      losses = (losses * 13 - change) / 14;
    }
  }

  const rs = gains / losses;
  return 100 - (100 / (1 + rs));
};

/**
 * Calculate Moving Average Convergence Divergence (MACD)
 * @param {Array} prices - Array of price data
 */
export const calculateMACD = (prices) => {
  if (prices.length < 26) return { macd: null, signal: null, histogram: null };

  const ema12 = calculateEMA(prices, 12);
  const ema26 = calculateEMA(prices, 26);
  const macdLine = ema12 - ema26;
  const signalLine = calculateEMA([...Array(prices.length - 26).fill(macdLine)], 9);
  const histogram = macdLine - signalLine;

  return {
    macd: macdLine,
    signal: signalLine,
    histogram
  };
};

/**
 * Calculate Simple Moving Average (SMA)
 * @param {Array} prices - Array of price data
 * @param {number} period - SMA period
 */
export const calculateSMA = (prices, period) => {
  if (prices.length < period) return null;

  const sum = prices.slice(-period).reduce((a, b) => a + b, 0);
  return sum / period;
};

/**
 * Calculate Exponential Moving Average (EMA)
 * @param {Array} prices - Array of price data
 * @param {number} period - EMA period
 */
export const calculateEMA = (prices, period) => {
  if (prices.length < period) return null;

  const k = 2 / (period + 1);
  let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;

  for (let i = period; i < prices.length; i++) {
    ema = prices[i] * k + ema * (1 - k);
  }

  return ema;
};
