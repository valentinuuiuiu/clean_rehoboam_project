import React, { useState } from 'react';

const PriceFeedConfig = () => {
  const [selectedTokens, setSelectedTokens] = useState([
    { id: 'BTC', name: 'Bitcoin', enabled: true },
    { id: 'ETH', name: 'Ethereum', enabled: true },
    { id: 'SHIB', name: 'Shiba Inu', enabled: false },
    { id: 'UMA', name: 'UMA', enabled: false },
    { id: 'AAVE', name: 'Aave', enabled: false },
    { id: 'XMR', name: 'Monero', enabled: false },
  ]);

  const [updateInterval, setUpdateInterval] = useState(30);
  const [alertThreshold, setAlertThreshold] = useState(5);

  const handleTokenToggle = (tokenId) => {
    setSelectedTokens(prev => 
      prev.map(token => 
        token.id === tokenId ? { ...token, enabled: !token.enabled } : token
      )
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg">
        <h3 className="text-lg font-semibold mb-3">Price Feed Configuration</h3>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-400 mb-1">
            Update Interval (seconds)
          </label>
          <input
            type="number"
            min="5"
            max="300"
            value={updateInterval}
            onChange={e => setUpdateInterval(Number(e.target.value))}
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-400 mb-1">
            Price Alert Threshold (%)
          </label>
          <input
            type="number"
            min="0.1"
            max="20"
            step="0.1"
            value={alertThreshold}
            onChange={e => setAlertThreshold(Number(e.target.value))}
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
          />
        </div>
      </div>
      
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg">
        <h3 className="text-lg font-semibold mb-3">Active Tokens</h3>
        
        <div className="space-y-2">
          {selectedTokens.map(token => (
            <div key={token.id} className="flex items-center">
              <label className="flex items-center cursor-pointer flex-1">
                <input
                  type="checkbox"
                  checked={token.enabled}
                  onChange={() => handleTokenToggle(token.id)}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <span className="ml-2">{token.name} ({token.id})</span>
              </label>
              {token.enabled && (
                <span className="text-gray-400 text-sm">Active</span>
              )}
            </div>
          ))}
        </div>
      </div>
      
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg">
        <h3 className="text-lg font-semibold mb-3">Data Sources</h3>
        
        <div className="space-y-2">
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={true}
              readOnly
              className="h-4 w-4 text-blue-600 rounded"
            />
            <span className="ml-2">Binance</span>
            <span className="ml-auto text-green-400 text-sm">Online</span>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={true}
              readOnly
              className="h-4 w-4 text-blue-600 rounded"
            />
            <span className="ml-2">Coinbase</span>
            <span className="ml-auto text-green-400 text-sm">Online</span>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={false}
              readOnly
              className="h-4 w-4 text-gray-500 rounded"
            />
            <span className="ml-2">Kraken</span>
            <span className="ml-auto text-gray-400 text-sm">Offline</span>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={true}
              readOnly
              className="h-4 w-4 text-blue-600 rounded"
            />
            <span className="ml-2">Chainlink (On-chain)</span>
            <span className="ml-auto text-yellow-400 text-sm">Limited</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceFeedConfig;