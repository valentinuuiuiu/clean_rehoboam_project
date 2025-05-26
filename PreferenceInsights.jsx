import React, { useEffect, useState, createContext, useContext } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell
} from 'recharts';

interface PreferencesContextType {
  preferences: any;
}

const PreferencesContext = createContext<PreferencesContextType>({ preferences: null });

export const usePreferences = () => useContext(PreferencesContext);

const CATEGORY_COLORS: { [key: string]: string } = {
  trading: '#2196f3',
  ui: '#4caf50',
  analysis: '#ff9800',
  rehoboam: '#9c27b0'
};

interface InsightData {
  category_impact: { [key: string]: { impact: number; confidence: number } };
  top_settings: { [key: string]: { key: string; value: any; impact: number; confidence: number }[] };
  suggestions: { category: string; current_impact: number; suggested_settings: { key: string; value: any; impact: number }[]; confidence: number; priority: string }[];
  performance_history: { timestamp: string; impact: number; confidence: number }[];
}

const PreferenceInsights: React.FC = () => {
  const [insights, setInsights] = useState<InsightData | null>(null);
  const [loading, setLoading] = useState(true);
  const { preferences } = usePreferences();

  useEffect(() => {
    fetchInsights();
  }, [preferences]);

  const fetchInsights = async () => {
    try {
      const response = await fetch('/api/preferences/insights?timeframe=7d');
      const data: InsightData = await response.json();
      setInsights(data);
    } catch (error) {
      console.error('Error fetching insights:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading insights...</div>;
  if (!insights) return <div>No insights available</div>;

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Performance Insights</h1>

      {/* Overall Performance Impact */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Category Impact</h2>
        <div className="bg-white p-4 rounded-lg shadow">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(insights.category_impact).map(([category, data]) => ({
              category,
              impact: data.impact,
              confidence: data.confidence
            }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="impact" fill="#2196f3" name="Performance Impact">
                {Object.entries(insights.category_impact).map(([category]) => (
                  <Cell key={category} fill={CATEGORY_COLORS[category]} />
                ))}
              </Bar>
              <Bar dataKey="confidence" fill="#4caf50" name="Confidence" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Top Performing Settings */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Top Performing Settings</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(insights.top_settings).map(([category, settings]) => (
            <div key={category} className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-medium mb-2 capitalize">{category}</h3>
              <div className="space-y-2">
                {settings.map((setting, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span>{setting.key}: {JSON.stringify(setting.value)}</span>
                    <span className={`px-2 py-1 rounded text-sm ${
                      setting.impact > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {(setting.impact * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Optimization Suggestions */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Optimization Suggestions</h2>
        <div className="space-y-4">
          {insights.suggestions.map((suggestion, index) => (
            <div key={index} className={`p-4 rounded-lg border ${
              suggestion.priority === 'high' 
                ? 'border-red-200 bg-red-50'
                : 'border-yellow-200 bg-yellow-50'
            }`}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium capitalize">{suggestion.category}</h4>
                  <p className="text-sm text-gray-600">
                    Current Impact: {(suggestion.current_impact * 100).toFixed(1)}%
                  </p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  suggestion.priority === 'high'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {suggestion.priority} priority
                </span>
              </div>
              <div className="mt-2">
                <p className="text-sm font-medium">Suggested Changes:</p>
                <ul className="mt-1 space-y-1">
                  {suggestion.suggested_settings.map((setting, idx) => (
                    <li key={idx} className="text-sm">
                      • Set {setting.key} to {JSON.stringify(setting.value)}
                      <span className="text-green-600 ml-2">
                        (+{(setting.impact * 100).toFixed(1)}%)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="mt-2 text-sm text-gray-500">
                Confidence: {(suggestion.confidence * 100).toFixed()}%
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Performance Trends */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Performance Trends</h2>
        <div className="bg-white p-4 rounded-lg shadow">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={insights.performance_history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="impact" 
                stroke="#2196f3" 
                name="Performance Impact" 
              />
              <Line 
                type="monotone" 
                dataKey="confidence" 
                stroke="#4caf50" 
                name="Confidence" 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Category Distribution */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Impact Distribution</h2>
        <div className="bg-white p-4 rounded-lg shadow">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={Object.entries(insights.category_impact).map(([category, data]) => ({
                  name: category,
                  value: Math.abs(data.impact)
                }))}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {Object.entries(insights.category_impact).map(([category]) => (
                  <Cell key={category} fill={CATEGORY_COLORS[category]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
};

export default PreferenceInsights;