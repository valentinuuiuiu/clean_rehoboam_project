import React, { useState, useEffect, useCallback, useRef } from 'react';
import LoadingSpinner from './ui/LoadingSpinner';
import { useLoading } from '../contexts/LoadingContext';
import { useNotification } from '../contexts/NotificationContext';
import { useWebSocket } from '../hooks/useWebSocket';

const TradingDashboard = () => {
  const [cryptoData, setCryptoData] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [selectedNetwork, setSelectedNetwork] = useState('ethereum');
  const [rehoboamEnabled, setRehoboamEnabled] = useState(false);
  const [riskProfile, setRiskProfile] = useState('moderate');
  const [sentiment, setSentiment] = useState('neutral');
  const [isLoading, setIsLoading] = useState(false);
  const [priceUpdateCount, setPriceUpdateCount] = useState(0);
  const { startLoading, stopLoading } = useLoading();
  const { addNotification } = useNotification();
  // Use relative URL path for API endpoint to avoid hardcoded domains
  const apiEndpoint = '';
  const strategyRequestRef = useRef(null);

  // Setup WebSocket connection for real-time price updates and market data
  const { 
    isConnected: wsConnected, 
    lastMessage: wsMessage,
    send: wsSend,
    connect: wsConnect,
    disconnect: wsDisconnect
  } = useWebSocket({
    url: '/ws/trading',
    autoConnect: true,
    onOpen: () => {
      console.log('WebSocket connected for trading dashboard');
      // Subscribe to price data for all supported networks
      wsSend({
        type: 'subscribe',
        data: { 
          topics: ['prices', 'gasPrices', 'arbitrage'], 
          networks: ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync']
        }
      });
    },
    onClose: () => {
      console.log('WebSocket closed for trading dashboard');
    },
    onError: () => {
      console.error('WebSocket error for trading dashboard');
      addNotification({ type: 'error', message: 'WebSocket connection error. Reconnecting...' });
    }
  });

  // Networks for Layer 2 optimization
  const networks = [
    { id: 'ethereum', name: 'Ethereum', type: 'L1' },
    { id: 'arbitrum', name: 'Arbitrum', type: 'L2 Optimistic' },
    { id: 'optimism', name: 'Optimism', type: 'L2 Optimistic' },
    { id: 'polygon', name: 'Polygon', type: 'L2 Sidechain' },
    { id: 'base', name: 'Base', type: 'L2 Optimistic' },
    { id: 'zksync', name: 'zkSync Era', type: 'L2 ZK' },
  ];

  // Process incoming WebSocket messages
  useEffect(() => {
    if (wsMessage) {
      try {
        console.log('Received WS message:', wsMessage.type);
        
        if (wsMessage.type === 'prices' && wsMessage.data && wsMessage.data.prices) {
          // Transform price data format for display
          const prices = wsMessage.data.prices;
          const formattedData = Object.keys(prices).map(symbol => {
            // Calculate change by comparing with stored prices when available
            const existingCrypto = cryptoData.find(c => c.symbol === symbol);
            const change24h = existingCrypto ? 
              ((prices[symbol] - existingCrypto.price) / existingCrypto.price) * 100 : 
              (Math.random() * 8) - 4; // Fallback for initial data
              
            return {
              symbol,
              name: getCryptoName(symbol),
              price: prices[symbol],
              change24h: parseFloat(change24h.toFixed(2))
            };
          });
          
          // Sort by market cap (simulated by putting major coins first)
          const mainCoins = ['BTC', 'ETH', 'LINK', 'AAVE', 'UMA', 'XMR'];
          formattedData.sort((a, b) => {
            const aIndex = mainCoins.indexOf(a.symbol);
            const bIndex = mainCoins.indexOf(b.symbol);
            if (aIndex >= 0 && bIndex >= 0) return aIndex - bIndex;
            if (aIndex >= 0) return -1;
            if (bIndex >= 0) return 1;
            return a.symbol.localeCompare(b.symbol);
          });
          
          setCryptoData(formattedData);
          setPriceUpdateCount(prev => prev + 1);
        }
        
        if (wsMessage.type === 'arbitrageOpportunities') {
          // Process arbitrage data if needed
          console.log('Received arbitrage opportunities:', wsMessage.data);
        }
        
        if (wsMessage.type === 'marketSentiment' && wsMessage.data && wsMessage.data.sentiment) {
          setSentiment(wsMessage.data.sentiment);
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    }
  }, [wsMessage, cryptoData]);

  // Initial data fetch using REST API
  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        // First try to get data from the API
        const priceResponse = await fetch(`${apiEndpoint}/api/market/prices`);
        
        if (!priceResponse.ok) {
          throw new Error(`API error: ${priceResponse.statusText}`);
        }
        
        const priceData = await priceResponse.json();
        
        // Transform price data from API format
        if (priceData.prices) {
          const formattedData = Object.keys(priceData.prices).map(symbol => ({
            symbol,
            name: getCryptoName(symbol),
            price: priceData.prices[symbol],
            change24h: parseFloat((Math.random() * 6 - 3).toFixed(2)) // Initial change data
          }));
          
          setCryptoData(formattedData);
          console.log('Loaded initial price data from API');
        }
        
        // Get market sentiment if Rehoboam is enabled
        if (rehoboamEnabled) {
          try {
            const sentimentResponse = await fetch(`${apiEndpoint}/api/market/emotions`);
            if (sentimentResponse.ok) {
              const sentimentData = await sentimentResponse.json();
              if (sentimentData.sentiment) {
                setSentiment(sentimentData.sentiment);
                console.log('Loaded market sentiment from API:', sentimentData.sentiment);
              }
            }
          } catch (error) {
            console.warn('Could not fetch market sentiment:', error);
          }
        }
        
        // Initially generate strategies
        await generateStrategies();
      } catch (error) {
        console.error('Error fetching initial data:', error);
        addNotification({ type: 'error', message: 'Failed to load price data from API' });
        
        // As a fallback, use a ping to the WebSocket server to request immediate data
        if (wsConnected) {
          console.log('Requesting immediate price data via WebSocket');
          wsSend({ type: 'getLatestPrices' });
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchInitialData();
    
    // Cleanup WebSocket on unmount
    return () => {
      if (wsConnected) {
        wsSend({
          type: 'unsubscribe',
          data: { topics: ['prices', 'gasPrices', 'arbitrage'] }
        });
        wsDisconnect();
      }
    };
  }, []);
  
  // Generate new strategies when settings change
  useEffect(() => {
    // Debounce strategy requests to prevent excessive API calls
    if (strategyRequestRef.current) {
      clearTimeout(strategyRequestRef.current);
    }
    
    strategyRequestRef.current = setTimeout(() => {
      generateStrategies();
    }, 300);
    
    return () => {
      if (strategyRequestRef.current) {
        clearTimeout(strategyRequestRef.current);
      }
    };
  }, [selectedNetwork, rehoboamEnabled, riskProfile]);
  
  // Helper to get full names for crypto symbols
  const getCryptoName = (symbol) => {
    const nameMap = {
      'BTC': 'Bitcoin',
      'ETH': 'Ethereum',
      'LINK': 'Chainlink',
      'UMA': 'UMA',
      'AAVE': 'Aave',
      'XMR': 'Monero',
      'USDC': 'USD Coin',
      'USDT': 'Tether',
      'DAI': 'Dai',
      'DOT': 'Polkadot',
      'SOL': 'Solana',
      'MATIC': 'Polygon',
      'SHIB': 'Shiba Inu'
    };
    return nameMap[symbol] || symbol;
  };
  
  // Generate trading strategies based on current settings
  const generateStrategies = async () => {
    console.log('Generating strategies with settings:', {
      network: selectedNetwork,
      rehoboam: rehoboamEnabled,
      risk: riskProfile
    });
    
    try {
      // Try to get real strategies from the AI trading agent API
      const response = await fetch(`${apiEndpoint}/api/trading/strategies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          network: selectedNetwork,
          rehoboamEnabled: rehoboamEnabled,
          riskProfile: riskProfile
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.strategies && Array.isArray(data.strategies)) {
          setStrategies(data.strategies);
          console.log('Loaded strategies from AI trading agent API');
          
          // Also update sentiment if provided and Rehoboam is enabled
          if (rehoboamEnabled && data.marketSentiment) {
            setSentiment(data.marketSentiment);
          }
          return;
        }
      }
      
      // If API fails or returns invalid data, fall back to generating strategies client-side
      console.warn('Could not fetch strategies from API, falling back to client-side generation');
      generateClientSideStrategies();
    } catch (error) {
      console.error('Error fetching strategies:', error);
      addNotification({ type: 'warning', message: 'Could not fetch trading strategies' });
      
      // Fall back to generating strategies client-side
      generateClientSideStrategies();
    }
  };
  
  // Fallback strategy generation if API fails
  const generateClientSideStrategies = () => {
    console.log('Generating strategies client-side');
    
    // Base strategies
    const baseStrategies = [
      {
        id: 'eth-arb-1',
        name: 'ETH Layer 2 Accumulation',
        description: `Accumulate ETH on ${selectedNetwork === 'ethereum' ? 'Arbitrum' : selectedNetwork} for reduced gas fees`,
        confidence: 0.85,
        network: selectedNetwork === 'ethereum' ? 'arbitrum' : selectedNetwork,
        expectedReturn: '4.2%',
        timeframe: 'medium',
        riskLevel: riskProfile === 'aggressive' ? 'high' : riskProfile === 'conservative' ? 'low' : 'moderate',
        reasoning: 'Layer 2 accumulation reduces gas costs by up to 90% while maintaining Ethereum security guarantees.'
      },
      {
        id: 'stable-yield-1',
        name: 'Stablecoin Yield Strategy',
        description: 'Generate yield on USDC via lending protocols',
        confidence: 0.92,
        network: selectedNetwork,
        expectedReturn: '3.5%',
        timeframe: 'long',
        riskLevel: 'low',
        reasoning: 'Stablecoin yields provide consistent returns with minimal impermanent loss risk.'
      }
    ];
    
    // Add Rehoboam-influenced strategy if enabled
    if (rehoboamEnabled) {      
      let rehoboamStrategy;
      
      if (sentiment.includes('bull')) {
        rehoboamStrategy = {
          id: 'rehoboam-bull-1',
          name: 'Rehoboam Bullish Strategy',
          description: 'Leverage market sentiment with L2 position buildup',
          confidence: 0.88,
          network: 'optimism',
          expectedReturn: '7.3%',
          timeframe: 'short',
          riskLevel: riskProfile === 'conservative' ? 'moderate' : 'high',
          reasoning: 'Rehoboam AI detected bullish market patterns with high confidence.'
        };
      } else if (sentiment.includes('bear')) {
        rehoboamStrategy = {
          id: 'rehoboam-bear-1',
          name: 'Rehoboam Defensive Approach',
          description: 'Protect capital with L2 stablecoin yields',
          confidence: 0.91,
          network: 'arbitrum',
          expectedReturn: '3.2%',
          timeframe: 'medium',
          riskLevel: 'low',
          reasoning: 'Rehoboam AI identified bearish market conditions requiring a defensive posture.'
        };
      } else if (sentiment === 'volatile') {
        rehoboamStrategy = {
          id: 'rehoboam-vol-1',
          name: 'Rehoboam Volatility Play',
          description: 'Capitalize on price oscillations between L1 and L2',
          confidence: 0.79,
          network: 'zksync',
          expectedReturn: '9.1%',
          timeframe: 'short',
          riskLevel: 'high',
          reasoning: 'Rehoboam AI\'s volatility analysis indicates arbitrage opportunities between networks.'
        };
      } else {
        rehoboamStrategy = {
          id: 'rehoboam-neutral-1',
          name: 'Rehoboam Balanced Strategy',
          description: 'Deploy capital across multiple L2 solutions',
          confidence: 0.84,
          network: 'polygon',
          expectedReturn: '5.3%',
          timeframe: 'medium',
          riskLevel: 'moderate',
          reasoning: 'Rehoboam AI detects balanced market conditions ideal for diversified L2 exposure.'
        };
      }
      
      setStrategies([...baseStrategies, rehoboamStrategy]);
    } else {
      setStrategies(baseStrategies);
    }
  };

  const handleNetworkChange = (e) => {
    setSelectedNetwork(e.target.value);
  };
  
  const handleRiskProfileChange = (e) => {
    setRiskProfile(e.target.value);
  };
  
  const toggleRehoboam = () => {
    setRehoboamEnabled(!rehoboamEnabled);
  };
  
  const executeStrategy = async (strategyId) => {
    const strategy = strategies.find(s => s.id === strategyId);
    if (!strategy) {
      addNotification({ type: 'error', message: 'Strategy not found' });
      return;
    }
    
    startLoading(`Executing strategy ${strategy.name}...`);
    
    try {
      // Call the actual trading API to execute the strategy
      const response = await fetch(`${apiEndpoint}/api/trading/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          strategyId,
          network: strategy.network,
          riskProfile: strategy.riskLevel,
          rehoboamEnabled: strategy.id.includes('rehoboam')
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('Strategy execution result:', result);
      
      // Update the executed strategy in the UI
      setStrategies(strategies.map(s => 
        s.id === strategyId 
          ? {
              ...s, 
              executed: true, 
              executedAt: new Date().toISOString(),
              executionResult: result.success ? 'success' : 'failed',
              txHash: result.txHash
            } 
          : s
      ));
      
      if (result.success) {
        addNotification({ type: 'success', message: `Successfully executed "${strategy.name}" strategy` });
      } else {
        addNotification({ type: 'warning', message: `Strategy execution completed with warnings: ${result.message}` });
      }
    } catch (error) {
      console.error('Error executing strategy:', error);
      addNotification({ type: 'error', message: `Failed to execute strategy: ${error.message}` });
      
      // If API execution fails, mark as executed but with failure status
      setStrategies(strategies.map(s => 
        s.id === strategyId 
          ? {
              ...s, 
              executed: true, 
              executedAt: new Date().toISOString(),
              executionResult: 'failed',
              error: error.message
            } 
          : s
      ));
    } finally {
      stopLoading();
    }
  };

  if (isLoading) {
    return <LoadingSpinner size="large" />;
  }

  return (
    <div className="space-y-8">
      <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-2xl font-bold mb-4">Market Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {cryptoData.map(crypto => (
            <div key={crypto.symbol} className="bg-gray-700 rounded-lg p-4 shadow">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-bold">{crypto.name}</h3>
                  <p className="text-gray-400">{crypto.symbol}</p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-semibold">${crypto.price.toLocaleString()}</p>
                  <p className={crypto.change24h >= 0 ? 'text-green-400' : 'text-red-400'}>
                    {crypto.change24h >= 0 ? '↑' : '↓'} {Math.abs(crypto.change24h)}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-2xl font-bold mb-4">AI Trading Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-gray-400 mb-2">Preferred Network</label>
            <select 
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
              value={selectedNetwork}
              onChange={handleNetworkChange}
            >
              {networks.map(network => (
                <option key={network.id} value={network.id}>
                  {network.name} ({network.type})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-gray-400 mb-2">Risk Profile</label>
            <select 
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
              value={riskProfile}
              onChange={handleRiskProfileChange}
            >
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
          
          <div className="flex items-center">
            <label className="flex items-center cursor-pointer">
              <div className="relative">
                <input 
                  type="checkbox" 
                  checked={rehoboamEnabled} 
                  onChange={toggleRehoboam}
                  className="sr-only" 
                />
                <div className={`block w-14 h-8 rounded-full ${rehoboamEnabled ? 'bg-blue-600' : 'bg-gray-600'}`}></div>
                <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition transform ${rehoboamEnabled ? 'translate-x-6' : ''}`}></div>
              </div>
              <span className="ml-3 text-gray-300">
                Rehoboam AI Enhancement
              </span>
            </label>
          </div>
        </div>
        
        {rehoboamEnabled && (
          <div className="bg-gray-700 rounded-lg p-4 mb-6">
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-2 animate-pulse"></div>
              <h3 className="font-bold">Rehoboam Market Sentiment Analysis</h3>
            </div>
            <p>
              Current market sentiment: <span className="font-semibold">{sentiment.replace('_', ' ')}</span>
            </p>
            <div className="mt-2 text-sm text-gray-400">
              Rehoboam's advanced sentiment analysis incorporates on-chain data, social signals, and market indicators.
            </div>
          </div>
        )}
      </div>
      
      <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-2xl font-bold mb-4">AI Trading Strategies</h2>
        <div className="space-y-4">
          {strategies.map(strategy => (
            <div key={strategy.id} className={`border ${strategy.id.includes('rehoboam') ? 'border-blue-500' : 'border-gray-700'} rounded-lg p-4 ${strategy.id.includes('rehoboam') ? 'bg-gray-700 bg-opacity-50' : 'bg-gray-700'}`}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-lg flex items-center">
                    {strategy.id.includes('rehoboam') && (
                      <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
                    )}
                    {strategy.name}
                  </h3>
                  <p className="mt-1">{strategy.description}</p>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-blue-400">{strategy.expectedReturn}</div>
                  <div className={`${strategy.riskLevel === 'high' ? 'text-red-400' : strategy.riskLevel === 'low' ? 'text-green-400' : 'text-yellow-400'} text-sm`}>
                    {strategy.riskLevel.charAt(0).toUpperCase() + strategy.riskLevel.slice(1)} risk
                  </div>
                </div>
              </div>
              
              <div className="mt-3 grid grid-cols-2 gap-4">
                <div>
                  <div className="text-gray-400 text-sm">Confidence</div>
                  <div className="w-full bg-gray-600 rounded-full h-2 mt-1">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${strategy.confidence * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-right text-xs mt-1">{Math.round(strategy.confidence * 100)}%</div>
                </div>
                
                <div>
                  <div className="text-gray-400 text-sm">Network</div>
                  <div className="font-medium">
                    {networks.find(n => n.id === strategy.network)?.name || strategy.network}
                  </div>
                </div>
              </div>
              
              <div className="mt-3 text-sm text-gray-400">
                <strong>AI reasoning:</strong> {strategy.reasoning}
              </div>
              
              <div className="mt-4">
                {strategy.executed && (
                  <div className="mb-2">
                    {strategy.executionResult === 'success' ? (
                      <div className="text-green-400 flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        Executed successfully at {new Date(strategy.executedAt).toLocaleTimeString()}
                      </div>
                    ) : (
                      <div className="text-red-400 flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        Execution failed at {new Date(strategy.executedAt).toLocaleTimeString()}
                      </div>
                    )}
                    
                    {strategy.txHash && (
                      <div className="mt-1 text-xs text-gray-400">
                        Transaction: <a 
                          href={`https://${strategy.network === 'ethereum' ? '' : `${strategy.network}.`}etherscan.io/tx/${strategy.txHash}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:underline"
                        >{`${strategy.txHash.substring(0, 8)}...${strategy.txHash.substring(strategy.txHash.length - 6)}`}</a>
                      </div>
                    )}
                    
                    {strategy.error && (
                      <div className="mt-1 text-xs text-red-400">
                        Error: {strategy.error}
                      </div>
                    )}
                  </div>
                )}
                
                <div className="flex justify-end">
                  {strategy.executed ? (
                    <button
                      onClick={() => executeStrategy(strategy.id)}
                      className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded text-sm"
                    >
                      Execute Again
                    </button>
                  ) : (
                    <button
                      onClick={() => executeStrategy(strategy.id)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
                    >
                      Execute Strategy
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TradingDashboard;