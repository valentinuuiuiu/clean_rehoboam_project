import React from 'react';

interface ArbitrageOpportunity {
  token: string;
  confidence_score: number;
  buy_network: string;
  sell_network: string;
  buy_price: number;
  sell_price: number;
  expected_profit_usd: number;
  gas_cost: number;
}

interface ArbitrageCardProps {
  opportunity: ArbitrageOpportunity;
}

const ArbitrageCard: React.FC<ArbitrageCardProps> = ({ opportunity }) => {
  return (
    <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <span className="text-lg font-bold">{opportunity.token}</span>
        <span className={`px-2 py-1 rounded-full text-sm ${
          opportunity.confidence_score > 0.7 
            ? 'bg-green-500/20 text-green-400' 
            : 'bg-yellow-500/20 text-yellow-400'
        }`}>
          {(opportunity.confidence_score * 100).toFixed(1)}% confidence
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-gray-400">Buy on</div>
          <div>{opportunity.buy_network}</div>
          <div className="text-xl font-bold text-green-400">
            ${opportunity.buy_price.toFixed(2)}
          </div>
        </div>
        <div>
          <div className="text-gray-400">Sell on</div>
          <div>{opportunity.sell_network}</div>
          <div className="text-xl font-bold text-red-400">
            ${opportunity.sell_price.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center">
        <div>
          <div className="text-gray-400">Expected Profit</div>
          <div className="text-xl font-bold text-green-400">
            ${opportunity.expected_profit_usd.toFixed(2)}
          </div>
        </div>
        <div>
          <div className="text-gray-400">Gas Cost</div>
          <div className="text-xl font-bold text-gray-300">
            ${opportunity.gas_cost.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArbitrageCard;