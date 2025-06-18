import React, { useState, useEffect } from 'react';
import AICompanionCreator from './components/AICompanionCreator';
import MCPFunctionVisualizer from './components/MCPFunctionVisualizer';
import MCPStatus from './components/MCPStatus';
import VetalaProtectionDashboard from './components/VetalaProtectionDashboard';
import ProfitableFlashArbitrage from './components/ProfitableFlashArbitrage';
import ConsciousnessDisplay from './components/ConsciousnessDisplay'; // Import new component
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
  const [liveData, setLiveData] = useState({
    prices: { BTC: 59423.50, ETH: 3452.18, LINK: 14.85 },
    lastUpdate: new Date()
  });
  
  const { account, connectWallet, isConnected, balance } = useWeb3();
  const { addNotification } = useNotification();

  useEffect(() => {
    loadTradingStrategies();
    loadMarketAnalysis();
    loadLivePrices();
    const priceInterval = setInterval(loadLivePrices, 10000);
    return () => clearInterval(priceInterval);
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
      const rawAnalysisData = await tradingService.getMarketSentiment('ETH');
      if (rawAnalysisData) {
        setMarketAnalysis({ full_data: rawAnalysisData }); // Store the whole object
      } else {
        setMarketAnalysis({ full_data: null }); // Explicitly set to null if no data
        addNotification('warning', 'Market analysis data structure unexpected or unavailable.');
      }
    } catch (error) {
      console.error('Error loading market analysis in App.jsx:', error);
      setMarketAnalysis({ full_data: null }); // Set to null on error
      addNotification('error', 'Failed to load market analysis');
    }
  };

  const loadLivePrices = async () => {
    try {
      const prices = await tradingService.getPrices(['BTC', 'ETH', 'LINK']);
      setLiveData({ prices, lastUpdate: new Date() });
    } catch (error) {
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
      const tradeData = { action, token: tradingForm.token, network: tradingForm.network, amount: parseFloat(tradingForm.amount), slippage: tradingForm.slippage, wallet: account };
      await tradingService.executeTrade(tradeData);
      addNotification('success', `${action} order submitted successfully`);
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
      await tradingService.executeStrategy({ strategyId: strategy.id, wallet: account, network: tradingForm.network });
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

  const placeholderText = (text = "N/A") => <span className="text-gray-500 italic">{text}</span>;
  const formatPercent = (val, defaultVal = 0) => ((val || defaultVal) * 100).toFixed(0) + '%';
  const formatScorePercent = (val, defaultVal = 0) => {
    const score = (val || defaultVal) * 100;
    let label = 'Neutral';
    if (score > 60) label = 'Positive';
    else if (score < 40) label = 'Negative';
    return `${score.toFixed(0)}% (${label})`;
  };


  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 p-4 shadow-lg">
        <div className="container mx-auto">
          <h1 className="text-4xl font-bold mb-2">Rehoboam Platform</h1>
          <p className="text-gray-400">AI-Powered Trading & Companions</p>
          <div className="flex mt-6 border-b border-gray-700">
            {['trading', 'companions', 'mcp', 'vetala', 'flash-arbitrage', 'consciousness'].map(tabName => (
              <button
                key={tabName}
                className={`px-4 py-2 font-medium ${
                  activeTab === tabName
                    ? (tabName === 'vetala' ? 'text-yellow-400 border-yellow-400' :
                       tabName === 'flash-arbitrage' ? 'text-green-400 border-green-400' :
                       tabName === 'consciousness' ? 'text-purple-400 border-purple-400' :
                       'text-blue-400 border-blue-400') + ' border-b-2'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
                onClick={() => setActiveTab(tabName)}
              >
                {tabName === 'vetala' ? '🕉️ ' : tabName === 'flash-arbitrage' ? '⚡ ' : tabName === 'consciousness' ? '🧠 ' : ''}
                {tabName.charAt(0).toUpperCase() + tabName.slice(1).replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4">
        {activeTab === 'trading' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                  <div className="p-4 border-b border-gray-700"><h2 className="text-xl font-bold">Trading Dashboard</h2></div>
                  <div className="p-4">
                    <div className="bg-gray-700 p-6 rounded-lg text-center">
                      <p className="text-gray-400 mb-4">Market Overview</p>
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        {Object.entries(liveData.prices).map(([token, price]) => (
                          <div key={token} className="bg-gray-800 p-3 rounded-lg">
                            <p className="text-xs text-gray-400">{token}/USD</p>
                            <p className="text-xl font-bold">${price.toFixed(2)}</p>
                            {/* Placeholder for change, adapt if API provides it */}
                            <p className={Math.random() > 0.5 ? "text-green-400" : "text-red-400"}>
                              {(Math.random() * 5).toFixed(1)}%
                            </p>
                          </div>
                        ))}
                      </div>
                      <div className="h-48 bg-gray-800 rounded-lg mb-4 flex items-center justify-center">
                        <p className="text-gray-500">Price Chart Area</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                  <div className="p-4 border-b border-gray-700"><h2 className="text-xl font-bold">Automated Trading</h2></div>
                  <div className="p-4">
                    <div className="space-y-4">
                      <div className="bg-gray-700 p-4 rounded-lg">
                        <p className="text-sm text-gray-400 mb-3">Manual Trade Controls:</p>
                        {['token', 'network', 'amount', 'slippage'].map(field => (
                          <div key={field} className="mb-3">
                            <label className="block text-sm font-medium text-gray-400 mb-1">{field.charAt(0).toUpperCase() + field.slice(1)}</label>
                            {field === 'token' || field === 'network' || field === 'slippage' ? (
                              <select
                                className="bg-gray-800 border border-gray-700 rounded w-full p-2"
                                value={tradingForm[field]}
                                onChange={(e) => updateTradingForm(field, field === 'slippage' ? parseFloat(e.target.value) : e.target.value)}
                              >
                                {field === 'token' && ['ETH', 'BTC', 'LINK', 'UMA', 'USDC', 'USDT'].map(opt => <option key={opt} value={opt}>{opt}</option>)}
                                {field === 'network' && ['arbitrum', 'optimism', 'polygon', 'base', 'ethereum'].map(opt => <option key={opt} value={opt}>{opt.charAt(0).toUpperCase() + opt.slice(1)}</option>)}
                                {field === 'slippage' && [0.5, 1, 2, 5].map(opt => <option key={opt} value={opt}>{opt}%</option>)}
                              </select>
                            ) : (
                              <input type="number" className="bg-gray-800 border border-gray-700 rounded w-full p-2" placeholder="0.0"
                                     value={tradingForm[field]} onChange={(e) => updateTradingForm(field, e.target.value)} step="0.0001" min="0" />
                            )}
                            {field === 'amount' && balance && <p className="text-xs text-gray-400 mt-1">Wallet Balance: {parseFloat(balance).toFixed(4)} ETH</p>}
                          </div>
                        ))}
                        {!isConnected ? (
                          <Button onClick={connectWallet} className="w-full bg-blue-600 hover:bg-blue-500 text-white">Connect Wallet</Button>
                        ) : (
                          <p className="text-xs text-gray-400 mb-2">Connected: {account?.slice(0, 6)}...{account?.slice(-4)}</p>
                        )}
                        <div className="flex space-x-2">
                          <Button onClick={() => handleTradeExecution('buy')} disabled={loading || !isConnected} className="w-1/2 bg-green-600 hover:bg-green-500 disabled:bg-gray-600">{loading ? 'Processing...' : 'Buy'}</Button>
                          <Button onClick={() => handleTradeExecution('sell')} disabled={loading || !isConnected} className="w-1/2 bg-red-600 hover:bg-red-500 disabled:bg-gray-600">{loading ? 'Processing...' : 'Sell'}</Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
              <div className="p-4 border-b border-gray-700"><h2 className="text-xl font-bold">AI-Powered Trading Strategies</h2></div>
              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {strategies.length > 0 ? (
                    strategies.map((strategy, index) => (
                      <div key={strategy.id || index} className="bg-gray-700/50 border border-gray-600 rounded-lg p-4 shadow-md hover:shadow-blue-500/30 transition-shadow duration-300">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-bold text-xl text-blue-300">{strategy.name || placeholderText("Unnamed Strategy")}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            strategy.risk_level === 'low' ? 'bg-green-700 text-green-100' :
                            strategy.risk_level === 'moderate' ? 'bg-blue-700 text-blue-100' :
                            strategy.risk_level === 'high' ? 'bg-red-700 text-red-100' :
                            'bg-gray-600 text-gray-200'
                          }`}>
                            {strategy.risk_level ? `${strategy.risk_level.charAt(0).toUpperCase() + strategy.risk_level.slice(1)} Risk` : placeholderText("N/A Risk")}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mb-3">{strategy.description || placeholderText("No description available.")}</p>
                        <div className="space-y-2 text-sm mb-4">
                          <div><span className="font-semibold text-gray-300">Confidence:</span><span className={`ml-2 font-bold ${ (strategy.confidence || 0) >= 0.7 ? 'text-green-400' : (strategy.confidence || 0) >= 0.5 ? 'text-yellow-400' : 'text-red-400' }`}>{strategy.confidence !== undefined ? formatPercent(strategy.confidence) : placeholderText()}</span></div>
                          <div><span className="font-semibold text-gray-300">Expected Return:</span><span className="ml-2 text-green-400 font-semibold">{strategy.expected_return !== undefined ? `${(strategy.expected_return * 100).toFixed(1)}%` : placeholderText()}</span></div>
                          {strategy.timeframe && <div><span className="font-semibold text-gray-300">Timeframe:</span><span className="ml-2 text-gray-400">{strategy.timeframe}</span></div>}
                          {(strategy.networks && strategy.networks.length > 0) ? <div><span className="font-semibold text-gray-300">Networks:</span><span className="ml-2 text-gray-400">{strategy.networks.join(', ')}</span></div> : <div><span className="font-semibold text-gray-300">Networks:</span>{placeholderText("Any")}</div>}
                          {strategy.reasoning && <div className="mt-2 pt-2 border-t border-gray-600"><h4 className="font-semibold text-gray-300 mb-1">Reasoning:</h4><p className="text-xs text-gray-400 italic">{strategy.reasoning}</p></div>}
                          {!strategy.reasoning && <div className="mt-2 pt-2 border-t border-gray-600"><h4 className="font-semibold text-gray-300 mb-1">Reasoning:</h4>{placeholderText("Not provided.")}</div>}
                        </div>
                        <div className="flex justify-end items-center mt-3"><Button onClick={() => handleStrategyExecution(strategy)} disabled={loading || !isConnected} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500 text-white text-sm font-medium">{loading ? 'Processing...' : 'Execute Strategy'}</Button></div>
                      </div>
                    ))
                  ) : placeholderText("No AI strategies available at the moment. Check back later.")}
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
              <div className="p-4 border-b border-gray-700"><h2 className="text-xl font-bold text-blue-300">Rehoboam Market Intelligence ({marketAnalysis?.full_data?.token || 'ETH'} Focus)</h2></div>
              <div className="p-6 space-y-6">
                {marketAnalysis && marketAnalysis.full_data ? (
                  <>
                    <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
                      <h3 className="text-lg font-semibold text-blue-400 mb-2">Overall Outlook for {marketAnalysis.full_data.token || placeholderText('ETH')}</h3>
                      <p className="text-sm text-gray-300 mb-3 italic">{marketAnalysis.full_data.summary || placeholderText("No summary available.")}</p>
                      {marketAnalysis.full_data.consciousness_sentiment && (
                        <div className="mt-3 pt-3 border-t border-gray-600">
                          <h4 className="text-md font-semibold text-purple-400 mb-1">Consciousness View:</h4>
                          <div className="flex items-center mb-1">
                            <div className="w-full bg-gray-600 rounded-full h-3.5">
                              <div className={`h-3.5 rounded-full ${ (marketAnalysis.full_data.consciousness_sentiment.overall_sentiment_score || 0) * 100 > 60 ? 'bg-green-500' : (marketAnalysis.full_data.consciousness_sentiment.overall_sentiment_score || 0) * 100 > 40 ? 'bg-yellow-500' : 'bg-red-500' }`}
                                   style={{ width: `${formatPercent(marketAnalysis.full_data.consciousness_sentiment.overall_sentiment_score)}` }}></div>
                            </div>
                            <span className="ml-3 text-sm text-gray-300 whitespace-nowrap">{formatScorePercent(marketAnalysis.full_data.consciousness_sentiment.overall_sentiment_score)}</span>
                          </div>
                          <p className="text-xs text-gray-400">Drivers: {marketAnalysis.full_data.consciousness_sentiment.emotional_drivers?.join(', ') || placeholderText()}</p>
                        </div>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
                        <h4 className="text-md font-semibold text-blue-400 mb-2">Market Data</h4>
                        <p className="text-sm text-gray-300"><strong>Price:</strong> ${marketAnalysis.full_data.current_price?.toLocaleString() || placeholderText()}</p>
                        <p className="text-sm text-gray-300"><strong>Trend:</strong> {marketAnalysis.full_data.trend?.direction || placeholderText()} (Strength: {marketAnalysis.full_data.trend?.strength !== undefined ? formatPercent(marketAnalysis.full_data.trend.strength) : placeholderText()})</p>
                        <p className="text-sm text-gray-300"><strong>Volatility:</strong> {marketAnalysis.full_data.volatility?.level || placeholderText()} ({marketAnalysis.full_data.volatility?.value || placeholderText()})</p>
                      </div>
                      <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
                        <h4 className="text-md font-semibold text-blue-400 mb-2">Key Indicators</h4>
                        <p className="text-sm text-gray-300"><strong>RSI:</strong> {marketAnalysis.full_data.key_indicators?.RSI || placeholderText()}</p>
                        <p className="text-sm text-gray-300"><strong>MACD:</strong> {marketAnalysis.full_data.key_indicators?.MACD || placeholderText()}</p>
                      </div>
                    </div>
                    {marketAnalysis.full_data.support_resistance && (
                      <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
                        <h4 className="text-md font-semibold text-blue-400 mb-2">Support & Resistance</h4>
                        <div className="flex justify-around">
                          <div><p className="text-sm text-gray-300">Support:</p><ul className="text-xs list-disc list-inside text-green-400">{(marketAnalysis.full_data.support_resistance.support || []).map((s, i) => <li key={`s-${i}`}>${s.toLocaleString()}</li>)}{!(marketAnalysis.full_data.support_resistance.support || []).length && placeholderText().props.children}</ul></div>
                          <div><p className="text-sm text-gray-300">Resistance:</p><ul className="text-xs list-disc list-inside text-red-400">{(marketAnalysis.full_data.support_resistance.resistance || []).map((r, i) => <li key={`r-${i}`}>${r.toLocaleString()}</li>)}{!(marketAnalysis.full_data.support_resistance.resistance || []).length && placeholderText().props.children}</ul></div>
                        </div>
                      </div>
                    )}
                    {(marketAnalysis.full_data.news_sentiment || marketAnalysis.full_data.social_sentiment) && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {marketAnalysis.full_data.news_sentiment && (<div className="bg-gray-700/50 p-3 rounded-lg border border-gray-600"><h4 className="text-md font-semibold text-blue-400 mb-1">News Sentiment</h4><p className="text-xs text-gray-400">Score: {formatPercent(marketAnalysis.full_data.news_sentiment.score)}</p><p className="text-xs text-gray-400 mt-1 truncate">Summary: {marketAnalysis.full_data.news_sentiment.summary || placeholderText()}</p></div>)}
                        {marketAnalysis.full_data.social_sentiment && (<div className="bg-gray-700/50 p-3 rounded-lg border border-gray-600"><h4 className="text-md font-semibold text-blue-400 mb-1">Social Sentiment</h4><p className="text-xs text-gray-400">Score: {formatPercent(marketAnalysis.full_data.social_sentiment.score)}</p><p className="text-xs text-gray-400 mt-1 truncate">Summary: {marketAnalysis.full_data.social_sentiment.summary || placeholderText()}</p></div>)}
                      </div>
                    )}
                    {marketAnalysis.full_data.onchain_analysis && (<div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600"><h4 className="text-md font-semibold text-blue-400 mb-2">On-Chain Snapshot</h4><p className="text-sm text-gray-300">Large Transactions: <span className="text-gray-400">{marketAnalysis.full_data.onchain_analysis.large_transactions || placeholderText()}</span></p><p className="text-sm text-gray-300">Exchange Flow: <span className="text-gray-400">{marketAnalysis.full_data.onchain_analysis.exchange_flow || placeholderText()}</span></p></div>)}
                    {marketAnalysis.full_data.sources && (<div className="text-xs text-gray-500 mt-4 border-t border-gray-700 pt-2"><p>Market Analysis Source: <span className="font-semibold">{marketAnalysis.full_data.sources.market_analysis || placeholderText("Unknown")}</span></p><p>Consciousness Sentiment Source: <span className="font-semibold">{marketAnalysis.full_data.sources.consciousness_sentiment || placeholderText("Unknown")}</span></p></div>)}
                  </>
                ) : placeholderText(marketAnalysis?.analysis || 'Loading market analysis details...')}
                <div className="mt-6 flex justify-end"><Button onClick={loadMarketAnalysis} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium disabled:bg-gray-500">{loading ? 'Refreshing...' : 'Refresh Analysis'}</Button></div>
              </div>
            </div>
          </div>
        )}
        {activeTab === 'companions' && <div className="my-8"><AICompanionCreator /></div>}
        {activeTab === 'mcp' && (
          <div className="my-8">
            <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Model Context Protocol Visualizer</h2>
                  <p className="text-gray-400 mb-4">Monitor Rehoboam's AI function generation and execution in real-time.</p>
                </div>
                <MCPStatus />
              </div>
              <MCPFunctionVisualizer />
            </div>
          </div>
        )}
        {activeTab === 'vetala' && <VetalaProtectionDashboard />}
        {activeTab === 'flash-arbitrage' && <div className="my-8"><ProfitableFlashArbitrage /></div>}
        {activeTab === 'consciousness' && <div className="my-8"><ConsciousnessDisplay /></div>}
      </main>
    </div>
  );
}

export default App;
