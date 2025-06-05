import React, { createContext, useState, useContext, useEffect } from 'react';

// Create a Web3 context with default values
const Web3Context = createContext({
  account: null,
  chainId: null,
  provider: null,
  isConnected: false,
  activeWallet: null,
  connectWallet: async () => {},
  switchNetwork: async () => {},
  error: null,
});

// Network configurations
export const SUPPORTED_NETWORKS = {
  ethereum: {
    chainId: 1,
    name: 'Ethereum',
    rpcUrl: 'https://eth-mainnet.g.alchemy.com/v2/demo',
    explorer: 'https://etherscan.io',
  },
  arbitrum: {
    chainId: 42161,
    name: 'Arbitrum',
    rpcUrl: 'https://arb-mainnet.g.alchemy.com/v2/demo',
    explorer: 'https://arbiscan.io',
  },
  optimism: {
    chainId: 10,
    name: 'Optimism',
    rpcUrl: 'https://opt-mainnet.g.alchemy.com/v2/demo',
    explorer: 'https://optimistic.etherscan.io',
  },
  polygon: {
    chainId: 137,
    name: 'Polygon',
    rpcUrl: 'https://polygon-mainnet.g.alchemy.com/v2/demo',
    explorer: 'https://polygonscan.com',
  },
  base: {
    chainId: 8453,
    name: 'Base',
    rpcUrl: 'https://base-mainnet.g.alchemy.com/v2/demo',
    explorer: 'https://basescan.org',
  },
  bsc: {
    chainId: 56,
    name: 'BNB Smart Chain',
    rpcUrl: 'https://bsc-dataseed.binance.org',
    explorer: 'https://bscscan.com',
    type: 'evm_compatible'
  },
  mina: {
    chainId: 'mina:mainnet', // Mina uses different chain ID format
    name: 'Mina Protocol',
    rpcUrl: 'https://proxy.berkeley.minaexplorer.com',
    explorer: 'https://minaexplorer.com',
    type: 'zero_knowledge'
  },
};

export const Web3ContextProvider = ({ children }) => {
  const [account, setAccount] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [provider, setProvider] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [activeWallet, setActiveWallet] = useState(null);
  const [error, setError] = useState(null);

  // Function to connect wallet
  const connectWallet = async (walletType = 'demo') => {
    try {
      setError(null);
      
      if (walletType === 'metamask' && window.ethereum) {
        try {
          // Request account access
          const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
          if (accounts.length > 0) {
            setAccount(accounts[0]);
            
            // Get chain ID
            const chainIdHex = await window.ethereum.request({ method: 'eth_chainId' });
            setChainId(parseInt(chainIdHex, 16));
            
            setIsConnected(true);
            setActiveWallet('metamask');
            setProvider(window.ethereum);
            console.log('✅ MetaMask wallet connected:', accounts[0]);
          }
        } catch (error) {
          console.warn('MetaMask connection failed, switching to demo mode:', error.message);
          // Fall back to demo mode
          connectWallet('demo');
          return;
        }
      } else if (walletType === 'talisman' && window.talismanEth) {
        try {
          // Request account access
          const accounts = await window.talismanEth.request({ method: 'eth_requestAccounts' });
          if (accounts.length > 0) {
            setAccount(accounts[0]);
            
            // Get chain ID
            const chainIdHex = await window.talismanEth.request({ method: 'eth_chainId' });
            setChainId(parseInt(chainIdHex, 16));
            
            setIsConnected(true);
            setActiveWallet('talisman');
            setProvider(window.talismanEth);
            console.log('✅ Talisman wallet connected:', accounts[0]);
          }
        } catch (error) {
          console.warn('Talisman connection failed, switching to demo mode:', error.message);
          // Fall back to demo mode
          connectWallet('demo');
          return;
        }
      } else {
        // Demo mode - simulate wallet connection
        const demoAccount = '0x742d35Cc6634C0532925a3b8D15d5C5B78Acc5e2';
        setAccount(demoAccount);
        setChainId(42161); // Arbitrum
        setIsConnected(true);
        setActiveWallet('demo');
        setProvider({ 
          demo: true, 
          request: async () => ({ result: 'demo_response' }),
          on: () => {},
          removeListener: () => {}
        });
        console.log('🎮 Demo wallet connected:', demoAccount);
        
        // Clear any previous errors when demo mode succeeds
        setError(null);
      }
    } catch (error) {
      console.error('Wallet connection error:', error);
      setError('Failed to connect wallet. Using demo mode instead.');
      
      // Always fall back to demo mode if everything fails
      if (walletType !== 'demo') {
        connectWallet('demo');
      }
    }
  };

  // Function to switch network
  const switchNetwork = async (targetChainId) => {
    try {
      setError(null);
      
      if (!provider) {
        setError('Wallet not connected.');
        return;
      }
      
      // Find network config
      const networkName = Object.keys(SUPPORTED_NETWORKS).find(
        key => SUPPORTED_NETWORKS[key].chainId === targetChainId
      );
      
      if (!networkName) {
        setError('Unsupported network.');
        return;
      }
      
      const network = SUPPORTED_NETWORKS[networkName];
      
      try {
        // Try to switch to the network
        await provider.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: `0x${targetChainId.toString(16)}` }],
        });
        
        // Update chain ID
        setChainId(targetChainId);
      } catch (switchError) {
        // If the network is not added to the wallet, add it
        if (switchError.code === 4902) {
          try {
            await provider.request({
              method: 'wallet_addEthereumChain',
              params: [
                {
                  chainId: `0x${targetChainId.toString(16)}`,
                  chainName: network.name,
                  rpcUrls: [network.rpcUrl],
                  blockExplorerUrls: [network.explorer],
                  nativeCurrency: {
                    name: 'Ether',
                    symbol: 'ETH',
                    decimals: 18,
                  },
                },
              ],
            });
            
            // Update chain ID
            setChainId(targetChainId);
          } catch (addError) {
            setError(`Error adding network: ${addError.message}`);
          }
        } else {
          setError(`Error switching network: ${switchError.message}`);
        }
      }
    } catch (error) {
      setError(`Error: ${error.message}`);
    }
  };

  // Event listeners for wallet changes
  useEffect(() => {
    const handleAccountsChanged = (accounts) => {
      if (accounts.length === 0) {
        setAccount(null);
        setIsConnected(false);
      } else {
        setAccount(accounts[0]);
      }
    };

    const handleChainChanged = (chainIdHex) => {
      setChainId(parseInt(chainIdHex, 16));
    };

    const handleDisconnect = () => {
      setAccount(null);
      setIsConnected(false);
      setActiveWallet(null);
      setProvider(null);
    };

    // Add event listeners if provider exists
    if (provider) {
      provider.on('accountsChanged', handleAccountsChanged);
      provider.on('chainChanged', handleChainChanged);
      provider.on('disconnect', handleDisconnect);
    }

    // Clean up event listeners
    return () => {
      if (provider) {
        provider.removeListener('accountsChanged', handleAccountsChanged);
        provider.removeListener('chainChanged', handleChainChanged);
        provider.removeListener('disconnect', handleDisconnect);
      }
    };
  }, [provider]);

  return (
    <Web3Context.Provider
      value={{
        account,
        chainId,
        provider,
        isConnected,
        activeWallet,
        connectWallet,
        switchNetwork,
        error,
      }}
    >
      {children}
    </Web3Context.Provider>
  );
};

export const useWeb3 = () => useContext(Web3Context);