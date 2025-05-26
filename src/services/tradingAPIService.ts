// Trading API Service with Infura Integration
import { ethers, JsonRpcProvider } from 'ethers';

export interface TradingExecutionRequest {
  token: string;
  amount: number;
  action: 'buy' | 'sell';
  network: string;
  slippage?: number;
}

export interface TradingExecutionResult {
  success: boolean;
  txHash?: string;
  message: string;
  gasUsed?: string;
  gasPrice?: string;
  networkUsed?: string;
}

export interface NetworkRecommendation {
  recommendedNetwork: string;
  gasEstimate: string;
  reason: string;
  alternatives: Array<{
    network: string;
    gasEstimate: string;
    score: number;
  }>;
}

class TradingAPIService {
  private infuraProvider: JsonRpcProvider | null = null;
  private readonly API_BASE = '/api';

  constructor() {
    this.initializeInfuraProvider();
  }

  private initializeInfuraProvider() {
    const infuraKey = import.meta.env.VITE_INFURA_API_KEY || 'ddd78bc17de648b2a89acf424fbfa8ed';
    if (infuraKey) {
      this.infuraProvider = new JsonRpcProvider(`https://mainnet.infura.io/v3/${infuraKey}`);
    }
  }

  // Execute trading strategy
  async executeTradingStrategy(request: TradingExecutionRequest): Promise<TradingExecutionResult> {
    try {
      const response = await fetch(`${this.API_BASE}/trading/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (error: any) {
      console.error('Trading execution error:', error);
      return {
        success: false,
        message: error.message || 'Trading execution failed'
      };
    }
  }

  // Get trading strategies from backend
  async getTradingStrategies(token: string = 'ETH', riskProfile: string = 'moderate') {
    try {
      const response = await fetch(`${this.API_BASE}/trading/strategies?token=${token}&risk_profile=${riskProfile}`);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const data = await response.json();
      return data.strategies || [];
    } catch (error) {
      console.error('Error fetching strategies:', error);
      throw error;
    }
  }

  // Get network recommendation using Infura data
  async getNetworkRecommendation(token: string, action: string, amount: number): Promise<NetworkRecommendation> {
    try {
      // Get gas prices using Infura
      let gasPrice = '20'; // Default fallback
      if (this.infuraProvider) {
        try {
          const feeData = await this.infuraProvider.getFeeData();
          if (feeData.gasPrice) {
            gasPrice = ethers.formatUnits(feeData.gasPrice, 'gwei');
          }
        } catch (error) {
          console.warn('Could not fetch gas price from Infura:', error);
        }
      }

      const response = await fetch(`${this.API_BASE}/optimizer/network?token=${token}&transaction_type=${action}&amount=${amount}`);
      
      if (!response.ok) {
        // Fallback recommendation
        return this.getFallbackNetworkRecommendation(token, gasPrice);
      }

      const data = await response.json();
      return {
        recommendedNetwork: data.recommended_network || 'arbitrum',
        gasEstimate: data.gas_estimate || `${gasPrice} gwei`,
        reason: data.reasoning || 'Lower fees and faster execution',
        alternatives: data.alternatives || []
      };
    } catch (error) {
      console.error('Error getting network recommendation:', error);
      return this.getFallbackNetworkRecommendation(token, '20');
    }
  }

  private getFallbackNetworkRecommendation(token: string, gasPrice: string): NetworkRecommendation {
    const networkMap: Record<string, string> = {
      'ETH': 'arbitrum',
      'BTC': 'optimism', 
      'LINK': 'base',
      'USDC': 'polygon',
      'UMA': 'arbitrum'
    };

    return {
      recommendedNetwork: networkMap[token] || 'arbitrum',
      gasEstimate: gasPrice + ' gwei',
      reason: 'Optimized for lower fees and faster execution',
      alternatives: [
        { network: 'arbitrum', gasEstimate: '0.5 gwei', score: 0.95 },
        { network: 'optimism', gasEstimate: '0.8 gwei', score: 0.90 },
        { network: 'base', gasEstimate: '0.3 gwei', score: 0.88 }
      ]
    };
  }

  // Get market analysis
  async getMarketAnalysis(token: string) {
    try {
      const response = await fetch(`${this.API_BASE}/market/analysis?token=${token}`);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching market analysis:', error);
      throw error;
    }
  }

  // Get arbitrage opportunities
  async getArbitrageOpportunities(token: string = 'ETH') {
    try {
      const response = await fetch(`${this.API_BASE}/arbitrage/opportunities?token=${token}`);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching arbitrage opportunities:', error);
      throw error;
    }
  }

  // Buy/Sell tokens
  async executeTrade(token: string, amount: number, action: 'buy' | 'sell', network: string = 'ethereum') {
    const request: TradingExecutionRequest = {
      token,
      amount,
      action,
      network,
      slippage: 1.0 // 1% default slippage
    };

    return this.executeTradingStrategy(request);
  }

  // Get current ETH price using Infura
  async getETHPrice(): Promise<number> {
    try {
      if (this.infuraProvider) {
        // This is a simple example - in production you'd use a price oracle
        return 3000; // Fallback price
      }
      return 3000;
    } catch (error) {
      console.error('Error fetching ETH price:', error);
      return 3000;
    }
  }

  // Get gas prices across networks
  async getGasPrices() {
    try {
      const response = await fetch(`${this.API_BASE}/gas/prices`);
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching gas prices:', error);
      throw error;
    }
  }
}

export const tradingAPIService = new TradingAPIService();
