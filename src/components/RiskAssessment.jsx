import React, { useState, useEffect } from 'react';

const RiskAssessment = () => {
  const [portfolio, setPortfolio] = useState({
    assets: [],
    totalValue: 0,
    riskScore: 0,
    diversificationScore: 0,
  });
  const [selectedTab, setSelectedTab] = useState('overview');
  const [loadingRiskData, setLoadingRiskData] = useState(true);
  const [isRiskOptimizing, setIsRiskOptimizing] = useState(false);

  // Risk metrics for Layer 2 networks
  const networkRiskMetrics = {
    ethereum: { securityScore: 95, liquidityScore: 98, centralizationRisk: 'Low', bridgeRisk: 'N/A' },
    arbitrum: { securityScore: 88, liquidityScore: 85, centralizationRisk: 'Medium', bridgeRisk: 'Low' },
    optimism: { securityScore: 86, liquidityScore: 82, centralizationRisk: 'Medium', bridgeRisk: 'Low' },
    polygon: { securityScore: 80, liquidityScore: 90, centralizationRisk: 'Medium', bridgeRisk: 'Low' },
    base: { securityScore: 82, liquidityScore: 75, centralizationRisk: 'Medium', bridgeRisk: 'Medium' },
    zksync: { securityScore: 84, liquidityScore: 70, centralizationRisk: 'Medium', bridgeRisk: 'Low' },
  };

  // Simulated loading of risk data
  useEffect(() => {
    const fetchRiskData = async () => {
      setLoadingRiskData(true);
      try {
        // This would connect to your AI risk assessment service in production
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Mock portfolio data for development
        const mockPortfolio = {
          assets: [
            { 
              symbol: 'ETH', 
              allocation: 45, 
              value: 3600, 
              riskScore: 65,
              networks: [
                { name: 'ethereum', allocation: 40 },
                { name: 'arbitrum', allocation: 35 },
                { name: 'optimism', allocation: 25 }
              ]
            },
            { 
              symbol: 'BTC', 
              allocation: 30, 
              value: 2400, 
              riskScore: 70,
              networks: [
                { name: 'ethereum', allocation: 100 }
              ]
            },
            { 
              symbol: 'LINK', 
              allocation: 12, 
              value: 960, 
              riskScore: 75,
              networks: [
                { name: 'ethereum', allocation: 30 },
                { name: 'polygon', allocation: 70 }
              ]
            },
            { 
              symbol: 'USDC', 
              allocation: 10, 
              value: 800, 
              riskScore: 30,
              networks: [
                { name: 'ethereum', allocation: 20 },
                { name: 'arbitrum', allocation: 50 },
                { name: 'base', allocation: 30 }
              ]
            },
            { 
              symbol: 'AAVE', 
              allocation: 3, 
              value: 240, 
              riskScore: 80,
              networks: [
                { name: 'ethereum', allocation: 50 },
                { name: 'polygon', allocation: 50 }
              ]
            },
          ],
          totalValue: 8000,
          riskScore: 68,
          diversificationScore: 72,
        };
        
        setPortfolio(mockPortfolio);
      } catch (error) {
        console.error('Error fetching risk data:', error);
      } finally {
        setLoadingRiskData(false);
      }
    };
    
    fetchRiskData();
  }, []);

  const handleOptimizeRisk = async () => {
    setIsRiskOptimizing(true);
    
    try {
      // This would call your AI optimization service in production
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simple "optimization" for simulation purposes
      const optimizedPortfolio = {
        ...portfolio,
        riskScore: Math.max(portfolio.riskScore - 12, 30),
        diversificationScore: Math.min(portfolio.diversificationScore + 8, 95),
        assets: portfolio.assets.map(asset => {
          // Redistribute allocations across networks for each asset
          if (asset.symbol === 'ETH') {
            return {
              ...asset,
              networks: [
                { name: 'ethereum', allocation: 25 },
                { name: 'arbitrum', allocation: 40 },
                { name: 'optimism', allocation: 35 }
              ]
            };
          } else if (asset.symbol === 'LINK') {
            return {
              ...asset,
              networks: [
                { name: 'ethereum', allocation: 20 },
                { name: 'polygon', allocation: 50 },
                { name: 'arbitrum', allocation: 30 }
              ]
            };
          } else {
            return asset;
          }
        })
      };
      
      setPortfolio(optimizedPortfolio);
    } catch (error) {
      console.error('Error optimizing portfolio:', error);
    } finally {
      setIsRiskOptimizing(false);
    }
  };

  // Calculate the overall network distribution
  const getNetworkDistribution = () => {
    const distribution = {};
    
    portfolio.assets.forEach(asset => {
      asset.networks.forEach(network => {
        const networkValue = (asset.value * asset.allocation / 100) * (network.allocation / 100);
        
        if (distribution[network.name]) {
          distribution[network.name] += networkValue;
        } else {
          distribution[network.name] = networkValue;
        }
      });
    });
    
    // Convert absolute values to percentages
    const totalValue = portfolio.totalValue;
    const percentages = {};
    
    Object.keys(distribution).forEach(network => {
      percentages[network] = (distribution[network] / totalValue) * 100;
    });
    
    return percentages;
  };

  const networkDistribution = getNetworkDistribution();

  // Helper function to get color class based on score
  const getScoreColorClass = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskLevelText = (score) => {
    if (score >= 80) return 'High Risk';
    if (score >= 60) return 'Moderate Risk';
    if (score >= 40) return 'Low Risk';
    return 'Very Low Risk';
  };

  if (loadingRiskData) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
      <div className="border-b border-gray-700">
        <nav className="flex">
          <button
            className={`px-4 py-3 font-medium ${selectedTab === 'overview' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-400'}`}
            onClick={() => setSelectedTab('overview')}
          >
            Portfolio Overview
          </button>
          <button
            className={`px-4 py-3 font-medium ${selectedTab === 'network' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-400'}`}
            onClick={() => setSelectedTab('network')}
          >
            Network Exposure
          </button>
          <button
            className={`px-4 py-3 font-medium ${selectedTab === 'optimization' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-400'}`}
            onClick={() => setSelectedTab('optimization')}
          >
            Risk Optimization
          </button>
        </nav>
      </div>
      
      {selectedTab === 'overview' && (
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-1">Overall Risk Score</h3>
              <div className="flex items-end">
                <span className={`text-4xl font-bold ${getScoreColorClass(portfolio.riskScore)}`}>
                  {portfolio.riskScore}
                </span>
                <span className="text-gray-400 ml-2 mb-1">/ 100</span>
              </div>
              <div className="mt-2 w-full bg-gray-600 rounded-full h-2.5">
                <div 
                  className={`h-2.5 rounded-full ${
                    portfolio.riskScore >= 80 ? 'bg-red-500' :
                    portfolio.riskScore >= 60 ? 'bg-yellow-500' :
                    portfolio.riskScore >= 40 ? 'bg-blue-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${portfolio.riskScore}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                {getRiskLevelText(portfolio.riskScore)}
              </p>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-1">Diversification Score</h3>
              <div className="flex items-end">
                <span className={`text-4xl font-bold ${getScoreColorClass(portfolio.diversificationScore)}`}>
                  {portfolio.diversificationScore}
                </span>
                <span className="text-gray-400 ml-2 mb-1">/ 100</span>
              </div>
              <div className="mt-2 w-full bg-gray-600 rounded-full h-2.5">
                <div 
                  className="bg-blue-500 h-2.5 rounded-full"
                  style={{ width: `${portfolio.diversificationScore}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                {portfolio.diversificationScore >= 80 ? 'Well diversified' :
                 portfolio.diversificationScore >= 60 ? 'Moderately diversified' :
                 'Poorly diversified'}
              </p>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-1">Portfolio Value</h3>
              <div className="flex items-end">
                <span className="text-4xl font-bold text-white">
                  ${portfolio.totalValue.toLocaleString()}
                </span>
              </div>
              <div className="mt-6 text-sm text-gray-400">
                <div className="flex justify-between mb-1">
                  <span>Assets</span>
                  <span>{portfolio.assets.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Networks</span>
                  <span>{Object.keys(networkDistribution).length}</span>
                </div>
              </div>
            </div>
          </div>
          
          <h3 className="text-xl font-semibold mb-4">Asset Allocation</h3>
          <div className="space-y-4">
            {portfolio.assets.map(asset => (
              <div key={asset.symbol} className="bg-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <h4 className="text-lg font-medium">{asset.symbol}</h4>
                    <p className="text-sm text-gray-400">${asset.value.toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold">{asset.allocation}%</div>
                    <div className={`text-sm ${getScoreColorClass(asset.riskScore)}`}>
                      Risk: {asset.riskScore}/100
                    </div>
                  </div>
                </div>
                
                <div className="w-full bg-gray-600 rounded-full h-1.5 mt-1">
                  <div 
                    className={`h-1.5 rounded-full ${
                      asset.riskScore >= 80 ? 'bg-red-500' :
                      asset.riskScore >= 60 ? 'bg-yellow-500' :
                      asset.riskScore >= 40 ? 'bg-blue-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${asset.riskScore}%` }}
                  ></div>
                </div>
                
                <div className="mt-2">
                  <div className="text-xs text-gray-400 mb-1">Network Distribution</div>
                  <div className="flex gap-2 flex-wrap">
                    {asset.networks.map(network => (
                      <div key={network.name} className="bg-gray-600 px-2 py-1 rounded text-xs">
                        {network.name.charAt(0).toUpperCase() + network.name.slice(1)}: {network.allocation}%
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {selectedTab === 'network' && (
        <div className="p-6">
          <h3 className="text-xl font-semibold mb-4">Network Exposure Analysis</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-lg font-semibold mb-3">Distribution by Network</h4>
              <div className="space-y-3">
                {Object.entries(networkDistribution).map(([network, percentage]) => (
                  <div key={network}>
                    <div className="flex justify-between items-center mb-1">
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full ${
                          network === 'ethereum' ? 'bg-blue-500' :
                          network === 'arbitrum' ? 'bg-indigo-500' :
                          network === 'optimism' ? 'bg-red-500' :
                          network === 'polygon' ? 'bg-purple-500' :
                          network === 'base' ? 'bg-green-500' :
                          'bg-yellow-500'
                        } mr-2`}></div>
                        <span className="capitalize">{network}</span>
                      </div>
                      <span>{percentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full ${
                          network === 'ethereum' ? 'bg-blue-500' :
                          network === 'arbitrum' ? 'bg-indigo-500' :
                          network === 'optimism' ? 'bg-red-500' :
                          network === 'polygon' ? 'bg-purple-500' :
                          network === 'base' ? 'bg-green-500' :
                          'bg-yellow-500'
                        }`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-lg font-semibold mb-3">Network Risk Factors</h4>
              <div className="space-y-4">
                <p className="text-sm text-gray-300">
                  Network risk assessments factor in security, liquidity, centralization, and bridge risks.
                </p>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full table-auto">
                    <thead>
                      <tr className="text-left text-xs text-gray-400">
                        <th className="px-2 py-1">Network</th>
                        <th className="px-2 py-1">Security</th>
                        <th className="px-2 py-1">Liquidity</th>
                        <th className="px-2 py-1">Central. Risk</th>
                        <th className="px-2 py-1">Bridge Risk</th>
                      </tr>
                    </thead>
                    <tbody className="text-sm">
                      {Object.entries(networkRiskMetrics).map(([network, metrics]) => (
                        <tr key={network} className="border-t border-gray-600">
                          <td className="px-2 py-1.5 capitalize">{network}</td>
                          <td className="px-2 py-1.5">
                            <span className={
                              metrics.securityScore >= 90 ? 'text-green-400' :
                              metrics.securityScore >= 80 ? 'text-blue-400' :
                              metrics.securityScore >= 70 ? 'text-yellow-400' : 'text-red-400'
                            }>
                              {metrics.securityScore}/100
                            </span>
                          </td>
                          <td className="px-2 py-1.5">
                            <span className={
                              metrics.liquidityScore >= 90 ? 'text-green-400' :
                              metrics.liquidityScore >= 80 ? 'text-blue-400' :
                              metrics.liquidityScore >= 70 ? 'text-yellow-400' : 'text-red-400'
                            }>
                              {metrics.liquidityScore}/100
                            </span>
                          </td>
                          <td className="px-2 py-1.5">
                            <span className={
                              metrics.centralizationRisk === 'Low' ? 'text-green-400' :
                              metrics.centralizationRisk === 'Medium' ? 'text-yellow-400' : 'text-red-400'
                            }>
                              {metrics.centralizationRisk}
                            </span>
                          </td>
                          <td className="px-2 py-1.5">
                            <span className={
                              metrics.bridgeRisk === 'N/A' ? 'text-gray-400' :
                              metrics.bridgeRisk === 'Low' ? 'text-green-400' :
                              metrics.bridgeRisk === 'Medium' ? 'text-yellow-400' : 'text-red-400'
                            }>
                              {metrics.bridgeRisk}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-lg font-semibold mb-3">Network Risk Assessment</h4>
            <div className="space-y-3 text-sm">
              <p>
                Your portfolio currently has a <strong className="text-blue-400">high exposure to Layer 1 (Ethereum)</strong> with {networkDistribution.ethereum?.toFixed(1) || 0}% of assets.
                This provides strong security but higher gas costs.
              </p>
              <p>
                Layer 2 networks comprise {(100 - (networkDistribution.ethereum || 0)).toFixed(1)}% of your portfolio, with
                <strong className="text-indigo-400"> Arbitrum </strong> 
                and <strong className="text-purple-400">Polygon</strong> being your largest L2 exposures.
              </p>
              <p>
                <strong className="text-yellow-400">Recommendations:</strong>
              </p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Consider increasing exposure to optimistic rollups like Arbitrum and Optimism for ETH-based assets</li>
                <li>Maintain USDC positions on Base and Arbitrum for yield farming opportunities with reduced risk</li>
                <li>For high-risk assets like AAVE, consider moving more allocation to zkSync for enhanced security</li>
              </ul>
            </div>
          </div>
        </div>
      )}
      
      {selectedTab === 'optimization' && (
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-xl font-semibold">AI Risk Optimization</h3>
            <button
              onClick={handleOptimizeRisk}
              disabled={isRiskOptimizing}
              className={`px-4 py-2 rounded-lg font-medium ${
                isRiskOptimizing ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isRiskOptimizing ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Optimizing...
                </span>
              ) : 'Optimize Portfolio'}
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="font-medium mb-3">Current Risk Profile</h4>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Risk Score</span>
                    <span className={getScoreColorClass(portfolio.riskScore)}>{portfolio.riskScore}/100</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        portfolio.riskScore >= 80 ? 'bg-red-500' :
                        portfolio.riskScore >= 60 ? 'bg-yellow-500' :
                        portfolio.riskScore >= 40 ? 'bg-blue-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${portfolio.riskScore}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Diversification</span>
                    <span>{portfolio.diversificationScore}/100</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${portfolio.diversificationScore}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <h5 className="text-sm font-medium mb-2">Network Distribution</h5>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(networkDistribution).map(([network, percentage]) => (
                      <div key={network} className="text-xs px-2 py-1 bg-gray-600 rounded capitalize">
                        {network}: {percentage.toFixed(1)}%
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="font-medium mb-3">Optimization Strategy</h4>
              <div className="space-y-3 text-sm">
                <p>
                  Our AI risk optimization engine analyzes your portfolio and suggests
                  adjustments to improve risk-reward metrics while considering Layer 2 efficiencies.
                </p>
                <div className="bg-gray-800 p-3 rounded-lg space-y-2">
                  <h5 className="font-medium">Recommended Actions:</h5>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Redistribute ETH from Ethereum L1 to Arbitrum and Optimism for reduced gas costs</li>
                    <li>Diversify LINK holdings across three networks instead of two</li>
                    <li>Add USDC liquidity on Optimism to improve cross-network diversification</li>
                    <li>Consider a small allocation to zkSync Era for emerging opportunities</li>
                  </ul>
                </div>
                <p className="text-gray-400">
                  Estimated risk reduction: 10-15 points<br/>
                  Estimated diversification improvement: 8-12 points<br/>
                  Estimated gas savings: 30-40%
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="font-medium mb-3">AI Reasoning</h4>
            <div className="prose prose-invert prose-sm max-w-none">
              <p>
                The optimization engine is using multi-model AI orchestration to analyze 
                your portfolio across Layer 2 networks:
              </p>
              <div className="space-y-4">
                <div className="bg-gray-800 p-3 rounded-lg">
                  <div className="flex items-center mb-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
                    <span className="font-medium">Gemini 2.5 Pro Analysis (Strategy)</span>
                  </div>
                  <p className="text-sm">
                    Your portfolio shows significant concentration risk due to high ETH exposure on Ethereum mainnet.
                    While L1 provides strong security, L2 solutions have matured significantly with comparable security
                    guarantees but much lower gas costs. A more balanced L1/L2 distribution will reduce your
                    risk profile while maintaining exposure to the Ethereum ecosystem.
                  </p>
                </div>
                
                <div className="bg-gray-800 p-3 rounded-lg">
                  <div className="flex items-center mb-2">
                    <div className="w-2 h-2 rounded-full bg-purple-500 mr-2"></div>
                    <span className="font-medium">DeepSeek Market Analysis</span>
                  </div>
                  <p className="text-sm">
                    Analysis of liquidity metrics across L2 networks indicates Arbitrum and Base
                    currently offer the most favorable risk-reward profiles. Network congestion
                    patterns suggest Optimism will see improved performance in the next quarter.
                    Historical bridge performance data indicates low risk for the major L2 networks,
                    making rebalancing a relatively safe operation.
                  </p>
                </div>
                
                <div className="bg-gray-800 p-3 rounded-lg">
                  <div className="flex items-center mb-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                    <span className="font-medium">GPT-4o-mini Anomaly Detection</span>
                  </div>
                  <p className="text-sm">
                    No significant anomalies detected in network behavior. The only
                    notable pattern is increased gas volatility on Ethereum mainnet,
                    reinforcing the recommendation to increase L2 allocation. No security
                    concerns identified across the major L2 networks in your portfolio.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskAssessment;