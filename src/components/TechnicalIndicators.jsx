import React from 'react';
import { calculateRSI, calculateMACD, calculateSMA } from '../utils/indicators';

const TechnicalIndicators = ({ prices, symbol }) => {
  const priceHistory = prices[symbol]?.history || [];
  
  // Calculate indicators
  const rsi = calculateRSI(priceHistory, 14);
  const macd = calculateMACD(priceHistory);
  const sma20 = calculateSMA(priceHistory, 20);
  const sma50 = calculateSMA(priceHistory, 50);

  return (
    <div className="bg-gray-700 p-4 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Technical Analysis</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-sm text-gray-400">RSI (14)</div>
          <div className={`text-lg font-bold ${
            rsi > 70 ? 'text-red-500' : 
            rsi < 30 ? 'text-green-500' : 
            'text-white'
          }`}>
            {rsi?.toFixed(2)}
          </div>
        </div>

        <div>
          <div className="text-sm text-gray-400">MACD</div>
          <div className={`text-lg font-bold ${
            macd.histogram > 0 ? 'text-green-500' : 'text-red-500'
          }`}>
            {macd.macd?.toFixed(2)}
          </div>
        </div>

        <div>
          <div className="text-sm text-gray-400">SMA 20</div>
          <div className="text-lg font-bold">${sma20?.toFixed(2)}</div>
        </div>

        <div>
          <div className="text-sm text-gray-400">SMA 50</div>
          <div className="text-lg font-bold">${sma50?.toFixed(2)}</div>
        </div>
      </div>

      <div className="mt-4 text-sm">
        <div className={`p-2 rounded ${
          rsi > 70 ? 'bg-red-900/20 text-red-400' :
          rsi < 30 ? 'bg-green-900/20 text-green-400' :
          'bg-gray-800 text-gray-400'
        }`}>
          {rsi > 70 ? 'Overbought - Consider Selling' :
           rsi < 30 ? 'Oversold - Consider Buying' :
           'Neutral RSI'}
        </div>
      </div>
    </div>
  );
};

export default TechnicalIndicators;
