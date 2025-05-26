import path from 'path';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});

export const RiskMetrics = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH'
};

export const riskAssessmentService = {
  calculateRiskScore(tradingData) {
    try {
      // Basic risk scoring algorithm
      const {
        volatility = 0,
        leverage = 1,
        exposure = 0,
        marketCap = 0,
        volume = 0
      } = tradingData;

      const volatilityWeight = 0.3;
      const leverageWeight = 0.25;
      const exposureWeight = 0.2;
      const marketCapWeight = 0.15;
      const volumeWeight = 0.1;

      const riskScore = 
        (volatility * volatilityWeight) +
        (leverage * leverageWeight) +
        (exposure * exposureWeight) +
        (1 / marketCap * marketCapWeight) +
        (1 / volume * volumeWeight);

      return Math.min(Math.max(riskScore, 0), 1);
    } catch (error) {
      console.error('Error calculating risk score:', error);
      return 1; // Return maximum risk on error
    }
  },

  getRiskLevel(score) {
    if (score < 0.3) return RiskMetrics.LOW;
    if (score < 0.7) return RiskMetrics.MEDIUM;
    return RiskMetrics.HIGH;
  },

  getRiskDetails(tradingData) {
    try {
      const riskFactors = [];
      
      if (tradingData.volatility > 0.5) {
        riskFactors.push('High market volatility');
      }
      if (tradingData.leverage > 2) {
        riskFactors.push('High leverage');
      }
      if (tradingData.exposure > 0.4) {
        riskFactors.push('Large position exposure');
      }
      if (tradingData.marketCap < 1000000) {
        riskFactors.push('Low market capitalization');
      }
      if (tradingData.volume < 100000) {
        riskFactors.push('Low trading volume');
      }

      return riskFactors.length > 0 
        ? riskFactors.join(', ')
        : 'No significant risk factors identified';
    } catch (error) {
      return 'Unable to analyze risk details';
    }
  },

  assessPortfolioRisk(positions) {
    try {
      const overallRisk = positions.reduce((acc, position) => {
        const riskScore = this.calculateRiskScore(position);
        return acc + (riskScore * position.weight || 1);
      }, 0) / positions.length;

      return {
        score: overallRisk,
        level: this.getRiskLevel(overallRisk),
        details: this.getRiskDetails(positions[0]) // Example with first position
      };
    } catch (error) {
      console.error('Portfolio risk assessment error:', error);
      return {
        score: 1,
        level: RiskMetrics.HIGH,
        details: 'Error assessing portfolio risk'
      };
    }
  },

  handleError(error) {
    // Convert Error objects to string messages
    if (error instanceof Error) {
      return error.message;
    }
    return String(error);
  },

  assessTradingRisk(tradingData) {
    try {
      // Risk assessment logic
      const riskScore = this.calculateRiskScore(tradingData);
      return {
        level: this.getRiskLevel(riskScore),
        score: riskScore,
        details: this.getRiskDetails(tradingData)
      };
    } catch (error) {
      return {
        level: RiskMetrics.HIGH,
        score: 1,
        details: this.handleError(error)
      };
    }
  }
};