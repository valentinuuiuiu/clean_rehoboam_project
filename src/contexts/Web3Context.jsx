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
};

export const Web3ContextProvider = ({ children }) => {
  const [account, setAccount] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [provider, setProvider] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [activeWallet, setActiveWallet] = useState(null);
  const [error, setError] = useState(null);

  // Function to connect wallet
  const connectWallet = async (walletType) => {
    try {
      setError(null);
      
      if (walletType === 'metamask') {
        // Check if MetaMask is installed
        if (window.ethereum) {
          try {
            // Request account access
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            setAccount(accounts[0]);
            
            // Get chain ID
            const chainIdHex = await window.ethereum.request({ method: 'eth_chainId' });
            setChainId(parseInt(chainIdHex, 16));
            
            setIsConnected(true);
            setActiveWallet('metamask');
            setProvider(window.ethereum);
          } catch (error) {
            setError('Error connecting to MetaMask: ' + error.message);
          }
        } else {
          setError('MetaMask is not installed. Please install it to continue.');
        }
      } else if (walletType === 'talisman') {
        // Check if Talisman is installed
        if (window.talismanEth) {
          try {
            // Request account access
            const accounts = await window.talismanEth.request({ method: 'eth_requestAccounts' });
            setAccount(accounts[0]);
            
            // Get chain ID
            const chainIdHex = await window.talismanEth.request({ method: 'eth_chainId' });
            setChainId(parseInt(chainIdHex, 16));
            
            setIsConnected(true);
            setActiveWallet('talisman');
            setProvider(window.talismanEth);
          } catch (error) {
            setError('Error connecting to Talisman: ' + error.message);
          }
        } else {
          setError('Talisman is not installed. Please install it to continue.');
        }
      }
    } catch (error) {
      setError('Error connecting wallet: ' + error.message);
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