import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTradingContext } from '../contexts/TradingContext';

type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
type Indicator = 'MA' | 'EMA' | 'RSI' | 'MACD';

interface ChartData {
  timestamp: number;
  price: number;
  volume: number;
  ma?: number;
  ema?: number;
  rsi?: number;
  macd?: number;
  signal?: number;
  histogram?: number;
}

interface TradingChartProps {
  data: ChartData[];
  onTimeframeChange?: (timeframe: Timeframe) => void;
  defaultTimeframe?: Timeframe;
}

const TradingChart: React.FC<TradingChartProps> = ({
  data,
  onTimeframeChange,
  defaultTimeframe = '15m'
}) => {
  const [timeframe, setTimeframe] = useState<Timeframe>(defaultTimeframe);
  const [activeIndicators, setActiveIndicators] = useState<Set<Indicator>>(new Set());
  const { selectedPair } = useTradingContext();

  const timeframes: Timeframe[] = ['1m', '5m', '15m', '1h', '4h', '1d'];
  const indicators: Indicator[] = ['MA', 'EMA', 'RSI', 'MACD'];

  const handleTimeframeChange = (newTimeframe: Timeframe) => {
    setTimeframe(newTimeframe);
    onTimeframeChange?.(newTimeframe);
  };

  const toggleIndicator = (indicator: Indicator) => {
    const newIndicators = new Set(activeIndicators);
    if (newIndicators.has(indicator)) {
      newIndicators.delete(indicator);
    } else {
      newIndicators.add(indicator);
    }
    setActiveIndicators(newIndicators);
  };

  // Calculate chart statistics
  const stats = useMemo(() => {
    if (!data.length) return { high: 0, low: 0, volume: 0 };
    
    const last24h = data.filter(d => d.timestamp >= Date.now() - 24 * 60 * 60 * 1000);
    return {
      high: Math.max(...last24h.map(d => d.price)),
      low: Math.min(...last24h.map(d => d.price)),
      volume: last24h.reduce((sum, d) => sum + d.volume, 0)
    };
  }, [data]);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <select
          value={timeframe}
          onChange={(e) => handleTimeframeChange(e.target.value as Timeframe)}
          className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          {timeframes.map(tf => (
            <option key={tf} value={tf}>{tf}</option>
          ))}
        </select>

        <div className="flex gap-2">
          {indicators.map(indicator => (
            <button
              key={indicator}
              onClick={() => toggleIndicator(indicator)}
              className={`px-3 py-1 rounded transition-colors ${
                activeIndicators.has(indicator)
                  ? 'bg-purple-500 text-white'
                  : 'border border-purple-500 text-purple-500 hover:bg-purple-500 hover:text-white'
              }`}
            >
              {indicator}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-xl font-bold mb-4">{selectedPair} Price Chart</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(156, 163, 175, 0.1)" />
            <XAxis
              dataKey="timestamp"
              type="number"
              domain={['auto', 'auto']}
              scale="time"
              tickFormatter={(ts) => new Date(ts).toLocaleTimeString()}
            />
            <YAxis yAxisId="price" orientation="left" />
            <YAxis yAxisId="volume" orientation="right" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151'
              }}
              labelFormatter={(label) => new Date(label).toLocaleString()}
            />
            
            {/* Price line */}
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="price"
              stroke="#10B981"
              dot={false}
            />

            {/* Volume line */}
            <Line
              yAxisId="volume"
              type="monotone"
              dataKey="volume"
              stroke="rgba(16, 185, 129, 0.2)"
              dot={false}
            />

            {/* Technical indicators */}
            {activeIndicators.has('MA') && (
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="ma"
                stroke="#60A5FA"
                dot={false}
              />
            )}
            {activeIndicators.has('EMA') && (
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="ema"
                stroke="#F59E0B"
                dot={false}
              />
            )}
            {activeIndicators.has('RSI') && (
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="rsi"
                stroke="#EC4899"
                dot={false}
              />
            )}
            {activeIndicators.has('MACD') && (
              <>
                <Line
                  yAxisId="price"
                  type="monotone"
                  dataKey="macd"
                  stroke="#8B5CF6"
                  dot={false}
                />
                <Line
                  yAxisId="price"
                  type="monotone"
                  dataKey="signal"
                  stroke="#D946EF"
                  dot={false}
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Price Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">24h High</div>
          <div className="text-xl font-bold">
            ${stats.high.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">24h Low</div>
          <div className="text-xl font-bold">
            ${stats.low.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-sm text-gray-400">24h Volume</div>
          <div className="text-xl font-bold">
            ${stats.volume.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingChart;