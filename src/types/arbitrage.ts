export interface Route {
  path: string[];
  expectedProfit: number;
  confidence: number;
}

export interface ArbitrageStrategy {
  symbol: string;
  routes: Route[];
  profitPotential: number;
  riskLevel: string;
  timestamp: number;
}