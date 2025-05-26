import React from 'react';
import { TradingProvider } from '../contexts/TradingContext';
import TradingInterface from '../components/TradingInterface';
import TradingChart from '../components/TradingChart';
import PriceCard from '../components/PriceCard';
import ArbitrageCard from '../components/ArbitrageCard';

const TradingDashboard: React.FC = () => {
  return (
    <TradingProvider>
      <div className="min-h-screen bg-gray-900 text-white">
        <header className="border-b border-gray-800 p-4 shadow-lg">
          <div className="container mx-auto">
            <h1 className="text-4xl font-bold mb-2">Advanced Trading Platform</h1>
            <p className="text-gray-400">AI-Powered Multi-Chain Trading</p>
          </div>
        </header>

        <main className="container mx-auto p-8">
          <div className="space-y-8">
            {/* Market Overview */}
            <section>
              <h2 className="text-2xl font-bold mb-4">Market Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {/* Price cards will be rendered here by TradingInterface */}
              </div>
            </section>

            {/* Trading Interface and Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <section>
                <div className="bg-gray-800 rounded-lg border border-gray-700 shadow-lg p-6">
                  <h2 className="text-2xl font-bold mb-4">Trading Chart</h2>
                  <TradingChart data={[]} />
                </div>
              </section>

              <section>
                <div className="bg-gray-800 rounded-lg border border-gray-700 shadow-lg p-6">
                  <h2 className="text-2xl font-bold mb-4">Trading Interface</h2>
                  <TradingInterface />
                </div>
              </section>
            </div>

            {/* Arbitrage Opportunities */}
            <section>
              <h2 className="text-2xl font-bold mb-4">Arbitrage Opportunities</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* ArbitrageCards will be rendered here by parent component */}
              </div>
            </section>
          </div>
        </main>
      </div>
    </TradingProvider>
  );
};

export default TradingDashboard;