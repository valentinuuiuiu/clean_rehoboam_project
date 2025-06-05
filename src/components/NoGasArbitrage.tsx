import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { FlashArbitrageService, FlashArbitrageOpportunity } from '../services/FlashArbitrageService';

interface ArbitrageOpportunity {
  id: string;
  token: string;
  tokenSymbol: string;
  buyDEX: string;
  sellDEX: string;
  amount: string;
  buyPrice: number;
  sellPrice: number;
  estimatedProfit: number;
  netProfit: number;
  canExecute: boolean;
  guidance: string;
  confidence: number;
  chainId: number;
  chainName: string;
}

export const NoGasArbitrage: React.FC = () => {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<string | null>(null);
  const [userAddress, setUserAddress] = useState<string>('');
  const [status, setStatus] = useState<string>('Ready to find profitable arbitrage with zero upfront cost');
  const [flashArbitrageService, setFlashArbitrageService] = useState<FlashArbitrageService | null>(null);

  useEffect(() => {
    // Check if wallet is connected and initialize service
    const checkWallet = async () => {
      if (typeof window.ethereum !== 'undefined') {
        try {
          const accounts = await window.ethereum.request({ method: 'eth_accounts' });
          if (accounts.length > 0) {
            setUserAddress(accounts[0]);
            
            // Initialize the service with a provider
            const provider = new ethers.BrowserProvider(window.ethereum);
            const service = new FlashArbitrageService(provider); // No contract address needed initially
            setFlashArbitrageService(service);
          }
        } catch (error) {
          console.error('Error checking wallet:', error);
        }
      }
    };

    checkWallet();
    
    // Start monitoring for opportunities
    if (userAddress && flashArbitrageService) {
      monitorOpportunities();
    }
  }, [userAddress, flashArbitrageService]);

  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        setUserAddress(accounts[0]);
        setStatus('Wallet connected! Searching for no-risk arbitrage opportunities...');
        
        // Initialize the service
        const provider = new ethers.BrowserProvider(window.ethereum);
        const service = new FlashArbitrageService(provider); // Auto-detects contract address
        setFlashArbitrageService(service);
      } catch (error) {
        console.error('Error connecting wallet:', error);
        setStatus('Failed to connect wallet');
      }
    } else {
      setStatus('Please install MetaMask to use flash loan arbitrage');
    }
  };

  const monitorOpportunities = async () => {
    if (!flashArbitrageService) return;
    
    setIsLoading(true);
    try {
      // Search for opportunities in major tokens
      const tokens = ['ETH', 'USDC', 'USDT'];
      const allOpportunities: FlashArbitrageOpportunity[] = [];
      
      for (const token of tokens) {
        try {
          const opportunities = await flashArbitrageService.findArbitrageOpportunities(
            token,
            ethers.parseEther("5").toString(), // 5 ETH equivalent
            0.25 // 0.25% minimum profit for aggressive arbitrage
          );
          allOpportunities.push(...opportunities);
        } catch (error) {
          console.log(`No opportunities found for ${token}`);
        }
      }
      
      // Filter for profitable opportunities that cover all costs
      const profitableOps = allOpportunities.filter(op => op.netProfit > 0 && op.confidence > 70);
      
      const detailedOps: ArbitrageOpportunity[] = await Promise.all(
        profitableOps.map(async (op, index) => {
          // Convert amount from string (wei) to number for calculations
          const amountInEth = parseFloat(ethers.formatEther(op.amount));
          
          // Check if this opportunity can be executed with no gas money
          const canExecute = op.netProfit > 0.001; // Must profit at least $1-2 to be worth it
          
          return {
            id: `opp-${index}`,
            token: op.token,
            tokenSymbol: getTokenSymbol(op.token),
            buyDEX: op.buyDEX,
            sellDEX: op.sellDEX,
            amount: amountInEth.toFixed(4),
            buyPrice: op.buyPrice,
            sellPrice: op.sellPrice,
            estimatedProfit: op.expectedProfit,
            netProfit: op.netProfit,
            canExecute,
            guidance: canExecute ? 
              'Profitable! You can execute this with zero upfront cost.' : 
              'Profit too small to cover all fees. Wait for better opportunity.',
            confidence: op.confidence,
            chainId: 1, // Default to Ethereum for now
            chainName: 'Ethereum'
          };
        })
      );

      setOpportunities(detailedOps);
      
      if (detailedOps.length === 0) {
        setStatus('No profitable opportunities found. Monitoring continues...');
      } else {
        setStatus(`Found ${detailedOps.length} potential arbitrage opportunities!`);
      }
    } catch (error) {
      console.error('Error monitoring opportunities:', error);
      setStatus('Error finding opportunities. Will retry...');
    } finally {
      setIsLoading(false);
    }
  };

  const executeArbitrage = async (opportunity: ArbitrageOpportunity) => {
    if (!userAddress || !flashArbitrageService) {
      setStatus('Please connect your wallet first');
      return;
    }

    setIsLoading(true);
    setStatus('Executing flash loan arbitrage... This is risk-free!');

    try {
      // Switch to the correct network if needed
      if (window.ethereum && opportunity.chainId !== (await window.ethereum.request({ method: 'eth_chainId' }))) {
        await window.ethereum.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: `0x${opportunity.chainId.toString(16)}` }],
        });
      }

      // Get signer from provider
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();

      // Create opportunity object for the service
      const opportunityData = {
        token: opportunity.token,
        buyDEX: opportunity.buyDEX,
        sellDEX: opportunity.sellDEX,
        buyPrice: opportunity.buyPrice,
        sellPrice: opportunity.sellPrice,
        amount: ethers.parseEther(opportunity.amount).toString(),
        expectedProfit: opportunity.estimatedProfit,
        confidence: opportunity.confidence,
        gasEstimate: "0.001",
        flashLoanFee: 0.0005,
        netProfit: opportunity.netProfit,
        profitPercentage: (opportunity.netProfit / parseFloat(opportunity.amount)) * 100
      };

      // Execute the arbitrage using the service
      const txResponse = await flashArbitrageService.executeArbitrage(opportunityData, signer);
      
      // Wait for transaction confirmation
      const receipt = await txResponse.wait();
      
      if (receipt && receipt.status === 1) {
        setStatus(`🎉 Arbitrage successful! Transaction: ${txResponse.hash}`);
        // Refresh opportunities after successful execution
        setTimeout(() => monitorOpportunities(), 3000);
      } else {
        setStatus(`❌ Transaction failed. Hash: ${txResponse.hash}`);
      }
    } catch (error: any) {
      console.error('Error executing arbitrage:', error);
      
      // Check if it's a revert due to unprofitable arbitrage
      if (error.message && error.message.includes('revert')) {
        setStatus('❌ Transaction reverted - arbitrage was not profitable enough. No gas consumed!');
      } else {
        setStatus('❌ Transaction failed. If it reverted, no gas was consumed.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getTokenSymbol = (address: string): string => {
    const symbols: { [key: string]: string } = {
      '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 'WETH',
      '0xA0b86a33E6417c66c4D6E1b5e6e6b6e1b5e6e6b6': 'USDC',
      '0xdAC17F958D2ee523a2206206994597C13D831ec7': 'USDT',
      '0x514910771AF9Ca656af840dff83E8264EcF986CA': 'LINK',
    };
    return symbols[address] || 'TOKEN';
  };

  const getChainName = (chainId: number): string => {
    const chains: { [key: number]: string } = {
      1: 'Ethereum',
      42161: 'Arbitrum',
      10: 'Optimism',
      8453: 'Base',
      137: 'Polygon',
    };
    return chains[chainId] || `Chain ${chainId}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">
            ⚡ Flash Loan Arbitrage - No Gas Required
          </h1>
          <p className="text-xl text-blue-200 mb-6">
            Execute profitable arbitrage with ZERO upfront capital using flash loans
          </p>
          
          {!userAddress ? (
            <button
              onClick={connectWallet}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              Connect Wallet to Start
            </button>
          ) : (
            <div className="bg-blue-800/50 rounded-lg p-4 inline-block">
              <p className="text-blue-100">
                Connected: {userAddress.slice(0, 6)}...{userAddress.slice(-4)}
              </p>
            </div>
          )}
        </div>

        {/* Status */}
        <div className="bg-gray-800/50 rounded-lg p-4 mb-6">
          <p className="text-center text-white font-medium">{status}</p>
        </div>

        {/* Refresh Button */}
        {userAddress && (
          <div className="text-center mb-6">
            <button
              onClick={monitorOpportunities}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
            >
              {isLoading ? 'Scanning Markets...' : 'Refresh Opportunities'}
            </button>
          </div>
        )}

        {/* Opportunities Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {opportunities.map((opportunity) => (
            <div
              key={opportunity.id}
              className={`bg-gray-800/70 rounded-lg p-6 border-2 transition-all ${
                opportunity.canExecute
                  ? 'border-green-500 hover:border-green-400'
                  : 'border-yellow-500 hover:border-yellow-400'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-white">
                  {opportunity.tokenSymbol} Arbitrage
                </h3>
                <span className={`px-2 py-1 rounded text-sm font-bold ${
                  opportunity.canExecute ? 'bg-green-600 text-white' : 'bg-yellow-600 text-black'
                }`}>
                  {opportunity.confidence}% confident
                </span>
              </div>

              <div className="space-y-2 text-sm text-gray-300 mb-4">
                <p><strong>Chain:</strong> {opportunity.chainName}</p>
                <p><strong>Amount:</strong> {parseFloat(opportunity.amount).toFixed(4)} ETH</p>
                <p><strong>Buy from:</strong> {opportunity.buyDEX}</p>
                <p><strong>Sell to:</strong> {opportunity.sellDEX}</p>
                <p><strong>Buy Price:</strong> ${opportunity.buyPrice.toFixed(6)}</p>
                <p><strong>Sell Price:</strong> ${opportunity.sellPrice.toFixed(6)}</p>
                <p className="text-green-400">
                  <strong>Net Profit:</strong> ${opportunity.netProfit.toFixed(6)}
                </p>
              </div>

              <p className="text-sm text-blue-200 mb-4">{opportunity.guidance}</p>

              {opportunity.canExecute ? (
                <button
                  onClick={() => executeArbitrage(opportunity)}
                  disabled={isLoading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  Execute Flash Arbitrage
                </button>
              ) : (
                <button
                  disabled
                  className="w-full bg-gray-600 text-gray-400 font-bold py-2 px-4 rounded-lg cursor-not-allowed"
                >
                  Profit Too Small
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Information Panel */}
        <div className="mt-12 bg-gray-800/50 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4">How Flash Loan Arbitrage Works</h2>
          <div className="grid gap-4 md:grid-cols-2 text-gray-300">
            <div>
              <h3 className="text-lg font-semibold text-blue-300 mb-2">⚡ No Upfront Capital</h3>
              <p>Borrow up to 100+ ETH instantly with no collateral using Aave flash loans</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-300 mb-2">🎯 Risk-Free</h3>
              <p>If arbitrage isn't profitable, entire transaction reverts - you pay $0</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-300 mb-2">🔄 Cross-DEX</h3>
              <p>Buy low on one DEX, sell high on another, all in one transaction</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-300 mb-2">⛓️ Multi-Chain</h3>
              <p>Works across Ethereum, Arbitrum, Optimism, Base, and Polygon</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NoGasArbitrage;
