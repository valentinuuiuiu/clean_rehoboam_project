import React, { useState, useEffect } from 'react';
import { useAITradingService } from '../hooks/useAITradingService';

const AITradingPanel = () => {
  const [activeToken, setActiveToken] = useState('ETH');
  const [riskProfile, setRiskProfile] = useState('moderate');
  const [autoTrade, setAutoTrade] = useState(false);
  const [rehoboamEnabled, setRehoboamEnabled] = useState(false);
  const [networkPreferences, setNetworkPreferences] = useState({
    ethereum: 0.5,
    arbitrum: 0.8,
    optimism: 0.7,
    polygon: 0.6,
    base: 0.9,
    zksync: 0.8
  });

  // This would be connected to actual AI settings in production
  const confidenceThreshold = 0.75;

  // Connect to AI trading service
  const {
    isConnected,
    marketData,
    tradeHistory,
    arbitrageOpportunities,
    strategies,
    getStrategies,
    executeStrategy,
    isLoading
  } = useAITradingService({
    autoConnect: true,
    onMarketUpdate: (data) => console.log('Market update received', data),
    onTradeComplete: (result) => console.log('Trade completed', result),
    onArbitrageUpdate: (opportunities) => console.log('Arbitrage update', opportunities),
    onStrategiesUpdate: (strategies) => console.log('Strategies update', strategies)
  });

  // Format currency values
  const formatCurrency = (value, decimals = 2) => {
    if (value === undefined || value === null) return '-';
    
    // Handle very small values (like SHIB)
    if (Math.abs(value) < 0.001) {
      return value.toExponential(6);
    }
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };

  // Format percentages
  const formatPercentage = (value) => {
    if (value === undefined || value === null) return '-';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  // Generate badge for AI confidence
  const confidenceBadge = (confidence) => {
    if (!confidence && confidence !== 0) return null;
    
    let colorClass;
    if (confidence >= 0.8) {
      colorClass = 'bg-green-500';
    } else if (confidence >= 0.6) {
      colorClass = 'bg-yellow-500';
    } else {
      colorClass = 'bg-red-500';
    }
    
    return (
      <span className={`text-xs font-medium ${colorClass} text-white py-1 px-2 rounded-full`}>
        {Math.round(confidence * 100)}%
      </span>
    );
  };
  
  // Get strategy color based on expected return
  const getStrategyColor = (expectedReturn) => {
    if (expectedReturn >= 0.08) return 'border-green-500 bg-green-950';
    if (expectedReturn >= 0.04) return 'border-yellow-500 bg-yellow-950';
    return 'border-blue-500 bg-blue-950';
  };

  // Generate AI recommendation card
  const renderRecommendationCard = (token) => {
    if (!marketData?.prices?.[token]?.ai) {
      return (
        <div className="border border-gray-700 rounded-lg p-4 mb-4">
          <p className="text-gray-400">No AI analysis available for {token}</p>
        </div>
      );
    }
    
    const analysis = marketData.prices[token].ai;
    const price = marketData.prices[token].price;
    
    return (
      <div className="border border-gray-700 rounded-lg p-4 mb-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="text-xl font-bold">{token} Analysis</h3>
            <p className="text-gray-400 text-sm">Current Price: {formatCurrency(price)}</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">AI Confidence:</span>
            {confidenceBadge(analysis.confidence)}
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-800 rounded p-3">
            <p className="text-gray-400 text-sm">Recommendation</p>
            <p className={`text-lg font-semibold ${
              analysis.recommendation === 'buy' ? 'text-green-400' : 
              analysis.recommendation === 'sell' ? 'text-red-400' : 'text-yellow-400'
            }`}>
              {analysis.recommendation?.toUpperCase()}
            </p>
          </div>
          
          <div className="bg-gray-800 rounded p-3">
            <p className="text-gray-400 text-sm">Market Sentiment</p>
            <p className="text-lg font-semibold">
              {analysis.sentiment > 0.2 ? 'Bullish' : 
               analysis.sentiment < -0.2 ? 'Bearish' : 'Neutral'}
            </p>
          </div>
          
          {analysis.prediction && (
            <>
              <div className="bg-gray-800 rounded p-3">
                <p className="text-gray-400 text-sm">24h Prediction</p>
                <p className="text-lg font-semibold">
                  {formatCurrency(analysis.prediction.price_24h)}
                </p>
              </div>
              
              <div className="bg-gray-800 rounded p-3">
                <p className="text-gray-400 text-sm">Support/Resistance</p>
                <p className="text-lg font-semibold">
                  {formatCurrency(analysis.prediction.support)} / {formatCurrency(analysis.prediction.resistance)}
                </p>
              </div>
            </>
          )}
        </div>

        {analysis.arbitrage && (
          <div className="bg-gray-800 rounded p-3 mb-4">
            <div className="flex justify-between items-center">
              <p className="text-sm font-semibold text-green-400">Arbitrage Opportunity</p>
              {confidenceBadge(analysis.arbitrage.confidence)}
            </div>
            <p className="text-gray-300 mt-1">
              Buy on {analysis.arbitrage.buyNetwork}, sell on {analysis.arbitrage.sellNetwork}
            </p>
            <p className="text-green-400 font-semibold mt-1">
              Potential profit: {formatPercentage(analysis.arbitrage.profit * 100)}
            </p>
          </div>
        )}
        
        <button 
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
          onClick={() => executeStrategy(token, analysis.recommendation, analysis.confidence)}
          disabled={isLoading}
        >
          {isLoading ? 'Processing...' : 'Execute AI Strategy'}
        </button>
      </div>
    );
  };

  // Fetch strategies when token or risk profile changes
  useEffect(() => {
    if (isConnected) {
      getStrategies(activeToken, riskProfile);
    }
  }, [activeToken, riskProfile, isConnected, getStrategies]);
  
  // Render AI trading strategies section
  const renderTradingStrategies = () => {
    // Use real strategies from the trading agent
    const strategiesList = strategies || [];
    
    return (
      <div className="mt-6">
        <h3 className="text-xl font-bold mb-4">AI Trading Strategies</h3>
        <div className="grid grid-cols-1 gap-4">
          {strategiesList.length === 0 ? (
            <p className="text-gray-400 text-sm">No strategies available for the selected token and risk profile.</p>
          ) : (
            strategiesList
              .filter(s => riskProfile === 'aggressive' || (s.risk_level || s.riskLevel) !== 'high')
              .filter(s => activeToken === 'All' || s.token === activeToken || (s.networks && s.networks.includes(activeToken)))
              .map(strategy => (
                <div 
                  key={strategy.id}
                  className={`border ${getStrategyColor(strategy.expected_return || strategy.expectedReturn)} rounded-lg p-4 relative`}
                >
                  {strategy.rehoboam && (
                    <div className="absolute -top-2 -right-2 bg-purple-600 text-white text-xs py-1 px-2 rounded-full">
                      Rehoboam
                    </div>
                  )}
                  
                  <div className="flex justify-between mb-2">
                    <h4 className="font-semibold">{strategy.name}</h4>
                    {confidenceBadge(strategy.confidence)}
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3">{strategy.description || strategy.reasoning}</p>
                  
                  <div className="grid grid-cols-3 gap-2 mb-3 text-sm">
                    <div>
                      <p className="text-gray-500">Expected Return</p>
                      <p className="text-green-400 font-semibold">
                        {formatPercentage((strategy.expected_return || strategy.expectedReturn) * 100)}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-gray-500">Risk Level</p>
                      <p className={`font-semibold ${
                        (strategy.risk_level || strategy.riskLevel) === 'high' ? 'text-red-400' :
                        (strategy.risk_level || strategy.riskLevel) === 'moderate' ? 'text-yellow-400' :
                        'text-green-400'
                      }`}>
                        {(strategy.risk_level || strategy.riskLevel).charAt(0).toUpperCase() + 
                         (strategy.risk_level || strategy.riskLevel).slice(1)}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-gray-500">Timeframe</p>
                      <p className="font-semibold">
                        {(strategy.timeframe || 'medium').charAt(0).toUpperCase() + 
                         (strategy.timeframe || 'medium').slice(1)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap space-x-2 mb-3">
                    {strategy.networks && strategy.networks.map(network => (
                      <span key={network} className="text-xs bg-gray-700 rounded-full px-2 py-1 mb-1">
                        {network.charAt(0).toUpperCase() + network.slice(1)}
                      </span>
                    ))}
                    
                    {strategy.token && (
                      <span className="text-xs bg-blue-900 rounded-full px-2 py-1 mb-1">
                        {strategy.token}
                      </span>
                    )}
                    
                    {strategy.tokens && strategy.tokens.map(token => (
                      <span key={token} className="text-xs bg-blue-900 rounded-full px-2 py-1 mb-1">
                        {token}
                      </span>
                    ))}
                  </div>
                  
                  <button 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
                    onClick={() => executeStrategy(strategy.id)}
                    disabled={isLoading}
                  >
                    {isLoading ? 'Processing...' : 'Execute Strategy'}
                  </button>
                </div>
              ))
          )}
        </div>
      </div>
    );
  };

  // Render network preference sliders
  const renderNetworkPreferences = () => {
    return (
      <div className="mt-6 border border-gray-700 rounded-lg p-4">
        <h3 className="text-xl font-bold mb-4">Layer 2 Network Preferences</h3>
        <p className="text-sm text-gray-400 mb-4">
          Adjust your preferences for Layer 2 networks to customize AI trading behavior
        </p>
        
        <div className="space-y-4">
          {Object.entries(networkPreferences).map(([network, value]) => (
            <div key={network}>
              <div className="flex justify-between mb-1">
                <label className="text-sm font-medium capitalize">{network}</label>
                <span className="text-sm text-gray-400">{Math.round(value * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={value}
                onChange={(e) => setNetworkPreferences({
                  ...networkPreferences,
                  [network]: parseFloat(e.target.value)
                })}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-gray-900 text-white p-4 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">AI Trading Agent</h2>
        <div className="flex items-center space-x-2">
          <span className={`inline-block w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-3 flex-1">
          <p className="text-sm text-gray-400">Token</p>
          <select 
            value={activeToken}
            onChange={(e) => setActiveToken(e.target.value)}
            className="bg-gray-700 text-white rounded-lg p-2 w-full mt-1"
          >
            <option value="ETH">Ethereum (ETH)</option>
            <option value="BTC">Bitcoin (BTC)</option>
            <option value="LINK">Chainlink (LINK)</option>
            <option value="UMA">UMA Protocol (UMA)</option>
            <option value="AAVE">Aave (AAVE)</option>
            <option value="XMR">Monero (XMR)</option>
            <option value="SHIB">Shiba Inu (SHIB)</option>
            <option value="All">All Tokens</option>
          </select>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-3 flex-1">
          <p className="text-sm text-gray-400">Risk Profile</p>
          <select 
            value={riskProfile}
            onChange={(e) => setRiskProfile(e.target.value)}
            className="bg-gray-700 text-white rounded-lg p-2 w-full mt-1"
          >
            <option value="conservative">Conservative</option>
            <option value="moderate">Moderate</option>
            <option value="aggressive">Aggressive</option>
          </select>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 flex-1">
          <div className="flex items-center justify-between">
            <p className="font-semibold">Auto-Trading</p>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                className="sr-only peer"
                checked={autoTrade}
                onChange={() => setAutoTrade(!autoTrade)}
              />
              <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          <p className="text-sm text-gray-400 mt-2">
            {autoTrade ? 'AI will automatically execute trades based on analysis' : 'Manual approval required for all trades'}
          </p>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 flex-1">
          <div className="flex items-center justify-between">
            <p className="font-semibold">Rehoboam AI</p>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                className="sr-only peer"
                checked={rehoboamEnabled}
                onChange={() => setRehoboamEnabled(!rehoboamEnabled)}
              />
              <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-focus:ring-4 peer-focus:ring-purple-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
          <p className="text-sm text-gray-400 mt-2">
            {rehoboamEnabled ? 'Advanced AI features enabled for predictive trading' : 'Standard AI features only'}
          </p>
        </div>
      </div>
      
      {/* Main panel with AI recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          {renderRecommendationCard(activeToken !== 'All' ? activeToken : 'ETH')}
        </div>
        
        <div>
          {/* Connected to actual service in production */}
          <div className="border border-gray-700 rounded-lg p-4 mb-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xl font-bold">Confidence Settings</h3>
              {confidenceBadge(confidenceThreshold)}
            </div>
            
            <p className="text-sm text-gray-400 mb-4">
              AI will only execute trades when confidence exceeds this threshold
            </p>
            
            <div className="mb-2 flex justify-between">
              <span className="text-xs text-gray-400">Conservative</span>
              <span className="text-xs text-gray-400">Balanced</span>
              <span className="text-xs text-gray-400">Aggressive</span>
            </div>
            
            <input
              type="range"
              min="0.5"
              max="0.95"
              step="0.05"
              defaultValue={confidenceThreshold}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          
          {/* Recent AI trades would be connected to actual service in production */}
          <div className="border border-gray-700 rounded-lg p-4">
            <h3 className="text-xl font-bold mb-4">Recent AI Trades</h3>
            
            {tradeHistory && tradeHistory.length > 0 ? (
              <div className="space-y-3">
                {tradeHistory.map((trade, index) => (
                  <div key={index} className="bg-gray-800 rounded p-3 flex justify-between items-center">
                    <div>
                      <span className={`text-sm font-semibold ${trade.side === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                        {trade.side.toUpperCase()} {trade.token}
                      </span>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(trade.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{trade.amount} {trade.token}</p>
                      <p className="text-xs text-gray-400 mt-1">{trade.network}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-sm">No recent AI trades</p>
            )}
          </div>
        </div>
      </div>

      {/* Trading strategies section */}
      {renderTradingStrategies()}
      
      {/* Network preferences */}
      {renderNetworkPreferences()}
    </div>
  );
};

export default AITradingPanel;