import React from 'react';
import { Card } from "./src/components/ui/card";
import { Progress } from "./src/components/ui/progress";
import { useQuery } from '@tanstack/react-query';
import { formatCurrency } from './src/utils/formatters';
import { ErrorMessage } from './ErrorMessage';
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
}

export const ArbitrageView: React.FC = () => {
  const { data: strategies, isLoading, error, isError } = useQuery<ArbitrageStrategy[]>({
    queryKey: ['arbitrage-strategies'],
    retry: 3,
    staleTime: 30000
  });

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>Loading arbitrage opportunities...</span>
        </div>
      </Card>
    );
  }

  if (isError) {
    return <ErrorMessage error={error instanceof Error ? error : 'Failed to fetch arbitrage strategies'} />;
  }

  if (!strategies?.length) {
    return (
      <Card className="p-6">
        <p className="text-center text-gray-500">No arbitrage opportunities found at this time.</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {strategies.map((strategy, index) => (
        <Card key={`${strategy.symbol}-${index}`} className="p-6">
          <div className="mb-4">
            <h3 className="text-xl font-bold">{strategy.symbol}</h3>
            <div className="flex items-center mt-2">
              <span className="text-sm text-gray-500 mr-2">Confidence:</span>
              <Progress value={strategy.confidence * 100} max={100} />
              <span className="ml-2">{Math.round(strategy.confidence * 100)}%</span>
            </div>
          </div>

          <div className="mb-4">
            <h4 className="font-semibold mb-2">Estimated Profit:</h4>
            <span className="text-2xl font-bold text-green-500">
              {formatCurrency(strategy.estimated_profit)}
            </span>
          </div>

          <div className="space-y-4">
            {strategy.routes.map((route, routeIndex) => (
              <div key={routeIndex} className="p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-500">Buy Network:</span>
                    <p>{route.buy_network}</p>
                    <span className="text-sm text-gray-500">Price:</span>
                    <p>{formatCurrency(route.buy_price)}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">Sell Network:</span>
                    <p>{route.sell_network}</p>
                    <span className="text-sm text-gray-500">Price:</span>
                    <p>{formatCurrency(route.sell_price)}</p>
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-sm text-gray-500">Gas Cost:</span>
                  <p>{formatCurrency(route.gas_cost)}</p>
                  <span className="text-sm text-gray-500">Slippage Cost:</span>
                  <p>{formatCurrency(route.slippage_cost)}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
};

export default ArbitrageView;