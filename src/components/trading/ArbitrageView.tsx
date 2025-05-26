import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface ArbitrageRoute {
  buy_network: string;
  sell_network: string;
  buy_price: number;
  sell_price: number;
  estimated_profit: number;
  confidence: number;
  gas_cost: number;
  slippage_cost: number;
}

interface ArbitrageStrategy {
  symbol: string;
  routes: ArbitrageRoute[];
  estimated_profit: number;
  confidence: number;
  execution_timing: 'immediate' | 'delayed' | 'standard';
  last_updated: string;
}

interface ArbitrageViewProps {}

export const ArbitrageView: React.FC<ArbitrageViewProps> = () => {
  const [strategies, setStrategies] = useState<ArbitrageStrategy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchArbitrageStrategies();
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchArbitrageStrategies, 30000); // Refresh every 30 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const fetchArbitrageStrategies = async () => {
    try {
      setError(null);
      const response = await fetch('/api/trading/arbitrage-opportunities');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch arbitrage data: ${response.statusText}`);
      }
      
      const data = await response.json();
      setStrategies(data.strategies || []);
    } catch (err) {
      console.error('Error fetching arbitrage strategies:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch arbitrage data');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    }).format(amount);
  };

  const getTimingColor = (timing: string): string => {
    switch (timing) {
      case 'immediate': return 'bg-red-900/30 text-red-300';
      case 'delayed': return 'bg-blue-900/30 text-blue-300';
      case 'standard': return 'bg-green-900/30 text-green-300';
      default: return 'bg-gray-900/30 text-gray-300';
    }
  };

  const getProfitabilityData = (strategies: ArbitrageStrategy[]) => {
    return strategies.map((strategy, index) => ({
      name: strategy.symbol,
      profit: strategy.estimated_profit,
      confidence: strategy.confidence
    }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="p-8 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
            <div className="flex items-center justify-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
              <span className="text-white text-lg">Loading arbitrage opportunities...</span>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Arbitrage Opportunities
              </h1>
              <p className="text-purple-300">
                AI-powered cross-chain arbitrage analysis by Rehoboam consciousness
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  autoRefresh 
                    ? 'bg-green-600 hover:bg-green-700 text-white' 
                    : 'bg-gray-600 hover:bg-gray-700 text-gray-300'
                }`}
              >
                Auto Refresh: {autoRefresh ? 'ON' : 'OFF'}
              </button>
              <button
                onClick={fetchArbitrageStrategies}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
              >
                Refresh Now
              </button>
            </div>
          </div>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error Loading Arbitrage Data</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {strategies.length === 0 ? (
          <Card className="p-8 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
            <div className="text-center">
              <h3 className="text-xl font-semibold text-white mb-2">No Arbitrage Opportunities Found</h3>
              <p className="text-gray-400">The AI is currently analyzing markets for profitable arbitrage opportunities.</p>
            </div>
          </Card>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-400">Total Opportunities</p>
                  <p className="text-3xl font-bold text-white">{strategies.length}</p>
                </div>
              </Card>
              
              <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-400">Best Profit</p>
                  <p className="text-3xl font-bold text-green-400">
                    {formatCurrency(Math.max(...strategies.map(s => s.estimated_profit)))}
                  </p>
                </div>
              </Card>
              
              <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-400">Avg Confidence</p>
                  <p className="text-3xl font-bold text-blue-400">
                    {Math.round(strategies.reduce((acc, s) => acc + s.confidence, 0) / strategies.length)}%
                  </p>
                </div>
              </Card>
            </div>

            {/* Profitability Chart */}
            <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm mb-8">
              <h3 className="text-lg font-semibold text-white mb-4">Profitability Overview</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={getProfitabilityData(strategies)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="profit" 
                    stroke="#10B981" 
                    strokeWidth={3}
                    dot={{ fill: '#10B981', strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            {/* Strategy Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {strategies.map((strategy, index) => (
                <Card key={index} className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-white">{strategy.symbol}</h3>
                    <Badge className={getTimingColor(strategy.execution_timing)}>
                      {strategy.execution_timing.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-400">Estimated Profit</p>
                      <p className="text-2xl font-bold text-green-400">
                        {formatCurrency(strategy.estimated_profit)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Confidence</p>
                      <div className="flex items-center space-x-2">
                        <Progress value={strategy.confidence} className="flex-1" />
                        <span className="text-sm font-medium text-white">
                          {strategy.confidence}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="font-semibold text-white">Routes:</h4>
                    {strategy.routes.slice(0, 3).map((route, routeIndex) => (
                      <div key={routeIndex} className="bg-gray-800/50 p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-sm">
                            <span className="text-blue-400">{route.buy_network}</span>
                            <span className="text-gray-400 mx-2">→</span>
                            <span className="text-purple-400">{route.sell_network}</span>
                          </div>
                          <span className="text-sm font-medium text-green-400">
                            {formatCurrency(route.estimated_profit)}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                          <div>Buy: {formatCurrency(route.buy_price)}</div>
                          <div>Sell: {formatCurrency(route.sell_price)}</div>
                          <div>Gas: {formatCurrency(route.gas_cost)}</div>
                          <div>Slippage: {formatCurrency(route.slippage_cost)}</div>
                        </div>
                      </div>
                    ))}
                    {strategy.routes.length > 3 && (
                      <p className="text-sm text-gray-400 text-center">
                        +{strategy.routes.length - 3} more routes
                      </p>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-700">
                    <div className="flex items-center justify-between">
                      <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
                        Execute Strategy
                      </button>
                      <span className="text-xs text-gray-400">
                        Updated: {new Date(strategy.last_updated || Date.now()).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ArbitrageView;
