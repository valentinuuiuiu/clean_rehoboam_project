import { TRADING_PAIRS } from './binanceService';
import { ethers } from 'ethers';

export interface ArbitrageRoute {
  buy_network: string;
  sell_network: string;
  buy_price: number;
  sell_price: number;
  estimated_profit: number;
  confidence: number;
  gas_cost: number;
  slippage_cost: number;
}

export interface ArbitrageStrategy {
  symbol: string;
  routes: ArbitrageRoute[];
  estimated_profit: number;
  confidence: number;
  execution_timing: 'immediate' | 'delayed' | 'standard';
  sourceChain: string;
  targetChain: string;
  token: string;
  profitPotential: number;
  gasEstimate: string;
}

const NETWORKS = [
  { id: 'ethereum', name: 'Ethereum', gas_cost: 25 },
  { id: 'arbitrum', name: 'Arbitrum', gas_cost: 2 },
  { id: 'polygon', name: 'Polygon', gas_cost: 0.5 },
  { id: 'avalanche', name: 'Avalanche', gas_cost: 1 }
];

class ArbitrageService {
  private lastPrices: Map<string, { [network: string]: number }> = new Map();
  private volatilityHistory: Map<string, number[]> = new Map();
  private readonly supportedChains = ['ethereum', 'arbitrum', 'optimism', 'polygon'];

  constructor() {
    this.initializePriceHistory();
  }

  private initializePriceHistory() {
    TRADING_PAIRS.forEach(pair => {
      this.lastPrices.set(pair, {});
      this.volatilityHistory.set(pair, []);
    });
  }

  public updatePrice(pair: string, network: string, price: number) {
    const prices = this.lastPrices.get(pair) || {};
    prices[network] = price;
    this.lastPrices.set(pair, prices);

    // Update volatility history
    const history = this.volatilityHistory.get(pair) || [];
    history.push(price);
    if (history.length > 100) history.shift();
    this.volatilityHistory.set(pair, history);
  }

  private calculateVolatility(pair: string): number {
    const history = this.volatilityHistory.get(pair) || [];
    if (history.length < 2) return 0;

    const returns = history.slice(1).map((price, i) => 
      (price - history[i]) / history[i]
    );
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - avgReturn, 2), 0) / returns.length;
    return Math.sqrt(variance);
  }

  private calculateSlippage(volume: number, liquidity: number): number {
    return Math.min(volume / liquidity * 0.01, 0.05);
  }

  public async findArbitrageOpportunities(): Promise<ArbitrageStrategy[]> {
    const opportunities: ArbitrageStrategy[] = [];

    TRADING_PAIRS.forEach(pair => {
      const prices = this.lastPrices.get(pair) || {};
      const volatility = this.calculateVolatility(pair);
      const routes: ArbitrageRoute[] = [];

      // Compare prices across networks
      NETWORKS.forEach(buyNetwork => {
        NETWORKS.forEach(sellNetwork => {
          if (buyNetwork.id === sellNetwork.id) return;

          const buyPrice = prices[buyNetwork.id];
          const sellPrice = prices[sellNetwork.id];

          if (!buyPrice || !sellPrice) return;

          const priceDiff = sellPrice - buyPrice;
          const totalGasCost = buyNetwork.gas_cost + sellNetwork.gas_cost;
          const estimatedVolume = 1000; // Example volume
          const slippageCost = this.calculateSlippage(estimatedVolume, 100000);
          const estimatedProfit = priceDiff - totalGasCost - (slippageCost * sellPrice);

          if (estimatedProfit > 0) {
            routes.push({
              buy_network: buyNetwork.name,
              sell_network: sellNetwork.name,
              buy_price: buyPrice,
              sell_price: sellPrice,
              estimated_profit: estimatedProfit,
              confidence: Math.max(0, 1 - volatility * 2),
              gas_cost: totalGasCost,
              slippage_cost: slippageCost * sellPrice
            });
          }
        });
      });

      if (routes.length > 0) {
        const bestRoute = routes.reduce((a, b) => 
          a.estimated_profit > b.estimated_profit ? a : b
        );

        opportunities.push({
          symbol: pair,
          routes: routes.sort((a, b) => b.estimated_profit - a.estimated_profit),
          estimated_profit: bestRoute.estimated_profit,
          confidence: bestRoute.confidence,
          execution_timing: bestRoute.confidence > 0.8 ? 'immediate' : 
                          bestRoute.confidence > 0.6 ? 'standard' : 'delayed',
          sourceChain: 'ethereum',
          targetChain: 'arbitrum',
          token: 'ETH',
          profitPotential: 0.5,
          gasEstimate: '0.002'
        });
      }
    });

    return opportunities.sort((a, b) => b.estimated_profit - a.estimated_profit);
  }

  public async validateStrategy(strategy: ArbitrageStrategy): Promise<boolean> {
    // Validate if the arbitrage opportunity is still valid
    return strategy.profitPotential > 0.5 && strategy.confidence > 0.7;
  }
}

export const arbitrageService = new ArbitrageService();
