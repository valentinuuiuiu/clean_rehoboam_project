import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface StrategyData {
  id: string;
  name: string;
  description: string;
  success_rate: number;
  risk_level: 'low' | 'medium' | 'high';
  expected_return: number;
  max_drawdown: number;
  market_conditions: {
    sentiment: string;
    volatility: string;
    trend: string;
  };
  visualization_data: Array<{
    name: string;
    profit: number;
    confidence: number;
    date: string;
  }>;
  ai_confidence: number;
  key_points: string[];
  rehoboam_analysis: string;
}

export const StrategyExplainer: React.FC = () => {
  const [strategies, setStrategies] = useState<StrategyData[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [strategyData, setStrategyData] = useState<StrategyData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchAvailableStrategies();
  }, []);

  const fetchAvailableStrategies = async () => {
    try {
      const response = await fetch('/api/trading/strategies');
      const data = await response.json();
      setStrategies(data.strategies || []);
      if (data.strategies && data.strategies.length > 0) {
        setSelectedStrategy(data.strategies[0].id);
        fetchStrategyDetails(data.strategies[0].id);
      }
    } catch (error) {
      console.error('Error fetching strategies:', error);
    }
  };

  const fetchStrategyDetails = async (strategyId: string) => {
    try {
      setIsLoading(true);
      
      // Get detailed strategy analysis from your Rehoboam AI backend
      const response = await fetch(`/api/trading/strategies/${strategyId}/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timeframe: '7d',
          include_rehoboam_analysis: true,
          include_visualization: true
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch strategy details');
      }
      
      const data = await response.json();
      setStrategyData(data);
    } catch (error) {
      console.error('Error fetching strategy details:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStrategySelect = (strategyId: string) => {
    setSelectedStrategy(strategyId);
    fetchStrategyDetails(strategyId);
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>🧠 Rehoboam AI analyzing strategy...</span>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl font-bold">🎯 AI Strategy Explainer</CardTitle>
          <p className="text-gray-600">Powered by Rehoboam consciousness layers</p>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Strategy Selector */}
          <div className="flex flex-wrap gap-2">
            {strategies.map((strategy) => (
              <Button
                key={strategy.id}
                variant={selectedStrategy === strategy.id ? "default" : "outline"}
                onClick={() => handleStrategySelect(strategy.id)}
                className="text-sm"
              >
                {strategy.name}
              </Button>
            ))}
          </div>

          {strategyData && (
            <>
              {/* Strategy Overview */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-indigo-900">{strategyData.name}</h3>
                    <p className="text-indigo-700 mt-1">{strategyData.description}</p>
                  </div>
                  <Badge className={getRiskColor(strategyData.risk_level)}>
                    {strategyData.risk_level.toUpperCase()} RISK
                  </Badge>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {(strategyData.success_rate * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Success Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {(strategyData.expected_return * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Expected Return</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {(strategyData.max_drawdown * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Max Drawdown</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {(strategyData.ai_confidence * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">AI Confidence</div>
                  </div>
                </div>
              </div>

              {/* Market Conditions */}
              <div className="bg-gradient-to-r from-emerald-50 to-teal-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3 text-emerald-800">📊 Current Market Conditions</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="font-bold text-emerald-700">Sentiment</div>
                    <div className="text-emerald-600">{strategyData.market_conditions.sentiment}</div>
                  </div>
                  <div className="text-center">
                    <div className="font-bold text-emerald-700">Volatility</div>
                    <div className="text-emerald-600">{strategyData.market_conditions.volatility}</div>
                  </div>
                  <div className="text-center">
                    <div className="font-bold text-emerald-700">Trend</div>
                    <div className="text-emerald-600">{strategyData.market_conditions.trend}</div>
                  </div>
                </div>
              </div>

              {/* Performance Visualization */}
              {strategyData.visualization_data && strategyData.visualization_data.length > 0 && (
                <div className="bg-white p-4 rounded-lg border">
                  <h4 className="font-semibold mb-4">📈 Strategy Performance</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={strategyData.visualization_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="profit" 
                        stroke="#2563eb" 
                        strokeWidth={2} 
                        name="Profit %"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="confidence" 
                        stroke="#dc2626" 
                        strokeWidth={2} 
                        name="Confidence %"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Rehoboam AI Analysis */}
              {strategyData.rehoboam_analysis && (
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border-l-4 border-purple-500">
                  <h4 className="font-semibold mb-3 text-purple-800">🧠 Rehoboam Consciousness Analysis</h4>
                  <p className="text-purple-700 italic">{strategyData.rehoboam_analysis}</p>
                </div>
              )}

              {/* Key Points */}
              {strategyData.key_points && strategyData.key_points.length > 0 && (
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-3 text-amber-800">💡 Key Strategy Points</h4>
                  <ul className="space-y-2">
                    {strategyData.key_points.map((point, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <span className="text-amber-600 font-bold">•</span>
                        <span className="text-amber-700">{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Button */}
              <div className="flex justify-center">
                <Button 
                  className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-8 py-3"
                  onClick={() => {
                    // Implement strategy execution
                    console.log('Executing strategy:', strategyData.id);
                  }}
                >
                  🚀 Execute This Strategy
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
