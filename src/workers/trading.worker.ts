// This is a web worker file that handles heavy computations
let isProcessing = false;

self.onmessage = async (e) => {
  if (isProcessing) return;
  
  const { type, data } = e.data;
  isProcessing = true;

  try {
    switch (type) {
      case 'analyze_market_data':
        const result = await analyzeMarketData(data);
        self.postMessage({ type: 'analysis_complete', data: result });
        break;

      case 'calculate_arbitrage':
        const opportunities = await calculateArbitrageOpportunities(data);
        self.postMessage({ type: 'arbitrage_complete', data: opportunities });
        break;

      case 'risk_assessment':
        const riskMetrics = await calculateRiskMetrics(data);
        self.postMessage({ type: 'risk_complete', data: riskMetrics });
        break;
    }
  } catch (error) {
    self.postMessage({ 
      type: 'error', 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    });
  } finally {
    isProcessing = false;
  }
};

async function analyzeMarketData(data) {
  // Simulate heavy computation
  const trends = data.prices.map(pricePoint => ({
    timestamp: pricePoint.timestamp,
    trend: calculateTrend(pricePoint.values),
    volatility: calculateVolatility(pricePoint.values),
    momentum: calculateMomentum(pricePoint.values)
  }));

  return {
    trends,
    summary: aggregateAnalysis(trends)
  };
}

async function calculateArbitrageOpportunities(data) {
  // Simulate complex arbitrage calculations
  const opportunities = data.pairs.map(pair => ({
    pair,
    profit: calculatePotentialProfit(pair, data.prices),
    risk: assessTradeRisk(pair, data.prices),
    confidence: calculateConfidence(pair, data.prices)
  }));

  return opportunities.filter(opp => opp.profit > 0 && opp.confidence > 0.7);
}

async function calculateRiskMetrics(data) {
  // Simulate risk calculations
  return {
    overallRisk: calculateOverallRisk(data),
    metrics: {
      volatility: calculateVolatilityRisk(data),
      exposure: calculateExposureRisk(data),
      concentration: calculateConcentrationRisk(data)
    }
  };
}

// Helper functions
function calculateTrend(values) {
  // Simple moving average implementation
  const sum = values.reduce((acc, val) => acc + val, 0);
  return sum / values.length;
}

function calculateVolatility(values) {
  const mean = calculateTrend(values);
  const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
  return Math.sqrt(squaredDiffs.reduce((acc, val) => acc + val, 0) / values.length);
}

function calculateMomentum(values) {
  if (values.length < 2) return 0;
  return (values[values.length - 1] - values[0]) / values[0];
}

function calculatePotentialProfit(pair, prices) {
  // Simple profit calculation
  const buyPrice = Math.min(...prices[pair]);
  const sellPrice = Math.max(...prices[pair]);
  return (sellPrice - buyPrice) / buyPrice;
}

function assessTradeRisk(pair, prices) {
  return calculateVolatility(prices[pair]);
}

function calculateConfidence(pair, prices) {
  const volatility = calculateVolatility(prices[pair]);
  const momentum = calculateMomentum(prices[pair]);
  return Math.max(0, Math.min(1, 1 - volatility + momentum));
}

function aggregateAnalysis(trends) {
  const avgTrend = trends.reduce((acc, t) => acc + t.trend, 0) / trends.length;
  const avgVolatility = trends.reduce((acc, t) => acc + t.volatility, 0) / trends.length;
  const avgMomentum = trends.reduce((acc, t) => acc + t.momentum, 0) / trends.length;

  return {
    trend: avgTrend,
    volatility: avgVolatility,
    momentum: avgMomentum
  };
}

function calculateOverallRisk(data) {
  const risks = [
    calculateVolatilityRisk(data),
    calculateExposureRisk(data),
    calculateConcentrationRisk(data)
  ];
  return risks.reduce((acc, risk) => acc + risk, 0) / risks.length;
}

function calculateVolatilityRisk(data) {
  return Math.min(1, calculateVolatility(data.prices) / 0.1);
}

function calculateExposureRisk(data) {
  return Math.min(1, data.exposure / data.totalPortfolioValue);
}

function calculateConcentrationRisk(data) {
  const maxAllocation = Math.max(...data.allocations);
  return Math.min(1, maxAllocation / 0.5);
}