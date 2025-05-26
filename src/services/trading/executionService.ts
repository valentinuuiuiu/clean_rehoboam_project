// Trading execution service for interacting with blockchain

export interface Position {
  id: string;
  symbol: string;
  amount: number;
  entryPrice: number;
  currentPrice?: number;
  pnl?: number;
  timestamp: number;
  network: string;
  status: 'open' | 'closed' | 'pending';
}

export interface TradeResult {
  success: boolean;
  transactionHash?: string;
  executedPrice: number;
  amount: number;
  fee: number;
  timestamp: number;
  error?: string;
}

class TradingExecutionService {
  private positions: Position[] = [];
  private transactionHistory: any[] = [];
  private currentMarketPrices: Record<string, number> = {
    'ETH': 3000,
    'BTC': 50000,
    'LINK': 20,
    'UMA': 10,
    'AAVE': 200,
    'SHIB': 0.00005
  };

  constructor() {
    // Simulate having a few open positions
    this.positions = [
      {
        id: '1',
        symbol: 'ETH',
        amount: 2.5,
        entryPrice: 2800,
        timestamp: Date.now() - 86400000, // 1 day ago
        network: 'ethereum',
        status: 'open'
      },
      {
        id: '2',
        symbol: 'BTC',
        amount: 0.1,
        entryPrice: 48000,
        timestamp: Date.now() - 172800000, // 2 days ago
        network: 'ethereum',
        status: 'open'
      }
    ];
    
    // Update current prices and PnL for positions
    this.updatePositionPrices();
  }

  /**
   * Get all open positions
   */
  public getPositions(): Position[] {
    this.updatePositionPrices();
    return this.positions;
  }

  /**
   * Get transaction history
   */
  public getTransactionHistory(): any[] {
    return this.transactionHistory;
  }

  /**
   * Execute a trade
   */
  public async executeTrade(
    symbol: string,
    amount: number,
    side: 'buy' | 'sell',
    network: string = 'ethereum'
  ): Promise<TradeResult> {
    try {
      // Get current price (simulated)
      const currentPrice = this.currentMarketPrices[symbol] || 0;
      if (currentPrice === 0) {
        throw new Error(`No price available for ${symbol}`);
      }

      // Apply small slippage to simulate real trading
      const slippage = side === 'buy' ? 0.005 : -0.005; // 0.5% slippage
      const executedPrice = currentPrice * (1 + slippage);
      
      // Calculate fee (simulated)
      const fee = amount * executedPrice * 0.001; // 0.1% fee
      
      // For a sell, check if we have enough balance
      if (side === 'sell') {
        const totalHolding = this.positions
          .filter(p => p.symbol === symbol && p.status === 'open')
          .reduce((total, pos) => total + pos.amount, 0);
          
        if (totalHolding < amount) {
          throw new Error(`Insufficient balance: have ${totalHolding} ${symbol}, trying to sell ${amount}`);
        }
      }
      
      // Create a new position for buys
      if (side === 'buy') {
        const newPosition: Position = {
          id: Date.now().toString(),
          symbol,
          amount,
          entryPrice: executedPrice,
          currentPrice: executedPrice,
          pnl: 0,
          timestamp: Date.now(),
          network,
          status: 'open'
        };
        
        this.positions.push(newPosition);
      } 
      // For sells, reduce existing positions
      else {
        let remainingToSell = amount;
        
        // Sort positions by entry price (highest first for FIFO selling)
        const sortedPositions = [...this.positions]
          .filter(p => p.symbol === symbol && p.status === 'open')
          .sort((a, b) => a.timestamp - b.timestamp);
          
        for (const position of sortedPositions) {
          if (remainingToSell <= 0) break;
          
          if (position.amount <= remainingToSell) {
            // Close this position completely
            position.status = 'closed';
            remainingToSell -= position.amount;
          } else {
            // Partially close position
            position.amount -= remainingToSell;
            remainingToSell = 0;
          }
        }
      }
      
      // Record the transaction
      const transaction = {
        symbol,
        amount,
        price: executedPrice,
        side,
        fee,
        network,
        timestamp: Date.now()
      };
      
      this.transactionHistory.push(transaction);
      
      return {
        success: true,
        executedPrice,
        amount,
        fee,
        timestamp: Date.now(),
        transactionHash: `0x${Math.random().toString(16).substring(2)}` // Fake transaction hash
      };
    } catch (error) {
      console.error(`Trade execution error:`, error);
      return {
        success: false,
        executedPrice: 0,
        amount: 0,
        fee: 0,
        timestamp: Date.now(),
        error: error.message
      };
    }
  }
  
  /**
   * Execute a trade on Layer 2 network
   */
  public async executeLayer2Trade(
    symbol: string,
    amount: number,
    side: 'buy' | 'sell',
    network: string
  ): Promise<TradeResult> {
    // Layer 2 specific logic would go here
    // For now, we'll just call the normal execute trade
    return this.executeTrade(symbol, amount, side, network);
  }

  /**
   * Bridge tokens between networks
   */
  public async bridgeTokens(
    symbol: string,
    amount: number,
    fromNetwork: string,
    toNetwork: string
  ): Promise<any> {
    try {
      // Verify we have enough funds on the source network
      const availableAmount = this.positions
        .filter(p => p.symbol === symbol && p.network === fromNetwork && p.status === 'open')
        .reduce((total, pos) => total + pos.amount, 0);
        
      if (availableAmount < amount) {
        throw new Error(`Insufficient balance on ${fromNetwork}: have ${availableAmount} ${symbol}, trying to bridge ${amount}`);
      }
      
      // Create a record for tokens leaving the source network
      const bridgeOutTx = {
        symbol,
        amount: -amount,
        network: fromNetwork,
        relatedNetwork: toNetwork,
        type: 'bridge_out',
        timestamp: Date.now()
      };
      
      // Create a record for tokens arriving on the destination network
      const bridgeInTx = {
        symbol,
        amount: amount * 0.995, // 0.5% fee for bridging
        network: toNetwork,
        relatedNetwork: fromNetwork,
        type: 'bridge_in',
        timestamp: Date.now() + 60000 // 1 minute later (simulated bridge time)
      };
      
      this.transactionHistory.push(bridgeOutTx);
      this.transactionHistory.push(bridgeInTx);
      
      // Reduce the amount on source network
      let remainingToMove = amount;
      const sourcePositions = [...this.positions]
        .filter(p => p.symbol === symbol && p.network === fromNetwork && p.status === 'open')
        .sort((a, b) => a.timestamp - b.timestamp);
        
      for (const position of sourcePositions) {
        if (remainingToMove <= 0) break;
        
        if (position.amount <= remainingToMove) {
          // Use this position completely
          position.status = 'closed';
          remainingToMove -= position.amount;
        } else {
          // Use this position partially
          position.amount -= remainingToMove;
          remainingToMove = 0;
        }
      }
      
      // Create new position on destination network
      const newPosition: Position = {
        id: Date.now().toString(),
        symbol,
        amount: amount * 0.995, // 0.5% fee
        entryPrice: this.currentMarketPrices[symbol] || 0,
        currentPrice: this.currentMarketPrices[symbol] || 0,
        pnl: 0,
        timestamp: Date.now() + 60000, // 1 minute later (simulated bridge time)
        network: toNetwork,
        status: 'open'
      };
      
      this.positions.push(newPosition);
      
      return {
        success: true,
        fromNetwork,
        toNetwork,
        symbol,
        sentAmount: amount,
        receivedAmount: amount * 0.995,
        fee: amount * 0.005,
        estimatedTimeMs: 60000 // 1 minute
      };
      
    } catch (error) {
      console.error(`Bridge execution error:`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Update prices for all positions
   */
  private updatePositionPrices(): void {
    this.positions.forEach(position => {
      if (position.status === 'open') {
        const currentPrice = this.currentMarketPrices[position.symbol] || 0;
        if (currentPrice > 0) {
          position.currentPrice = currentPrice;
          position.pnl = (currentPrice - position.entryPrice) * position.amount;
        }
      }
    });
  }
}

export const tradingExecutionService = new TradingExecutionService();
