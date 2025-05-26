import { ethers } from 'ethers';
import { TRADING_PAIRS } from '../../config/trading';

interface BinancePrice {
  symbol: string;
  price: string;
  timestamp: number;
}

export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(price);
};

export const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}%`;
};

export const formatVolume = (volume: number): string => {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 2
  }).format(volume);
};

class BinanceService {
  private readonly API_URL = 'https://api.binance.com/api/v3';
  private readonly UPDATE_INTERVAL = 5000; // 5 seconds

  public async getPrices(symbols: string[]): Promise<Record<string, number>> {
    try {
      const response = await fetch(`${this.API_URL}/ticker/price`);
      const prices: BinancePrice[] = await response.json();
      
      return prices.reduce((acc, { symbol, price }) => {
        if (symbols.includes(symbol)) {
          acc[symbol] = parseFloat(price);
        }
        return acc;
      }, {} as Record<string, number>);
    } catch (error) {
      console.error('Error fetching Binance prices:', error);
      return {};
    }
  }

  public async getMarketData(symbol: string) {
    try {
      const response = await fetch(`${this.API_URL}/ticker/24hr?symbol=${symbol}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching market data:', error);
      return null;
    }
  }

  public subscribeToTicker(symbol: string, callback: (price: number) => void): () => void {
    const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@ticker`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(parseFloat(data.c)); // Current price
    };

    return () => ws.close();
  }
}

export const binanceService = new BinanceService();