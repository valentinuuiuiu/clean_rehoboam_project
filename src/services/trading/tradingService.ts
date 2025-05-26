import { TRADING_PAIRS } from '../../config/trading';
import { ethers } from 'ethers';
import { useWeb3 } from '../../contexts/Web3Context';

export interface Position {
  pair: string;
  side: 'buy' | 'sell';
  amount: number;
  entryPrice: number;
  currentPrice: number;
  profitLoss: number;
  timestamp: number;
}

export interface Balance {
  asset: string;
  free: number;
  locked: number;
}

class TradingService {
  private positions: Position[] = [];
  private balances: Map<string, Balance> = new Map();
  private minProfitPercent = 0.5; // Minimum 0.5% profit target
  private maxSlippagePercent = 0.1; // Maximum 0.1% slippage allowed
  private tradingEnabled = false;

  constructor() {
    this.initializeBalances();
  }

  private initializeBalances() {
    TRADING_PAIRS.forEach(pair => {
      const asset = pair.replace('USDT', '');
      this.balances.set(asset, { asset, free: 0, locked: 0 });
    });
  }

  public async deposit(asset: string, amount: number): Promise<boolean> {
    try {
      const balance = this.balances.get(asset);
      if (!balance) return false;

      balance.free += amount;
      return true;
    } catch (error) {
      console.error('Deposit error:', error);
      return false;
    }
  }

  public async executeTrade(pair: string, side: 'buy' | 'sell', amount: number): Promise<boolean> {
    try {
      const executionPrice = side === 'buy' ? amount * 1.001 : amount * 0.999;
      this.positions.push({
        pair,
        side,
        amount,
        entryPrice: executionPrice,
        currentPrice: executionPrice,
        profitLoss: 0,
        timestamp: Date.now()
      });
      console.log(`Successfully executed ${side} trade for ${amount} ${pair} at ${executionPrice}`);
      return true;
    } catch (error) {
      console.error('Trade execution failed:', error);
      return false;
    }
  }

  public getBalance(asset: string): Balance | null {
    return this.balances.get(asset) || null;
  }

  public getAllPositions(): Position[] {
    return [...this.positions];
  }

  public enableTrading(): void {
    this.tradingEnabled = true;
    console.log('Trading enabled');
  }

  public disableTrading(): void {
    this.tradingEnabled = false;
    console.log('Trading disabled');
  }
}

export const tradingService = new TradingService();