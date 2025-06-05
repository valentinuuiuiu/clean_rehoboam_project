"""
Wallet Configuration for Rehoboam Trading System

This module contains wallet-specific configurations and utilities
for the Rehoboam AI trading system.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class WalletType(Enum):
    """Supported wallet types"""
    METAMASK = "metamask"
    HARDWARE = "hardware"
    PAPER = "paper"

class NetworkType(Enum):
    """Supported network types"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    AVALANCHE = "avalanche"
    BSC = "bsc"
    OPTIMISM = "optimism"

@dataclass
class WalletConfig:
    """Wallet configuration dataclass"""
    address: str
    wallet_type: WalletType
    name: str
    networks: List[NetworkType]
    is_primary: bool = False
    risk_tolerance: str = "medium"  # low, medium, high
    max_position_size: float = 0.1  # 10% of portfolio
    auto_rebalance: bool = True
    stop_loss_threshold: float = 0.05  # 5% stop loss
    take_profit_threshold: float = 0.2  # 20% take profit

# Primary user wallet configuration
USER_WALLET_ADDRESS = "0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"

USER_WALLET = WalletConfig(
    address=USER_WALLET_ADDRESS,
    wallet_type=WalletType.METAMASK,
    name="Rehoboam Primary Wallet",
    networks=[
        NetworkType.ETHEREUM,
        NetworkType.POLYGON,
        NetworkType.ARBITRUM,
        NetworkType.AVALANCHE
    ],
    is_primary=True,
    risk_tolerance="medium",
    max_position_size=0.15,  # 15% max position
    auto_rebalance=True,
    stop_loss_threshold=0.03,  # 3% stop loss for conservative approach
    take_profit_threshold=0.25  # 25% take profit
)

# Network configurations with RPC endpoints
NETWORK_CONFIGS = {
    NetworkType.ETHEREUM: {
        "name": "Ethereum Mainnet",
        "chain_id": 1,
        "rpc_urls": [
            f"https://mainnet.infura.io/v3/{os.getenv('INFURA_API_KEY', '')}",
            "https://ethereum.publicnode.com",
            "https://rpc.ankr.com/eth"
        ],
        "explorer_url": "https://etherscan.io",
        "native_currency": {
            "name": "Ethereum",
            "symbol": "ETH",
            "decimals": 18
        },
        "gas_price_gwei": 20,
        "max_gas_price_gwei": 100
    },
    NetworkType.POLYGON: {
        "name": "Polygon Mainnet",
        "chain_id": 137,
        "rpc_urls": [
            "https://polygon-rpc.com",
            "https://rpc.ankr.com/polygon",
            "https://polygon.publicnode.com"
        ],
        "explorer_url": "https://polygonscan.com",
        "native_currency": {
            "name": "Polygon",
            "symbol": "MATIC",
            "decimals": 18
        },
        "gas_price_gwei": 30,
        "max_gas_price_gwei": 200
    },
    NetworkType.ARBITRUM: {
        "name": "Arbitrum One",
        "chain_id": 42161,
        "rpc_urls": [
            "https://arb1.arbitrum.io/rpc",
            "https://rpc.ankr.com/arbitrum",
            "https://arbitrum.publicnode.com"
        ],
        "explorer_url": "https://arbiscan.io",
        "native_currency": {
            "name": "Ethereum",
            "symbol": "ETH",
            "decimals": 18
        },
        "gas_price_gwei": 0.1,
        "max_gas_price_gwei": 2
    },
    NetworkType.AVALANCHE: {
        "name": "Avalanche C-Chain",
        "chain_id": 43114,
        "rpc_urls": [
            "https://api.avax.network/ext/bc/C/rpc",
            "https://rpc.ankr.com/avalanche",
            "https://avalanche.publicnode.com"
        ],
        "explorer_url": "https://snowtrace.io",
        "native_currency": {
            "name": "Avalanche",
            "symbol": "AVAX",
            "decimals": 18
        },
        "gas_price_gwei": 25,
        "max_gas_price_gwei": 100
    }
}

# DeFi protocols and DEX configurations for each network
DEFI_PROTOCOLS = {
    NetworkType.ETHEREUM: {
        "uniswap_v3": {
            "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"
        },
        "aave_v3": {
            "pool": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
            "pool_data_provider": "0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3"
        },
        "compound_v3": {
            "comet": "0xc3d688B66703497DAA19211EEdff47f25384cdc3"
        }
    },
    NetworkType.POLYGON: {
        "quickswap": {
            "router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
        },
        "aave_v3": {
            "pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
        }
    },
    NetworkType.ARBITRUM: {
        "uniswap_v3": {
            "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984"
        },
        "gmx": {
            "vault": "0x489ee077994B6658eAfA855C308275EAd8097C4A"
        }
    },
    NetworkType.AVALANCHE: {
        "traderjoe": {
            "router": "0x60aE616a2155Ee3d9A68541Ba4544862310933d4"
        },
        "aave_v3": {
            "pool": "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
        }
    }
}

# Token addresses for cross-chain tracking
MAJOR_TOKENS = {
    "USDC": {
        NetworkType.ETHEREUM: "0xA0b86a33E6441b80bD9aE2F31D28Ca5Ff8E6B1F1",
        NetworkType.POLYGON: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        NetworkType.ARBITRUM: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
        NetworkType.AVALANCHE: "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
    },
    "USDT": {
        NetworkType.ETHEREUM: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        NetworkType.POLYGON: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        NetworkType.ARBITRUM: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        NetworkType.AVALANCHE: "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7"
    },
    "WETH": {
        NetworkType.ETHEREUM: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        NetworkType.POLYGON: "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        NetworkType.ARBITRUM: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        NetworkType.AVALANCHE: "0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB"
    },
    "WBTC": {
        NetworkType.ETHEREUM: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        NetworkType.POLYGON: "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
        NetworkType.ARBITRUM: "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
        NetworkType.AVALANCHE: "0x50b7545627a5162F82A992c33b87aDc75187B218"
    }
}

def get_wallet_config() -> WalletConfig:
    """Get the primary user wallet configuration"""
    return USER_WALLET

def get_network_config(network: NetworkType) -> Dict:
    """Get configuration for a specific network"""
    return NETWORK_CONFIGS.get(network, {})

def get_defi_protocols(network: NetworkType) -> Dict:
    """Get DeFi protocol addresses for a specific network"""
    return DEFI_PROTOCOLS.get(network, {})

def get_token_address(token_symbol: str, network: NetworkType) -> Optional[str]:
    """Get token contract address for a specific network"""
    return MAJOR_TOKENS.get(token_symbol.upper(), {}).get(network)

def is_wallet_address_valid(address: str) -> bool:
    """Validate if an Ethereum address is properly formatted"""
    try:
        # Basic validation - should start with 0x and be 42 characters long
        if not address.startswith('0x') or len(address) != 42:
            return False
        
        # Check if it's a valid hex string
        int(address[2:], 16)
        return True
    except ValueError:
        return False

def get_supported_networks() -> List[NetworkType]:
    """Get list of supported networks for the user wallet"""
    return USER_WALLET.networks
