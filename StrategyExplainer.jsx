import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from './components/ui/card';
import { Progress } from './components/ui/progress';
import { ErrorMessage } from './components/ErrorMessage';

interface StrategyResponse {
  description: string;
  key_points: string[];
  success_rate: number;
  risk_level: string;
  market_conditions: {
    sentiment: string;
    volatility: string;
    trend: string;
  };
  visualization_data: Array<{
    name: string;
    profit: number;
    confidence: number;
  }>;
  ai_confidence: number;
}

const StrategyExplainer: React.FC = () => {
  const [selectedStrategy, setSelectedStrategy] = useState<string>('trend_following');

  const { data: strategyData, isLoading, error } = useQuery<StrategyResponse>({
    queryKey: ['strategy', selectedStrategy],
    queryFn: async () => {
      const response = await fetch(`/api/strategy/${selectedStrategy}`);
      return response.json();
    },
    staleTime: 30000,
    cacheTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false
  });

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>Loading strategy data...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Strategy Explainer</h2>
      {strategyData ? (
        <div>
          <p className="mb-4">{strategyData.description}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {strategyData.key_points.map((point, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">{point}</p>
              </div>
            ))}
          </div>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Market Conditions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Sentiment</p>
                <Progress value={strategyData.market_conditions.sentiment} className="mb-2" />
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Volatility</p>
                <Progress value={strategyData.market_conditions.volatility} className="mb-2" />
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Trend</p>
                <Progress value={strategyData.market_conditions.trend} className="mb-2" />
              </div>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Visualization</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={strategyData.visualization_data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="profit" stroke="#3B82F6" />
                  <Line type="monotone" dataKey="confidence" stroke="#10B981" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-gray-500">No strategy data available.</p>
      )}
    </Card>
  );
};

export default StrategyExplainer;