import React from 'react';
import { useWeb3 } from '../contexts/Web3Context';
import { usePerformance } from '../contexts/PerformanceContext';

const StatusBar = () => {
  const { account, chainId, isConnected, connectWallet, error } = useWeb3();
  const { metrics } = usePerformance();

  const truncateAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatChainName = (id) => {
    switch (id) {
      case 1: return 'Ethereum';
      case 42161: return 'Arbitrum';
      case 10: return 'Optimism';
      case 137: return 'Polygon';
      case 8453: return 'Base';
      default: return `Chain #${id}`;
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-4 py-2">
      <div className="container mx-auto flex flex-wrap items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <span className="text-gray-400 text-sm">Status:</span>
            <span className="ml-2 text-sm">
              {isConnected ? (
                <span className="text-green-400">Connected</span>
              ) : (
                <span className="text-red-400">Disconnected</span>
              )}
            </span>
          </div>
          
          {isConnected && account && (
            <>
              <div>
                <span className="text-gray-400 text-sm">Account:</span>
                <span className="ml-2 text-sm text-blue-400">{truncateAddress(account)}</span>
              </div>
              
              {chainId && (
                <div>
                  <span className="text-gray-400 text-sm">Network:</span>
                  <span className="ml-2 text-sm text-purple-400">{formatChainName(chainId)}</span>
                </div>
              )}
            </>
          )}
        </div>
        
        <div className="flex items-center space-x-4">
          <div>
            <span className="text-gray-400 text-sm">CPU:</span>
            <span className="ml-2 text-sm text-yellow-400">{metrics.cpuUsage.toFixed(1)}%</span>
          </div>
          
          <div>
            <span className="text-gray-400 text-sm">Memory:</span>
            <span className="ml-2 text-sm text-yellow-400">{metrics.memoryUsage.toFixed(1)}%</span>
          </div>
          
          <div>
            <span className="text-gray-400 text-sm">Latency:</span>
            <span className="ml-2 text-sm text-yellow-400">{metrics.responseTime || 0} ms</span>
          </div>
        </div>
        
        <div>
          {!isConnected ? (
            <div className="flex space-x-2">
              <button
                onClick={() => connectWallet('metamask')}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                Connect MetaMask
              </button>
              <button
                onClick={() => connectWallet('talisman')}
                className="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700"
              >
                Connect Talisman
              </button>
            </div>
          ) : (
            <span className="text-sm text-gray-400">© 2025 Advanced Trading Platform</span>
          )}
        </div>
      </div>
      
      {error && (
        <div className="mt-2 bg-red-900/50 p-2 rounded text-sm text-red-200">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default StatusBar;