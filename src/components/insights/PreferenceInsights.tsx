import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell
} from 'recharts';
import { Card } from '../ui/card';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Progress } from '../ui/progress';

const CATEGORY_COLORS: { [key: string]: string } = {
  trading: '#2196f3',
  ui: '#4caf50',
  analysis: '#ff9800',
  rehoboam: '#9c27b0',
  risk: '#f44336',
  performance: '#00bcd4'
};

interface CategoryImpact {
  impact: number;
  confidence: number;
}

interface TopSetting {
  key: string;
  value: any;
  impact: number;
  confidence: number;
}

interface Suggestion {
  category: string;
  current_impact: number;
  suggested_settings: {
    key: string;
    value: any;
    impact: number;
  }[];
  confidence: number;
  priority: string;
}

interface PerformancePoint {
  timestamp: string;
  impact: number;
  confidence: number;
}

interface InsightData {
  category_impact: { [key: string]: CategoryImpact };
  top_settings: { [key: string]: TopSetting[] };
  suggestions: Suggestion[];
  performance_history: PerformancePoint[];
}

const PreferenceInsights: React.FC = () => {
  const [insights, setInsights] = useState<InsightData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState('7d');

  useEffect(() => {
    fetchInsights();
  }, [timeframe]);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/preferences/insights?timeframe=${timeframe}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch insights: ${response.statusText}`);
      }
      
      const data: InsightData = await response.json();
      setInsights(data);
    } catch (err) {
      console.error('Error fetching insights:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch preference insights');
      
      // Fallback mock data for development
      setInsights({
        category_impact: {
          trading: { impact: 85, confidence: 92 },
          ui: { impact: 67, confidence: 78 },
          analysis: { impact: 91, confidence: 88 },
          rehoboam: { impact: 96, confidence: 95 }
        },
        top_settings: {
          trading: [
            { key: 'risk_tolerance', value: 'moderate', impact: 85, confidence: 90 },
            { key: 'max_position_size', value: 0.1, impact: 78, confidence: 85 }
          ],
          analysis: [
            { key: 'technical_indicators', value: ['RSI', 'MACD'], impact: 91, confidence: 88 }
          ]
        },
        suggestions: [
          {
            category: 'trading',
            current_impact: 85,
            suggested_settings: [
              { key: 'stop_loss_percentage', value: 0.05, impact: 92 }
            ],
            confidence: 87,
            priority: 'high'
          }
        ],
        performance_history: [
          { timestamp: '2025-05-20T00:00:00Z', impact: 78, confidence: 80 },
          { timestamp: '2025-05-21T00:00:00Z', impact: 82, confidence: 83 },
          { timestamp: '2025-05-22T00:00:00Z', impact: 85, confidence: 87 },
          { timestamp: '2025-05-23T00:00:00Z', impact: 89, confidence: 90 },
          { timestamp: '2025-05-24T00:00:00Z', impact: 91, confidence: 92 },
          { timestamp: '2025-05-25T00:00:00Z', impact: 88, confidence: 89 },
          { timestamp: '2025-05-26T00:00:00Z', impact: 93, confidence: 94 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const formatPerformanceHistory = (history: PerformancePoint[]) => {
    return history.map(point => ({
      date: new Date(point.timestamp).toLocaleDateString(),
      impact: point.impact,
      confidence: point.confidence
    }));
  };

  const formatCategoryData = (categoryImpact: { [key: string]: CategoryImpact }) => {
    return Object.entries(categoryImpact).map(([category, data]) => ({
      category: category.charAt(0).toUpperCase() + category.slice(1),
      impact: data.impact,
      confidence: data.confidence,
      fill: CATEGORY_COLORS[category] || '#8884d8'
    }));
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-900/30 text-red-300';
      case 'medium': return 'bg-yellow-900/30 text-yellow-300';
      case 'low': return 'bg-green-900/30 text-green-300';
      default: return 'bg-gray-900/30 text-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="p-8 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
            <div className="flex items-center justify-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
              <span className="text-white text-lg">Analyzing preference insights...</span>
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
                Preference Insights
              </h1>
              <p className="text-purple-300">
                AI-powered analysis of your trading preferences and system performance
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="1d">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
              <button
                onClick={fetchInsights}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        {error && (
          <Alert variant="warning" className="mb-6">
            <AlertTitle>Using Mock Data</AlertTitle>
            <AlertDescription>
              Unable to fetch live insights: {error}. Displaying sample data for demonstration.
            </AlertDescription>
          </Alert>
        )}

        {insights && (
          <>
            {/* Performance History Chart */}
            <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm mb-8">
              <h3 className="text-lg font-semibold text-white mb-4">Performance History</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={formatPerformanceHistory(insights.performance_history)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="impact" 
                    stroke="#10B981" 
                    strokeWidth={3}
                    name="Impact Score"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="confidence" 
                    stroke="#3B82F6" 
                    strokeWidth={3}
                    name="Confidence Level"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            {/* Category Impact Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
                <h3 className="text-lg font-semibold text-white mb-4">Category Impact</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={formatCategoryData(insights.category_impact)}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      dataKey="impact"
                      label={({ category, impact }) => `${category}: ${impact}%`}
                    >
                      {formatCategoryData(insights.category_impact).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>

              <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
                <h3 className="text-lg font-semibold text-white mb-4">Impact vs Confidence</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={formatCategoryData(insights.category_impact)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="category" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Bar dataKey="impact" fill="#10B981" name="Impact Score" />
                    <Bar dataKey="confidence" fill="#3B82F6" name="Confidence Level" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Top Settings by Category */}
            <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm mb-8">
              <h3 className="text-lg font-semibold text-white mb-4">Top Performing Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(insights.top_settings).map(([category, settings]) => (
                  <div key={category} className="bg-gray-800/50 p-4 rounded-lg">
                    <h4 className="font-semibold text-white mb-3 capitalize">
                      {category}
                    </h4>
                    <div className="space-y-3">
                      {settings.slice(0, 3).map((setting, index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-300">{setting.key}</span>
                            <Badge className="bg-purple-900/30 text-purple-300">
                              {setting.impact}%
                            </Badge>
                          </div>
                          <div className="text-xs text-gray-400">
                            Value: {JSON.stringify(setting.value)}
                          </div>
                          <Progress value={setting.confidence} className="h-1" />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* AI Suggestions */}
            <Card className="p-6 bg-gray-900/50 border-gray-700 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-white mb-4">AI Optimization Suggestions</h3>
              <div className="space-y-4">
                {insights.suggestions.map((suggestion, index) => (
                  <div key={index} className="bg-gray-800/50 p-4 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-white capitalize">
                        {suggestion.category} Optimization
                      </h4>
                      <div className="flex items-center space-x-2">
                        <Badge className={getPriorityColor(suggestion.priority)}>
                          {suggestion.priority.toUpperCase()}
                        </Badge>
                        <span className="text-sm text-gray-400">
                          {suggestion.confidence}% confidence
                        </span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-400 mb-2">Current Impact</p>
                        <div className="flex items-center space-x-2">
                          <Progress value={suggestion.current_impact} className="flex-1" />
                          <span className="text-sm font-medium text-white">
                            {suggestion.current_impact}%
                          </span>
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-400 mb-2">Suggested Settings</p>
                        {suggestion.suggested_settings.map((setting, settingIndex) => (
                          <div key={settingIndex} className="text-sm">
                            <span className="text-gray-300">{setting.key}:</span>
                            <span className="text-white ml-2">{JSON.stringify(setting.value)}</span>
                            <span className="text-green-400 ml-2">(+{setting.impact}%)</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mt-3 flex justify-end">
                      <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors">
                        Apply Suggestion
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default PreferenceInsights;
