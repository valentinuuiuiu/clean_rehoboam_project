import React, { useState, useEffect } from 'react';

interface ArbitrageRoute {
  buy_network: string;
  sell_network: string;
  buy_price: number;
  sell_price: number;
  estimated_profit: number;
  confidence: number;
  gas_cost: number;
  slippage_cost: number;
}

interface ArbitrageStrategy {
  symbol: string;
  routes: ArbitrageRoute[];
  estimated_profit: number;
  confidence: number;
  execution_timing: 'immediate' | 'delayed' | 'standard';
  executed?: boolean;
  executedAt?: string;
}

const ArbitrageView: React.FC = () => {
  const [strategies, setStrategies] = useState<ArbitrageStrategy[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedToken, setSelectedToken] = useState('ETH');
  const [showDetails, setShowDetails] = useState<string | null>(null);
  const [refreshInterval, setRefreshInterval] = useState<number>(30);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [executeLoading, setExecuteLoading] = useState<string | null>(null);

  // Network mapping for display
  const networkNames: Record<string, string> = {
    'ethereum': 'Ethereum',
    'arbitrum': 'Arbitrum',
    'optimism': 'Optimism',
    'polygon': 'Polygon',
    'base': 'Base',
    'zksync': 'zkSync Era',
    'scroll': 'Scroll',
    'mantle': 'Mantle',
    'celo': 'Celo',
    'avalanche': 'Avalanche',
    'linea': 'Linea',
  };

  // Tokens to analyze
  const tokens = ['BTC', 'ETH', 'USDC', 'LINK', 'UMA', 'AAVE', 'XMR'];

  // Fetch arbitrage opportunities
  useEffect(() => {
    fetchArbitrageOpportunities();
    
    // Set up polling interval
    const intervalId = setInterval(() => {
      fetchArbitrageOpportunities();
    }, refreshInterval * 1000);
    
    return () => clearInterval(intervalId);
  }, [refreshInterval, selectedToken]);

  const fetchArbitrageOpportunities = async () => {
    setIsLoading(true);
    try {
      // In production, this would call our backend API
      // For now, we'll simulate the response with realistic data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const simulatedData = getSimulatedArbitrageData(selectedToken);
      setStrategies(simulatedData);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch arbitrage opportunities:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate simulated arbitrage data for development
  const getSimulatedArbitrageData = (token: string): ArbitrageStrategy[] => {
    const basePrice = token === 'BTC' ? 60000 : 
                    token === 'ETH' ? 3000 : 
                    token === 'LINK' ? 15 : 
                    token === 'USDC' ? 1 :
                    token === 'AAVE' ? 90 :
                    token === 'UMA' ? 3.5 : 150;
    
    // Generate price variations across networks
    const networks = ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync'];
    const priceMap: Record<string, number> = {};
    
    networks.forEach(network => {
      // Add some realistic price variations (0.1% to 2.5%)
      const variation = (Math.random() * 2.5 + 0.1) * (Math.random() > 0.5 ? 1 : -1);
      priceMap[network] = basePrice * (1 + variation / 100);
    });
    
    // Find the best arbitrage routes
    const routes: ArbitrageRoute[] = [];
    
    for (let i = 0; i < networks.length; i++) {
      for (let j = 0; j < networks.length; j++) {
        if (i !== j) {
          const network1 = networks[i];
          const network2 = networks[j];
          
          if (priceMap[network1] < priceMap[network2]) {
            const priceDiff = priceMap[network2] - priceMap[network1];
            const percentDiff = (priceDiff / priceMap[network1]) * 100;
            
            // Only consider meaningful opportunities
            if (percentDiff > 0.15) {
              // Calculate realistic costs
              const gasCost = getSimulatedGasCost(network1, network2);
              const slippageCost = basePrice * 0.001 * (1 + Math.random());
              
              const estimatedProfit = priceDiff - gasCost - slippageCost;
              
              // Only add profitable routes
              if (estimatedProfit > 0) {
                routes.push({
                  buy_network: network1,
                  sell_network: network2,
                  buy_price: priceMap[network1],
                  sell_price: priceMap[network2],
                  estimated_profit: estimatedProfit,
                  confidence: 0.5 + Math.random() * 0.45, // 50-95% confidence
                  gas_cost: gasCost,
                  slippage_cost: slippageCost
                });
              }
            }
          }
        }
      }
    }
    
    // Sort routes by estimated profit
    routes.sort((a, b) => b.estimated_profit - a.estimated_profit);
    
    // Take top routes
    const topRoutes = routes.slice(0, Math.min(3, routes.length));
    
    if (topRoutes.length === 0) {
      return [];
    }
    
    // Create a strategy with the routes
    const totalProfit = topRoutes.reduce((sum, route) => sum + route.estimated_profit, 0);
    const avgConfidence = topRoutes.reduce((sum, route) => sum + route.confidence, 0) / topRoutes.length;
    
    const strategyTiming = avgConfidence > 0.8 ? 'immediate' : avgConfidence > 0.6 ? 'standard' : 'delayed';
    
    return [{
      symbol: token,
      routes: topRoutes,
      estimated_profit: totalProfit,
      confidence: avgConfidence,
      execution_timing: strategyTiming as 'immediate' | 'delayed' | 'standard'
    }];
  };
  
  const getSimulatedGasCost = (network1: string, network2: string): number => {
    // Simulate different gas costs for different networks
    const baseGas = network1 === 'ethereum' ? 25 : 
                   network1 === 'arbitrum' ? 3 :
                   network1 === 'optimism' ? 2 :
                   network1 === 'polygon' ? 0.5 :
                   network1 === 'base' ? 1 :
                   network1 === 'zksync' ? 1.5 : 5;
                   
    const bridgeGas = network2 === 'ethereum' ? 18 : 
                     network2 === 'arbitrum' ? 5 :
                     network2 === 'optimism' ? 4 :
                     network2 === 'polygon' ? 1 :
                     network2 === 'base' ? 2 :
                     network2 === 'zksync' ? 3 : 8;
                     
    return baseGas + bridgeGas;
  };

  const handleRefresh = () => {
    fetchArbitrageOpportunities();
  };

  const handleTokenChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedToken(e.target.value);
  };

  const handleRefreshIntervalChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRefreshInterval(parseInt(e.target.value));
  };

  const handleExecuteStrategy = async (symbol: string) => {
    setExecuteLoading(symbol);
    
    try {
      // In production, this would call our backend API
      // For now, we'll simulate the API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update UI after "execution"
      const updatedStrategies = strategies.map(strat => 
        strat.symbol === symbol 
          ? {...strat, executed: true, executedAt: new Date().toISOString()}
          : strat
      );
      
      setStrategies(updatedStrategies);
      console.log(`Executed arbitrage strategy for ${symbol}`);
    } catch (error) {
      console.error('Failed to execute strategy:', error);
    } finally {
      setExecuteLoading(null);
    }
  };

  const toggleDetails = (symbol: string) => {
    if (showDetails === symbol) {
      setShowDetails(null);
    } else {
      setShowDetails(symbol);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div className="flex items-center space-x-4">
          <div>
            <label htmlFor="token-select" className="block text-sm text-gray-400 mb-1">Token</label>
            <select
              id="token-select"
              className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-sm"
              value={selectedToken}
              onChange={handleTokenChange}
            >
              {tokens.map(token => (
                <option key={token} value={token}>{token}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="refresh-interval" className="block text-sm text-gray-400 mb-1">Refresh</label>
            <select
              id="refresh-interval"
              className="bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-sm"
              value={refreshInterval}
              onChange={handleRefreshIntervalChange}
            >
              <option value="10">10s</option>
              <option value="30">30s</option>
              <option value="60">1m</option>
              <option value="300">5m</option>
            </select>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {lastUpdated && (
            <span className="text-xs text-gray-400">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className={`p-2 rounded-md ${isLoading ? 'bg-gray-700 cursor-not-allowed' : 'bg-gray-700 hover:bg-gray-600'}`}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="h-5 w-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
          </button>
        </div>
      </div>
      
      {strategies.length === 0 && !isLoading ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium">No Arbitrage Opportunities</h3>
          <p className="mt-2 text-gray-400">
            We couldn't find any profitable arbitrage opportunities for {selectedToken} at this time.
            Markets appear to be in equilibrium.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {strategies.map(strategy => (
            <div key={strategy.symbol} className="bg-gray-800 rounded-lg overflow-hidden">
              <div className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div>
                    <h3 className="text-xl font-bold">{strategy.symbol} Arbitrage Strategy</h3>
                    <div className="mt-1 flex items-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        strategy.execution_timing === 'immediate' 
                          ? 'bg-green-900 text-green-300' 
                          : strategy.execution_timing === 'standard' 
                            ? 'bg-blue-900 text-blue-300' 
                            : 'bg-yellow-900 text-yellow-300'
                      }`}>
                        {strategy.execution_timing === 'immediate' ? 'Immediate Execution' : 
                          strategy.execution_timing === 'standard' ? 'Standard Execution' : 'Delayed Execution'}
                      </span>
                      <span className="ml-2 text-sm text-gray-400">
                        {strategy.routes.length} routes • {(strategy.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm text-gray-400">Estimated Profit</div>
                      <div className="text-2xl font-bold text-green-400">
                        ${strategy.estimated_profit.toFixed(2)}
                      </div>
                    </div>
                    
                    {strategy.executed ? (
                      <div className="text-green-400 flex items-center text-sm">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        Executed at {strategy.executedAt ? new Date(strategy.executedAt).toLocaleTimeString() : ''}
                      </div>
                    ) : (
                      <button
                        onClick={() => handleExecuteStrategy(strategy.symbol)}
                        disabled={executeLoading === strategy.symbol}
                        className={`px-4 py-2 rounded-lg font-medium ${
                          executeLoading === strategy.symbol ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                      >
                        {executeLoading === strategy.symbol ? (
                          <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Executing...
                          </span>
                        ) : 'Execute Strategy'}
                      </button>
                    )}
                    
                    <button
                      onClick={() => toggleDetails(strategy.symbol)}
                      className="p-2 rounded-md bg-gray-700 hover:bg-gray-600"
                    >
                      {showDetails === strategy.symbol ? (
                        <svg className="h-5 w-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                        </svg>
                      ) : (
                        <svg className="h-5 w-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
              
              {showDetails === strategy.symbol && (
                <div className="bg-gray-900 border-t border-gray-700 p-6">
                  <h4 className="text-lg font-medium mb-4">Arbitrage Routes</h4>
                  
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-700">
                      <thead>
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Buy Network</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Buy Price</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Sell Network</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Sell Price</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Price Diff</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Costs</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Profit</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Confidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-700">
                        {strategy.routes.map((route, index) => {
                          const priceDiff = route.sell_price - route.buy_price;
                          const percentDiff = (priceDiff / route.buy_price) * 100;
                          
                          return (
                            <tr key={index}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <div className="font-medium">{networkNames[route.buy_network] || route.buy_network}</div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                ${route.buy_price.toFixed(2)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <div className="font-medium">{networkNames[route.sell_network] || route.sell_network}</div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                ${route.sell_price.toFixed(2)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <div className="text-green-400">+{percentDiff.toFixed(2)}%</div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <div className="text-gray-400">
                                  <div>Gas: ${route.gas_cost.toFixed(2)}</div>
                                  <div>Slippage: ${route.slippage_cost.toFixed(2)}</div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <div className="font-medium text-green-400">${route.estimated_profit.toFixed(2)}</div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <div className="w-full bg-gray-600 rounded-full h-2">
                                  <div 
                                    className={`h-2 rounded-full ${
                                      route.confidence > 0.8 ? 'bg-green-500' :
                                      route.confidence > 0.6 ? 'bg-blue-500' : 'bg-yellow-500'
                                    }`}
                                    style={{ width: `${route.confidence * 100}%` }}
                                  ></div>
                                </div>
                                <div className="text-xs text-right mt-1">
                                  {Math.round(route.confidence * 100)}%
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                  
                  <div className="mt-6 bg-gray-800 rounded-lg p-4 text-sm">
                    <h5 className="font-medium mb-2">AI Reasoning</h5>
                    <p className="text-gray-300">
                      This arbitrage opportunity leverages price differences between {networkNames[strategy.routes[0].buy_network]} and {networkNames[strategy.routes[0].sell_network]} L2 networks. 
                      Confidence is based on historical price stability and current network congestion. 
                      {strategy.confidence > 0.8 
                        ? ' The high confidence score suggests immediate execution for optimal profits.'
                        : strategy.confidence > 0.6
                          ? ' The moderate confidence score suggests standard execution timing.'
                          : ' The lower confidence score suggests delayed execution to monitor for better entry points.'}
                    </p>
                    <div className="mt-2 text-xs text-gray-400">
                      <div className="font-medium mb-1">AI Factors Considered:</div>
                      <ul className="pl-4 list-disc">
                        <li>Layer 2 network gas costs and bridge fees</li>
                        <li>Historical slippage on DEXs for {strategy.symbol}</li>
                        <li>Market depth analysis across networks</li>
                        <li>Price divergence patterns for {strategy.symbol}</li>
                        <li>Network congestion and transaction confirmation times</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ArbitrageView;