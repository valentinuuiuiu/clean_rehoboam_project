import { TRADING_PAIRS } from '../config/trading';
import { arbitrageService } from './arbitrageService';

export interface TradingPosition {
  pair: string;
  entryPrice: number;
  amount: number;
  side: 'buy' | 'sell';
  timestamp: number;
}

export interface WalletBalance {
  asset: string;
  free: number;
  locked: number;
}

class TradingService {
  private positions: TradingPosition[] = [];
  private balances: Map<string, WalletBalance> = new Map();
  private minProfitPercent = 0.5; // Minimum 0.5% profit target
  private maxSlippagePercent = 0.1; // Maximum 0.1% slippage allowed
  private tradingEnabled = false;

  constructor() {
    this.initializeBalances();
  }

  private initializeBalances() {
    // Initialize with zero balances for all trading pairs
    TRADING_PAIRS.forEach(pair => {
      const baseAsset = pair.replace('USDT', '');
      this.balances.set(baseAsset, {
        asset: baseAsset,
        free: 0,
        locked: 0
      });
    });
    
    // Initialize USDT balance
    this.balances.set('USDT', {
      asset: 'USDT',
      free: 0,
      locked: 0
    });
  }

  public async deposit(asset: string, amount: number): Promise<boolean> {
    const balance = this.balances.get(asset);
    if (!balance) {
      console.error(`Asset ${asset} not supported`);
      return false;
    }

    // Update free balance
    this.balances.set(asset, {
      ...balance,
      free: balance.free + amount
    });

    console.log(`Deposited ${amount} ${asset}`);
    return true;
  }

  public async executeTrade(pair: string, side: 'buy' | 'sell', amount: number): Promise<boolean> {
    try {
      // Safety checks
      if (!this.tradingEnabled) {
        console.error('Trading is currently disabled');
        return false;
      }

      const [baseAsset, quoteAsset] = this.splitPair(pair);
      const balance = side === 'buy' ? 
        this.balances.get(quoteAsset) :
        this.balances.get(baseAsset);

      if (!balance || balance.free < amount) {
        console.error(`Insufficient ${side === 'buy' ? quoteAsset : baseAsset} balance`);
        return false;
      }

      // Check current market conditions
      const opportunities = await arbitrageService.findArbitrageOpportunities();
      const bestOpportunity = opportunities.find(opp => opp.symbol === pair);

      if (!bestOpportunity || bestOpportunity.estimated_profit < this.minProfitPercent) {
        console.log('No profitable opportunities found');
        return false;
      }

      // Execute the trade with safety checks
      const executionPrice = side === 'buy' ? 
        bestOpportunity.routes[0].buy_price :
        bestOpportunity.routes[0].sell_price;

      // Update balances
      if (side === 'buy') {
        // Lock quote asset (e.g., USDT)
        const quoteBalance = this.balances.get(quoteAsset)!;
        this.balances.set(quoteAsset, {
          ...quoteBalance,
          free: quoteBalance.free - amount,
          locked: quoteBalance.locked + amount
        });

        // Add base asset after successful trade
        const baseBalance = this.balances.get(baseAsset)!;
        const receivedAmount = amount / executionPrice * (1 - this.maxSlippagePercent/100);
        this.balances.set(baseAsset, {
          ...baseBalance,
          free: baseBalance.free + receivedAmount
        });
      } else {
        // Lock base asset
        const baseBalance = this.balances.get(baseAsset)!;
        this.balances.set(baseAsset, {
          ...baseBalance,
          free: baseBalance.free - amount,
          locked: baseBalance.locked + amount
        });

        // Add quote asset after successful trade
        const quoteBalance = this.balances.get(quoteAsset)!;
        const receivedAmount = amount * executionPrice * (1 - this.maxSlippagePercent/100);
        this.balances.set(quoteAsset, {
          ...quoteBalance,
          free: quoteBalance.free + receivedAmount
        });
      }

      // Record the position
      this.positions.push({
        pair,
        entryPrice: executionPrice,
        amount,
        side,
        timestamp: Date.now()
      });

      console.log(`Successfully executed ${side} trade for ${amount} ${pair} at ${executionPrice}`);
      return true;
    } catch (error) {
      console.error('Trade execution failed:', error);
      return false;
    }
  }

  public getBalance(asset: string): WalletBalance | null {
    return this.balances.get(asset) || null;
  }

  public getAllPositions(): TradingPosition[] {
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

  private splitPair(pair: string): [string, string] {
    const baseAsset = pair.replace('USDT', '');
    return [baseAsset, 'USDT'];
  }
}

export const tradingService = new TradingService();
