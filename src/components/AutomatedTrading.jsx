import React, { useState, useEffect } from 'react';
import { useWeb3 } from '../contexts/Web3Context';
import { useNotification } from '../contexts/NotificationContext';
import tradingService from '../services/tradingService';

const [loading, setLoading] = useState(true);
const [tradingData, setTradingData] = useState(null);

useEffect(() => {
    const fetchData = async () => {
        // Simulate fetching data
        setTimeout(() => {
            setTradingData({ /* mock data */ });
            setLoading(false);
        }, 1000);
    };
    fetchData();
}, []);

if (loading) {
    return <div>Loading...</div>;
}
const AutomatedTrading = () => {
  const [activeTab, setActiveTab] = useState('manual');
  const [amount, setAmount] = useState('');
  const [token, setToken] = useState('ETH');
  const [action, setAction] = useState('buy');
  const [slippage, setSlippage] = useState('1.0');
  const [network, setNetwork] = useState('ethereum');
  const [aiAssistance, setAiAssistance] = useState(true);
  const [executionSpeed, setExecutionSpeed] = useState('normal');
  const [isProcessing, setIsProcessing] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [isLoadingStrategies, setIsLoadingStrategies] = useState(false);

  const { account, connectWallet } = useWeb3();
  const { addNotification } = useNotification();

  const tokens = ['ETH', 'BTC', 'LINK', 'UMA', 'AAVE', 'XMR', 'HAI', 'MINA'];
  const networks = [
    { id: 'ethereum', name: 'Ethereum', type: 'L1' },
    { id: 'arbitrum', name: 'Arbitrum', type: 'L2 Optimistic' },
    { id: 'optimism', name: 'Optimism', type: 'L2 Optimistic' },
    { id: 'polygon', name: 'Polygon', type: 'L2 Sidechain' },
    { id: 'base', name: 'Base', type: 'L2 Optimistic' },
    { id: 'bsc', name: 'BNB Smart Chain', type: 'L1 EVM Compatible' },
    { id: 'zksync', name: 'zkSync Era', type: 'L2 ZK' },
    { id: 'mina', name: 'Mina Protocol', type: 'L1 Zero Knowledge' },
  ];

  // Load AI trading strategies
  useEffect(() => {
    if (activeTab === 'automated') {
      loadTradingStrategies();
    }
  }, [activeTab, token]);

  const loadTradingStrategies = async () => {
    setIsLoadingStrategies(true);
    try {
      const strategiesData = await tradingService.getStrategies();
      setStrategies(strategiesData);
    } catch (error) {
      console.error('Failed to load strategies:', error);
      addNotification('warning', 'Failed to load AI strategies. Using fallback data.');
      // Fallback strategies
      setStrategies([
        {
          id: 'eth-arbitrum-1',
          name: 'ETH Layer 2 Accumulation',
          description: 'Accumulate ETH on Arbitrum for reduced gas fees',
          confidence: 0.85,
          expectedReturn: 0.04,
          network: 'arbitrum'
        }
      ]);
    } finally {
      setIsLoadingStrategies(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!account) {
      addNotification('error', 'Please connect your wallet first');
      await connectWallet();
      return;
    }

    setIsProcessing(true);
    setConfirmation(null);
    
    try {
      // Execute trade using the API service
      const result = await tradingService.executeTrade({
        action,
        token,
        amount: parseFloat(amount),
        network,
        wallet: account
      });

      if (result.success) {
        setConfirmation({
          success: true,
          message: result.message,
          txHash: result.txHash,
          timestamp: new Date().toISOString()
        });
        addNotification('success', `Trade executed successfully!`);
      } else {
        setConfirmation({
          success: false,
          message: result.message,
          timestamp: new Date().toISOString()
        });
        addNotification('error', result.message);
      }
    } catch (error) {
      console.error('Trade execution error:', error);
      setConfirmation({
        success: false,
        message: 'Failed to execute trade. Please try again.',
        timestamp: new Date().toISOString()
      });
      addNotification('error', 'Trade execution failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setAmount('');
    setToken('ETH');
    setAction('buy');
    setSlippage('1.0');
    setNetwork('ethereum');
    setConfirmation(null);
  };

  const handleNetworkRecommendation = async () => {
    try {
      // Simple network recommendation logic
      const recommendation = {
        recommendedNetwork: parseFloat(amount) > 1000 ? 'arbitrum' : 'ethereum',
        reason: parseFloat(amount) > 1000 ? 'Lower fees for large trades' : 'Most liquidity available'
      };
      
      setNetwork(recommendation.recommendedNetwork);
      addNotification('info', `Recommended: ${recommendation.recommendedNetwork} - ${recommendation.reason}`);
    } catch (error) {
      console.error('Network recommendation failed:', error);
      // Fallback recommendation
      const recommendedNetworks = {
        'ETH': 'arbitrum',
        'BTC': 'optimism',
        'LINK': 'base',
        'UMA': 'zksync',
        'AAVE': 'polygon',
        'XMR': 'ethereum',
        'HAI': 'bsc',     // HAI native on BSC (verified contract)
        'MINA': 'mina',   // MINA native to its zero-knowledge network
      };
      
      setNetwork(recommendedNetworks[token] || 'ethereum');
      addNotification('info', `Using fallback recommendation: ${recommendedNetworks[token] || 'ethereum'}`);
    }
  };

  const executeAIStrategy = async (strategy) => {
    if (!account) {
      addNotification('error', 'Please connect your wallet first');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await tradingService.executeStrategy({
        strategyId: strategy.id,
        token: strategy.token || token,
        amount: 0.1, // Default amount
        action: 'buy', // Default action for strategies
        network: strategy.network || 'arbitrum',
        wallet: account
      });

      if (result.success) {
        addNotification('success', `AI Strategy "${strategy.name}" executed successfully!`);
        setStrategies(strategies.map(s => 
          s.id === strategy.id 
            ? { ...s, executed: true, executedAt: new Date().toISOString() } 
            : s
        ));
      } else {
        addNotification('error', `Strategy execution failed: ${result.message}`);
      }
    } catch (error) {
      console.error('AI strategy execution error:', error);
      addNotification('error', 'Failed to execute AI strategy');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <div className="mb-6">
        <div className="flex border-b border-gray-700">
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'manual' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-400'}`}
            onClick={() => setActiveTab('manual')}
          >
            Manual Trading
          </button>
          <button
            className={`py-2 px-4 font-medium ${activeTab === 'automated' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-400'}`}
            onClick={() => setActiveTab('automated')}
          >
            AI-Powered Automation
          </button>
        </div>
      </div>
      
      {activeTab === 'manual' ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-gray-400 mb-2">Token</label>
              <select
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              >
                {tokens.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-gray-400 mb-2">Amount</label>
              <input
                type="text"
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                placeholder="Enter amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-gray-400 mb-2">Action</label>
              <select
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                value={action}
                onChange={(e) => setAction(e.target.value)}
              >
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
                <option value="swap">Swap</option>
                <option value="stake">Stake</option>
                <option value="unstake">Unstake</option>
              </select>
            </div>
            
            <div>
              <label className="block text-gray-400 mb-2">Slippage Tolerance (%)</label>
              <input
                type="text"
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                placeholder="1.0"
                value={slippage}
                onChange={(e) => setSlippage(e.target.value)}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-gray-400">Network</label>
                <button
                  type="button"
                  onClick={handleNetworkRecommendation}
                  className="text-blue-400 text-sm hover:underline"
                >
                  Recommend network
                </button>
              </div>
              <select
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                value={network}
                onChange={(e) => setNetwork(e.target.value)}
              >
                {networks.map(net => (
                  <option key={net.id} value={net.id}>
                    {net.name} ({net.type})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-gray-400 mb-2">Execution Speed</label>
              <select
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                value={executionSpeed}
                onChange={(e) => setExecutionSpeed(e.target.value)}
              >
                <option value="fast">Fast (Higher fees)</option>
                <option value="normal">Normal</option>
                <option value="slow">Slow (Lower fees)</option>
              </select>
            </div>
          </div>
          
          <div className="flex items-center my-4">
            <label className="flex items-center cursor-pointer">
              <div className="relative">
                <input 
                  type="checkbox" 
                  checked={aiAssistance} 
                  onChange={() => setAiAssistance(!aiAssistance)}
                  className="sr-only" 
                />
                <div className={`block w-14 h-8 rounded-full ${aiAssistance ? 'bg-blue-600' : 'bg-gray-600'}`}></div>
                <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition transform ${aiAssistance ? 'translate-x-6' : ''}`}></div>
              </div>
              <span className="ml-3 text-gray-300">
                AI Trading Assistance
              </span>
            </label>
          </div>
          
          {aiAssistance && (
            <div className="bg-gray-700 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-2">
                <div className="w-3 h-3 rounded-full bg-blue-500 mr-2 animate-pulse"></div>
                <h3 className="font-bold">AI Trading Insights</h3>
              </div>
              <div className="text-sm">
                <p className="mb-1">
                  <span className="text-blue-400">Layer 2 optimization:</span> {network !== 'ethereum' ? 
                    `Using ${networks.find(n => n.id === network)?.name} can reduce gas fees by up to 90%` : 
                    'Consider using Layer 2 for reduced fees'}
                </p>
                {token === 'ETH' && (
                  <p className="mb-1">
                    <span className="text-blue-400">Market sentiment:</span> Bullish signals detected in the last 24 hours
                  </p>
                )}
                {action === 'buy' && (
                  <p className="mb-1">
                    <span className="text-blue-400">Entry point:</span> Current price is 4% above 30-day moving average
                  </p>
                )}
                <p className="mb-1">
                  <span className="text-blue-400">Gas optimization:</span> Set execution to 'slow' to save up to 25% on gas
                </p>
              </div>
            </div>
          )}
          
          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={isProcessing}
              className={`px-6 py-2 rounded-lg font-medium ${
                isProcessing ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isProcessing ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                `Execute ${action}`
              )}
            </button>
            
            <button
              type="button"
              onClick={handleReset}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium"
            >
              Reset
            </button>
          </div>
        </form>
      ) : (
        <div className="bg-gray-700 rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">AI Automated Trading</h3>
          <p className="mb-6 text-gray-300">
            The AI trading automation feature utilizes Rehoboam's market analysis to execute trades based on your risk profile and preferences.
          </p>
          
          <div className="space-y-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <h4 className="font-medium mb-2">Market Sentiment Analysis</h4>
                <p className="text-sm text-gray-400">Rehoboam continuously monitors market sentiment across multiple sources to identify opportunities.</p>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-4">
                <h4 className="font-medium mb-2">Layer 2 Gas Optimization</h4>
                <p className="text-sm text-gray-400">Automatically selects the most cost-efficient network for each transaction.</p>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-4">
                <h4 className="font-medium mb-2">Multi-Model Orchestration</h4>
                <p className="text-sm text-gray-400">Uses Gemini 2.5 Pro for strategy, DeepSeek for analysis, and GPT-4o mini for anomaly detection.</p>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-4">
                <h4 className="font-medium mb-2">Dynamic Risk Management</h4>
                <p className="text-sm text-gray-400">Adjusts position sizes and entry/exit points based on market volatility and conditions.</p>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 border-l-4 border-yellow-500">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-yellow-500 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="font-medium">Advanced Feature - Coming Soon</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    AI-powered automated trading requires additional configuration. Please check back soon or use manual trading with AI assistance.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <button
            onClick={() => setActiveTab('manual')}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
          >
            Use Manual Trading
          </button>
        </div>
      )}
      
      {confirmation && (
        <div className={`mt-6 rounded-lg p-4 border ${confirmation.success ? 'border-green-500 bg-green-900 bg-opacity-20' : 'border-red-500 bg-red-900 bg-opacity-20'}`}>
          <div className="flex items-start">
            {confirmation.success ? (
              <svg className="w-5 h-5 text-green-500 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-red-500 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            )}
            <div>
              <h4 className="font-medium">{confirmation.success ? 'Transaction Successful' : 'Transaction Failed'}</h4>
              <p className="text-sm mt-1">{confirmation.message}</p>
              {confirmation.txHash && (
                <p className="text-xs text-gray-400 mt-1">
                  Transaction Hash: <span className="font-mono">{confirmation.txHash.substring(0, 10)}...{confirmation.txHash.substring(58)}</span>
                </p>
              )}
              <p className="text-xs text-gray-400 mt-1">
                {new Date(confirmation.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AutomatedTrading;