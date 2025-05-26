// Risk profile types 
export type RiskProfile = 'conservative' | 'moderate' | 'aggressive' | 'low' | 'high';

// Market condition types
export type MarketCondition = 'bull' | 'bear' | 'stable' | 'volatile' | 'normal' | 'opportunity';

// Trading timeframe types
export type TimeFrame = 'short' | 'medium' | 'long';

// Trading execution timeframe
export type ExecutionTimeframe = 'immediate' | 'delayed' | 'standard';

// Trading action types
export type TradingAction = 
  | 'buy' 
  | 'sell' 
  | 'swap' 
  | 'stake' 
  | 'unstake' 
  | 'provide_liquidity' 
  | 'remove_liquidity' 
  | 'borrow'
  | 'repay'
  | 'cross_chain_arbitrage'
  | 'accumulate'
  | 'distribute'
  | 'yield_farm'
  | 'arbitrage';

// Trading strategy interface
export interface TradingStrategy {
  id: string;
  name: string;
  description: string;
  confidence: number;
  riskLevel: 'low' | 'moderate' | 'high';
  expectedReturn: number;
  timeframe: TimeFrame;
  networks: string[];
  tokens: string[];
  action: TradingAction;
  marketCondition: MarketCondition;
  reasoning: string;
}

// Trade decision interface
export interface TradeDecision {
  shouldExecute: boolean;
  confidence: number;
  reasoning: string;
  timeframe: ExecutionTimeframe;
  expectedProfitPercentage: number;
}