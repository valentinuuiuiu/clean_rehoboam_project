import React, { useState, useEffect } from 'react';
import AICompanionCreator from './components/AICompanionCreator';
import MCPFunctionVisualizer from './components/MCPFunctionVisualizer';
import MCPStatus from './components/MCPStatus';
import VetalaProtectionDashboard from './components/VetalaProtectionDashboard';
import ProfitableFlashArbitrage from './components/ProfitableFlashArbitrage';
import { useWeb3 } from './contexts/Web3Context';
import { useNotification } from './contexts/NotificationContext';
import tradingService from './services/tradingService';

// Removed RehoboamAI class definition

function App() {
  const [activeTab, setActiveTab] = useState('trading');
  const [tradingForm, setTradingForm] = useState({
    token: 'ETH',
    network: 'arbitrum',
    amount: '',
    slippage: 1
  });
  const [strategies, setStrategies] = useState([]);
  const [marketAnalysis, setMarketAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  // const [rehoboamActive, setRehoboamActive] = useState(false); // Removed
  // const [rehoboamAI, setRehoboamAI] = useState(null); // Removed
  const [liveData, setLiveData] = useState({
    prices: { BTC: 59423.50, ETH: 3452.18, LINK: 14.85 },
    lastUpdate: new Date()
  });
  
  const { account, connectWallet, isConnected, balance } = useWeb3();
  const { addNotification } = useNotification();

  // Load strategies and market analysis on component mount
  useEffect(() => {
    loadTradingStrategies();
    loadMarketAnalysis();
    loadLivePrices();
    
    // Removed Rehoboam AI initialization
    
    // Set up live price updates
    const priceInterval = setInterval(loadLivePrices, 10000); // Every 10 seconds
    
    return () => {
      // if (ai) ai.deactivate(); // Removed Rehoboam AI deactivation
      clearInterval(priceInterval);
    };
  }, []);

  const loadTradingStrategies = async () => {
    try {
      const fetchedStrategies = await tradingService.getStrategies();
      setStrategies(fetchedStrategies);
    } catch (error) {
      console.error('Error loading strategies:', error);
      addNotification('error', 'Failed to load trading strategies');
    }
  };

  const loadMarketAnalysis = async () => {
    try {
      const analysis = await tradingService.getMarketSentiment();
      setMarketAnalysis(analysis);
    } catch (error) {
      console.error('Error loading market analysis:', error);
      addNotification('error', 'Failed to load market analysis');
    }
  };

  const loadLivePrices = async () => {
    try {
      const prices = await tradingService.getPrices(['BTC', 'ETH', 'LINK']);
      setLiveData({ prices, lastUpdate: new Date() });
    } catch (error) {
      // Use mock data if API fails
      const mockPrices = {
        BTC: 59423.50 + (Math.random() - 0.5) * 1000,
        ETH: 3452.18 + (Math.random() - 0.5) * 200,
        LINK: 14.85 + (Math.random() - 0.5) * 2
      };
      setLiveData({ prices: mockPrices, lastUpdate: new Date() });
    }
  };

  const handleTradeExecution = async (action) => {
    if (!isConnected) {
      addNotification('warning', 'Please connect your wallet first');
      await connectWallet();
      return;
    }

    if (!tradingForm.amount || parseFloat(tradingForm.amount) <= 0) {
      addNotification('error', 'Please enter a valid amount');
      return;
    }

    setLoading(true);
    try {
      const tradeData = {
        action,
        token: tradingForm.token,
        network: tradingForm.network,
        amount: parseFloat(tradingForm.amount),
        slippage: tradingForm.slippage,
        wallet: account
      };

      const result = await tradingService.executeTrade(tradeData);
      addNotification('success', `${action} order submitted successfully`);
      
      // Reset form
      setTradingForm({ ...tradingForm, amount: '' });
    } catch (error) {
      console.error(`Error executing ${action}:`, error);
      addNotification('error', `Failed to execute ${action} order`);
    } finally {
      setLoading(false);
    }
  };

  const handleStrategyExecution = async (strategy) => {
    if (!isConnected) {
      addNotification('warning', 'Please connect your wallet first');
      await connectWallet();
      return;
    }

    setLoading(true);
    try {
      const result = await tradingService.executeStrategy({
        strategyId: strategy.id,
        wallet: account,
        network: tradingForm.network
      });
      
      addNotification('success', `Strategy "${strategy.name}" executed successfully`);
    } catch (error) {
      console.error('Error executing strategy:', error);
      addNotification('error', `Failed to execute strategy: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const updateTradingForm = (field, value) => {
    setTradingForm(prev => ({ ...prev, [field]: value }));
  };

  // Removed toggleRehoboam function

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 p-4 shadow-lg">
        <div className="container mx-auto">
          <h1 className="text-4xl font-bold mb-2">Rehoboam Platform</h1>
          <p className="text-gray-400">AI-Powered Trading & Companions</p>
          
          {/* Navigation Tabs */}
          <div className="flex mt-6 border-b border-gray-700">
            <button
              className={`px-4 py-2 font-medium ${
                activeTab === 'trading'
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => setActiveTab('trading')}
            >
              Trading
            </button>
            <button
              className={`px-4 py-2 font-medium ${
                activeTab === 'companions'
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => setActiveTab('companions')}
            >
              AI Companions
            </button>
            <button
              className={`px-4 py-2 font-medium ${
                activeTab === 'mcp'
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => setActiveTab('mcp')}
            >
              MCP Visualizer
            </button>
            <button
              className={`px-4 py-2 font-medium ${
                activeTab === 'vetala'
                  ? 'text-yellow-400 border-b-2 border-yellow-400'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => setActiveTab('vetala')}
            >
              🕉️ Vetal Shabar Raksha
            </button>
            <button
              className={`px-4 py-2 font-medium ${
                activeTab === 'flash-arbitrage'
                  ? 'text-green-400 border-b-2 border-green-400'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => setActiveTab('flash-arbitrage')}
            >
              ⚡ Flash Arbitrage
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4">
        {activeTab === 'trading' && (
          <div className="space-y-8">
            {/* Import existing trading components */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                  <div className="p-4 border-b border-gray-700">
                    <h2 className="text-xl font-bold">Trading Dashboard</h2>
                  </div>
                  <div className="p-4">
                    <div className="import-component">
                      {/* This will be replaced by the TradingDashboard component */}
                      <div className="bg-gray-700 p-6 rounded-lg text-center">
                        <p className="text-gray-400 mb-4">Market Overview</p>
                        <div className="grid grid-cols-3 gap-4 mb-6">
                          <div className="bg-gray-800 p-3 rounded-lg">
                            <p className="text-xs text-gray-400">BTC/USD</p>
                            <p className="text-xl font-bold">${liveData.prices.BTC}</p>
                            <p className="text-green-400">+2.5%</p>
                          </div>
                          <div className="bg-gray-800 p-3 rounded-lg">
                            <p className="text-xs text-gray-400">ETH/USD</p>
                            <p className="text-xl font-bold">${liveData.prices.ETH}</p>
                            <p className="text-green-400">+1.8%</p>
                          </div>
                          <div className="bg-gray-800 p-3 rounded-lg">
                            <p className="text-xs text-gray-400">LINK/USD</p>
                            <p className="text-xl font-bold">${liveData.prices.LINK}</p>
                            <p className="text-red-400">-0.7%</p>
                          </div>
                        </div>
                        <div className="h-48 bg-gray-800 rounded-lg mb-4 flex items-center justify-center">
                          <p className="text-gray-500">Price Chart</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                  <div className="p-4 border-b border-gray-700">
                    <h2 className="text-xl font-bold">Automated Trading</h2>
                  </div>
                  <div className="p-4">
                    <div className="import-component">
                      {/* This will be replaced by the AutomatedTrading component */}
                      <div className="space-y-4">
                        {/* Rehoboam AI Toggle UI Removed */}
                        
                        <div className="bg-gray-700 p-4 rounded-lg">
                          {/* Manual trade controls remain */}
                          <p className="text-sm text-gray-400 mb-3">Manual Trade Controls:</p>
                          <div className="mb-3">
                            <label className="block text-sm font-medium text-gray-400 mb-1">Token</label>
                            <select 
                              className="bg-gray-800 border border-gray-700 rounded w-full p-2"
                              value={tradingForm.token}
                              onChange={(e) => updateTradingForm('token', e.target.value)}
                            >
                              <option value="ETH">ETH</option>
                              <option value="BTC">BTC</option>
                              <option value="LINK">LINK</option>
                              <option value="UMA">UMA</option>
                              <option value="USDC">USDC</option>
                              <option value="USDT">USDT</option>
                            </select>
                          </div>
                          
                          <div className="mb-3">
                            <label className="block text-sm font-medium text-gray-400 mb-1">Network</label>
                            <select 
                              className="bg-gray-800 border border-gray-700 rounded w-full p-2"
                              value={tradingForm.network}
                              onChange={(e) => updateTradingForm('network', e.target.value)}
                            >
                              <option value="arbitrum">Arbitrum</option>
                              <option value="optimism">Optimism</option>
                              <option value="polygon">Polygon</option>
                              <option value="base">Base</option>
                              <option value="ethereum">Ethereum</option>
                            </select>
                          </div>
                          
                          <div className="mb-3">
                            <label className="block text-sm font-medium text-gray-400 mb-1">Amount</label>
                            <input 
                              type="number" 
                              className="bg-gray-800 border border-gray-700 rounded w-full p-2" 
                              placeholder="0.0"
                              value={tradingForm.amount}
                              onChange={(e) => updateTradingForm('amount', e.target.value)}
                              step="0.0001"
                              min="0"
                            />
                            {balance && (
                              <p className="text-xs text-gray-400 mt-1">
                                Wallet Balance: {parseFloat(balance).toFixed(4)} ETH
                              </p>
                            )}
                          </div>

                          <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-400 mb-1">Slippage (%)</label>
                            <select 
                              className="bg-gray-800 border border-gray-700 rounded w-full p-2"
                              value={tradingForm.slippage}
                              onChange={(e) => updateTradingForm('slippage', parseFloat(e.target.value))}
                            >
                              <option value={0.5}>0.5%</option>
                              <option value={1}>1%</option>
                              <option value={2}>2%</option>
                              <option value={5}>5%</option>
                            </select>
                          </div>
                          
                          {!isConnected ? (
                            <button 
                              onClick={connectWallet}
                              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 px-4 rounded mb-2"
                            >
                              Connect Wallet
                            </button>
                          ) : (
                            <div className="mb-2">
                              <p className="text-xs text-gray-400 mb-2">
                                Connected: {account?.slice(0, 6)}...{account?.slice(-4)}
                              </p>
                            </div>
                          )}
                          
                          <div className="flex space-x-2">
                            <button 
                              className={`w-1/2 text-white py-2 px-4 rounded ${
                                loading 
                                  ? 'bg-gray-600 cursor-not-allowed' 
                                  : 'bg-green-600 hover:bg-green-500'
                              }`}
                              onClick={() => handleTradeExecution('buy')}
                              disabled={loading}
                            >
                              {loading ? 'Processing...' : 'Buy'}
                            </button>
                            <button 
                              className={`w-1/2 text-white py-2 px-4 rounded ${
                                loading 
                                  ? 'bg-gray-600 cursor-not-allowed' 
                                  : 'bg-red-600 hover:bg-red-500'
                              }`}
                              onClick={() => handleTradeExecution('sell')}
                              disabled={loading}
                            >
                              {loading ? 'Processing...' : 'Sell'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Strategies Section */}
            <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
              <div className="p-4 border-b border-gray-700">
                <h2 className="text-xl font-bold">AI-Powered Trading Strategies</h2>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {strategies.length > 0 ? (
                    strategies.map((strategy, index) => (
                      <div key={strategy.id || index} className="border border-gray-700 rounded-lg p-4">
                        <div className="flex justify-between">
                          <h3 className="font-bold text-xl">{strategy.name}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            strategy.risk_level === 'low' ? 'bg-green-900/30 text-green-400' :
                            strategy.risk_level === 'moderate' ? 'bg-blue-900/30 text-blue-400' :
                            'bg-yellow-900/30 text-yellow-400'
                          }`}>
                            {strategy.risk_level} Risk
                          </span>
                        </div>
                        <p className="text-gray-400 mt-2">
                          {strategy.description}
                        </p>
                        <div className="flex justify-between items-center mt-3">
                          <div>
                            <span className="text-sm text-gray-400">Expected Return:</span>
                            <span className="ml-2 text-green-400">{strategy.expected_return}%</span>
                          </div>
                          <button 
                            className={`px-4 py-2 rounded text-white ${
                              loading 
                                ? 'bg-gray-600 cursor-not-allowed' 
                                : 'bg-green-600 hover:bg-green-500'
                            }`}
                            onClick={() => handleStrategyExecution(strategy)}
                            disabled={loading}
                          >
                            {loading ? 'Processing...' : 'Execute'}
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    // Fallback strategies if API fails
                    <>
                      <div className="border border-gray-700 rounded-lg p-4">
                        <div className="flex justify-between">
                          <h3 className="font-bold text-xl">ETH Layer 2 Accumulation</h3>
                          <span className="px-2 py-1 bg-blue-900/30 text-blue-400 rounded-full text-xs">
                            Moderate Risk
                          </span>
                        </div>
                        <p className="text-gray-400 mt-2">
                          Accumulate ETH on Arbitrum for reduced gas fees
                        </p>
                        <div className="flex justify-between items-center mt-3">
                          <div>
                            <span className="text-sm text-gray-400">Expected Return:</span>
                            <span className="ml-2 text-green-400">4.2%</span>
                          </div>
                          <button 
                            className={`px-4 py-2 rounded text-white ${
                              loading 
                                ? 'bg-gray-600 cursor-not-allowed' 
                                : 'bg-green-600 hover:bg-green-500'
                            }`}
                            onClick={() => handleStrategyExecution({
                              id: 'eth-l2-accumulation',
                              name: 'ETH Layer 2 Accumulation',
                              description: 'Accumulate ETH on Arbitrum for reduced gas fees'
                            })}
                            disabled={loading}
                          >
                            {loading ? 'Processing...' : 'Execute'}
                          </button>
                        </div>
                      </div>

                      <div className="border border-gray-700 rounded-lg p-4">
                        <div className="flex justify-between">
                          <h3 className="font-bold text-xl">Stablecoin Yield Strategy</h3>
                          <span className="px-2 py-1 bg-green-900/30 text-green-400 rounded-full text-xs">
                            Low Risk
                          </span>
                        </div>
                        <p className="text-gray-400 mt-2">
                          Generate yield on USDC via lending protocols
                        </p>
                        <div className="flex justify-between items-center mt-3">
                          <div>
                            <span className="text-sm text-gray-400">Expected Return:</span>
                            <span className="ml-2 text-green-400">3.5%</span>
                          </div>
                          <button 
                            className={`px-4 py-2 rounded text-white ${
                              loading 
                                ? 'bg-gray-600 cursor-not-allowed' 
                                : 'bg-green-600 hover:bg-green-500'
                            }`}
                            onClick={() => handleStrategyExecution({
                              id: 'stablecoin-yield',
                              name: 'Stablecoin Yield Strategy',
                              description: 'Generate yield on USDC via lending protocols'
                            })}
                            disabled={loading}
                          >
                            {loading ? 'Processing...' : 'Execute'}
                          </button>
                        </div>
                      </div>
                      
                      <div className="border border-gray-700 rounded-lg p-4">
                        <div className="flex justify-between">
                          <h3 className="font-bold text-xl">Cross-Chain Arbitrage</h3>
                          <span className="px-2 py-1 bg-yellow-900/30 text-yellow-400 rounded-full text-xs">
                            High Risk
                          </span>
                        </div>
                        <p className="text-gray-400 mt-2">
                          Exploit price differences across Arbitrum, Optimism, and Base
                        </p>
                        <div className="flex justify-between items-center mt-3">
                          <div>
                            <span className="text-sm text-gray-400">Expected Return:</span>
                            <span className="ml-2 text-green-400">7.8%</span>
                          </div>
                          <button 
                            className={`px-4 py-2 rounded text-white ${
                              loading 
                                ? 'bg-gray-600 cursor-not-allowed' 
                                : 'bg-green-600 hover:bg-green-500'
                            }`}
                            onClick={() => handleStrategyExecution({
                              id: 'cross-chain-arbitrage',
                              name: 'Cross-Chain Arbitrage',
                              description: 'Exploit price differences across Arbitrum, Optimism, and Base'
                            })}
                            disabled={loading}
                          >
                            {loading ? 'Processing...' : 'Execute'}
                          </button>
                        </div>
                      </div>
                      
                      <div className="border border-gray-700 rounded-lg p-4">
                        <div className="flex justify-between">
                          <h3 className="font-bold text-xl">DEX-CEX Spread Strategy</h3>
                          <span className="px-2 py-1 bg-blue-900/30 text-blue-400 rounded-full text-xs">
                            Moderate Risk
                          </span>
                        </div>
                        <p className="text-gray-400 mt-2">
                          Profit from temporary price discrepancies between DEXs and CEXs
                        </p>
                        <div className="flex justify-between items-center mt-3">
                          <div>
                            <span className="text-sm text-gray-400">Expected Return:</span>
                            <span className="ml-2 text-green-400">5.1%</span>
                          </div>
                          <button 
                            className={`px-4 py-2 rounded text-white ${
                              loading 
                                ? 'bg-gray-600 cursor-not-allowed' 
                                : 'bg-green-600 hover:bg-green-500'
                            }`}
                            onClick={() => handleStrategyExecution({
                              id: 'dex-cex-spread',
                              name: 'DEX-CEX Spread Strategy',
                              description: 'Profit from temporary price discrepancies between DEXs and CEXs'
                            })}
                            disabled={loading}
                          >
                            {loading ? 'Processing...' : 'Execute'}
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            {/* Market Analysis Section */}
            <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
              <div className="p-4 border-b border-gray-700">
                <h2 className="text-xl font-bold">Rehoboam Market Analysis</h2>
              </div>
              <div className="p-4">
                <div className="bg-gray-700 p-4 rounded-lg">
                  <h3 className="text-lg font-medium mb-2">Current Market Sentiment</h3>
                  <div className="flex items-center mb-4">
                    <div className="w-full bg-gray-800 rounded-full h-4">
                      <div 
                        className={`h-4 rounded-full ${
                          marketAnalysis?.sentiment > 60 ? 'bg-green-600' :
                          marketAnalysis?.sentiment > 40 ? 'bg-yellow-600' : 'bg-red-600'
                        }`} 
                        style={{ width: `${marketAnalysis?.sentiment || 65}%` }}
                      ></div>
                    </div>
                    <span className={`ml-4 font-bold ${
                      marketAnalysis?.sentiment > 60 ? 'text-green-400' :
                      marketAnalysis?.sentiment > 40 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {marketAnalysis?.sentiment > 60 ? 'Bullish' : 
                       marketAnalysis?.sentiment > 40 ? 'Neutral' : 'Bearish'} 
                      ({marketAnalysis?.sentiment || 65}%)
                    </span>
                  </div>
                  <p className="text-gray-300">
                    {marketAnalysis?.analysis || 
                     'Rehoboam AI detects positive momentum on layer 2 networks, with increasing TVL on Arbitrum and Optimism. Recent price action suggests accumulation phase for ETH.'}
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="font-medium mb-2">Key Insights</h3>
                    <ul className="list-disc pl-5 text-gray-300 space-y-1">
                      {marketAnalysis?.insights ? (
                        marketAnalysis.insights.map((insight, index) => (
                          <li key={index}>{insight}</li>
                        ))
                      ) : (
                        <>
                          <li>Increased institutional demand for ETH</li>
                          <li>Growing competition among L2 solutions</li>
                          <li>Declining gas costs improving user experience</li>
                          <li>DeFi TVL growth signals market confidence</li>
                        </>
                      )}
                    </ul>
                  </div>
                  
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <h3 className="font-medium mb-2">Recommendations</h3>
                    <ul className="list-disc pl-5 text-gray-300 space-y-1">
                      {marketAnalysis?.recommendations ? (
                        marketAnalysis.recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))
                      ) : (
                        <>
                          <li>Focus on L2 opportunities with lower fees</li>
                          <li>Consider stablecoin yield strategies during volatility</li>
                          <li>Monitor cross-chain TVL for arbitrage opportunities</li>
                          <li>Implement MEV-resistant trading strategies</li>
                        </>
                      )}
                    </ul>
                  </div>
                </div>
                
                <div className="mt-4 flex justify-end">
                  <button 
                    onClick={loadMarketAnalysis}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded"
                    disabled={loading}
                  >
                    {loading ? 'Refreshing...' : 'Refresh Analysis'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'companions' && (
          <div className="my-8">
            <AICompanionCreator />
          </div>
        )}
        
        {activeTab === 'mcp' && (
          <div className="my-8">
            <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Model Context Protocol Visualizer</h2>
                  <p className="text-gray-400 mb-4">
                    Monitor Rehoboam's AI function generation and execution in real-time. The MCP enables 
                    Rehoboam to create and call specialized functions based on market conditions.
                  </p>
                </div>
                <div className="ml-6">
                  <MCPStatus />
                </div>
              </div>
              <MCPFunctionVisualizer />
            </div>
          </div>
        )}

        {activeTab === 'vetala' && (
          <VetalaProtectionDashboard />
        )}

        {activeTab === 'flash-arbitrage' && (
          <div className="my-8">
            <ProfitableFlashArbitrage />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
