import { Position } from './executionService';

export interface RiskMetrics {
  totalExposure: number;          // Total position value in USD
  maxDrawdown: number;            // Maximum historical loss percentage
  volatility: number;             // Price volatility (standard deviation)
  sharpeRatio: number;            // Risk-adjusted return metric
  openPositionsCount: number;     // Number of open positions
}

class RiskAssessmentService {
  private historicalPrices: number[] = [];
  private readonly maxHistoryLength = 100;

  public calculateRiskMetrics(positions: Position[]): RiskMetrics {
    const totalExposure = positions.reduce((sum, pos) => 
      sum + pos.amount * pos.currentPrice, 0);

    const returns = this.calculateReturns();
    const volatility = this.calculateVolatility(returns);
    const sharpeRatio = this.calculateSharpeRatio(returns, volatility);
    
    return {
      totalExposure,
      maxDrawdown: this.calculateMaxDrawdown(positions),
      volatility,
      sharpeRatio,
      openPositionsCount: positions.length
    };
  }

  private calculateReturns(): number[] {
    return this.historicalPrices
      .slice(1)
      .map((price, i) => 
        (price - this.historicalPrices[i]) / this.historicalPrices[i]);
  }

  private calculateVolatility(returns: number[]): number {
    if (returns.length === 0) return 0;
    const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const squaredDiffs = returns.map(r => Math.pow(r - mean, 2));
    return Math.sqrt(squaredDiffs.reduce((sum, d) => sum + d, 0) / returns.length);
  }

  private calculateSharpeRatio(returns: number[], volatility: number): number {
    if (volatility === 0 || returns.length === 0) return 0;
    const meanReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const riskFreeRate = 0.02 / 365; // Assuming 2% annual risk-free rate
    return (meanReturn - riskFreeRate) / volatility;
  }

  private calculateMaxDrawdown(positions: Position[]): number {
    const pnls = positions.map(p => p.profitLoss);
    if (pnls.length === 0) return 0;
    return Math.min(...pnls);
  }

  public updatePriceHistory(price: number) {
    this.historicalPrices.push(price);
    if (this.historicalPrices.length > this.maxHistoryLength) {
      this.historicalPrices.shift();
    }
  }
}

export const riskAssessmentService = new RiskAssessmentService();
