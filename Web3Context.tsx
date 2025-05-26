/// <reference types="vite/client" />

import React, { createContext, useContext, useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { Web3Provider as EthersWeb3Provider } from '@ethersproject/providers';

declare global {
  interface Window {
    ethereum?: any;
    talismanEth?: any;
  }
}

// Network configuration type
type NetworkConfig = {
  chainId: number;
  name: string;
  rpcUrl: string;
  explorer: string;
};

type SupportedNetworks = {
  [key: string]: NetworkConfig;
};

interface Web3ContextType {
  account: string | null;
  chainId: number | null;
  provider: EthersWeb3Provider | null;
  isConnected: boolean;
  activeWallet: 'metamask' | 'talisman' | null;
  connectWallet: (walletType: 'metamask' | 'talisman') => Promise<void>;
  switchNetwork: (chainId: number) => Promise<void>;
  error: string | null;
}

// Supported networks configuration
export const SUPPORTED_NETWORKS: SupportedNetworks = {
  ETHEREUM: {
    chainId: 1,
    name: 'Ethereum',
    rpcUrl: `https://eth-mainnet.g.alchemy.com/v2/${process.env.VITE_ALCHEMY_API_KEY || ''}`,
    explorer: 'https://etherscan.io'
  },
  ARBITRUM: {
    chainId: 42161,
    name: 'Arbitrum One',
    rpcUrl: `https://arb-mainnet.g.alchemy.com/v2/${process.env.VITE_ALCHEMY_API_KEY || ''}`,
    explorer: 'https://arbiscan.io'
  },
  OPTIMISM: {
    chainId: 10,
    name: 'Optimism',
    rpcUrl: `https://opt-mainnet.g.alchemy.com/v2/${process.env.VITE_ALCHEMY_API_KEY || ''}`,
    explorer: 'https://optimistic.etherscan.io'
  },
  POLYGON: {
    chainId: 137,
    name: 'Polygon',
    rpcUrl: `https://polygon-mainnet.g.alchemy.com/v2/${process.env.VITE_ALCHEMY_API_KEY || ''}`,
    explorer: 'https://polygonscan.com'
  }
};

const Web3Context = createContext<Web3ContextType>({
  account: null,
  chainId: null,
  provider: null,
  isConnected: false,
  activeWallet: null,
  connectWallet: async () => {},
  switchNetwork: async () => {},
  error: null,
});

export const Web3ContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [account, setAccount] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [provider, setProvider] = useState<EthersWeb3Provider | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeWallet, setActiveWallet] = useState<'metamask' | 'talisman' | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const connectWallet = async (walletType: 'metamask' | 'talisman') => {
    try {
      let selectedProvider;
      
      if (walletType === 'talisman') {
        if (typeof window.talismanEth === 'undefined') {
          throw new Error('Talisman wallet is not installed');
        }
        selectedProvider = window.talismanEth;
      } else {
        if (typeof window.ethereum === 'undefined') {
          throw new Error('MetaMask is not installed');
        }
        selectedProvider = window.ethereum;
      }

      setIsLoading(true);
      setError(null);

      const ethersProvider = new ethers.BrowserProvider(selectedProvider);
      const accounts = await selectedProvider.request({ 
        method: 'eth_requestAccounts' 
      });

      const network = await ethersProvider.getNetwork();
      setAccount(accounts[0]);
      setChainId(Number(network.chainId));
      setProvider(ethersProvider as unknown as EthersWeb3Provider);
      setActiveWallet(walletType);
      setError(null);

      console.log('Wallet connected:', {
        type: walletType,
        account: accounts[0],
        chainId: Number(network.chainId),
        network: network.name
      });
    } catch (err) {
      console.error('Wallet connection error:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect wallet');
    } finally {
      setIsLoading(false);
    }
  };

  const switchNetwork = async (targetChainId: number) => {
    const provider = activeWallet === 'talisman' ? window.talismanEth : window.ethereum;
    if (!provider) {
      setError('No wallet provider found');
      return;
    }

    const networkEntry = Object.entries(SUPPORTED_NETWORKS).find(
      ([_, network]) => network.chainId === targetChainId
    );

    if (!networkEntry) {
      setError('Unsupported network');
      return;
    }

    const network = networkEntry[1];

    try {
      await provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${targetChainId.toString(16)}` }],
      });
    } catch (switchError: any) {
      // This error code indicates that the chain has not been added to the wallet
      if (switchError.code === 4902) {
        try {
          await provider.request({
            method: 'wallet_addEthereumChain',
            params: [{
              chainId: `0x${targetChainId.toString(16)}`,
              chainName: network.name,
              nativeCurrency: {
                name: network.name,
                symbol: network.name.substring(0, 3).toUpperCase(),
                decimals: 18,
              },
              rpcUrls: [network.rpcUrl],
              blockExplorerUrls: [network.explorer],
            }],
          });
        } catch (addError) {
          console.error('Add network error:', addError);
          setError('Failed to add network to wallet');
        }
      } else {
        console.error('Switch network error:', switchError);
        setError('Failed to switch network');
      }
    }
  };

  useEffect(() => {
    if (provider) {
      const handleAccountsChanged = (accounts: string[]) => {
        setAccount(accounts[0] || null);
      };

      const handleChainChanged = (chainId: string) => {
        setChainId(parseInt(chainId));
      };

      const handleDisconnect = () => {
        setAccount(null);
        setChainId(null);
        setProvider(null);
        setActiveWallet(null);
      };

      const walletProvider = activeWallet === 'talisman' ? window.talismanEth : window.ethereum;
      if (walletProvider) {
        walletProvider.on('accountsChanged', handleAccountsChanged);
        walletProvider.on('chainChanged', handleChainChanged);
        walletProvider.on('disconnect', handleDisconnect);

        return () => {
          walletProvider.removeListener('accountsChanged', handleAccountsChanged);
          walletProvider.removeListener('chainChanged', handleChainChanged);
          walletProvider.removeListener('disconnect', handleDisconnect);
        };
      }
    }
  }, [provider, activeWallet]);

  return (
    <Web3Context.Provider value={{
      account,
      chainId,
      provider,
      isConnected: !!account,
      activeWallet,
      connectWallet,
      switchNetwork,
      error,
      isLoading,
    }}>
      {children}
    </Web3Context.Provider>
  );
};

export const useWeb3 = () => useContext(Web3Context);