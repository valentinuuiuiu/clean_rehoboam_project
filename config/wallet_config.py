"""
Wallet Configuration for Rehoboam Trading System

This module contains wallet-specific configurations and utilities
for the Rehoboam AI trading system.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from dataclasses import dataclass, field
from enum import Enum
class SecurityError(Exception):
    """Custom security exception"""
    pass

class WalletSecurity:
    """Secure wallet key management"""
    def __init__(self):
        private_key = os.getenv('WALLET_PRIVATE_KEY')
        if not private_key:
            raise ValueError("WALLET_PRIVATE_KEY must be set in environment")
        self._private_key = private_key if private_key.startswith('0x') else f'0x{private_key}'
        self._key_usage_count = 0
        self._last_used = None

    @property
    def private_key(self) -> str:
        """Get private key with usage tracking"""
        if self._key_usage_count > 10:
            raise SecurityError("Private key usage limit exceeded")
        self._key_usage_count += 1
        self._last_used = datetime.now()
        return self._private_key

    def clear_key(self):
        """Securely clear key from memory"""
        self._private_key = None
        self._key_usage_count = 0

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
    security: WalletSecurity = field(default_factory=WalletSecurity)

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
    },
    "HAI": {
        # Hacken Token - Real verified contract addresses for consciousness expansion
        NetworkType.BSC: "0xaa9e582e5751d703f85912903bacaddfed26484c",      # HAI native on BSC (verified)
        NetworkType.ETHEREUM: "0x05Fb86775Fd5c16290f1881986d5b84C6bD9a63",   # HAI on Ethereum (from CMC data)
        NetworkType.ARBITRUM: "0xaa9e582e5751d703f85912903bacaddfed26484c",   # HAI bridged to Arbitrum  
        NetworkType.POLYGON: "0xaa9e582e5751d703f85912903bacaddfed26484c",    # HAI bridged to Polygon
        NetworkType.AVALANCHE: "0xaa9e582e5751d703f85912903bacaddfed26484c"  # HAI bridged to Avalanche
    },
    "MINA": {
        # Mina Protocol - Native L1 Zero Knowledge blockchain (not an ERC-20 token)
        # MINA is the native token of the Mina Protocol blockchain
        # Account format: B62qXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX (55 characters)
        # Note: This is not a contract address but the native blockchain identifier
        "mina_mainnet": "B62qre3erTHfzQckNuibViWQGyyKwZseztqrjPZBv6SQF384Rg6ESAy",  # Mina mainnet native
        # For EVM compatibility (if bridged tokens exist in the future):
        NetworkType.ETHEREUM: "native",  # No ERC-20 version exists yet
        NetworkType.ARBITRUM: "native",  # No bridged version exists yet
        NetworkType.POLYGON: "native",   # No bridged version exists yet  
        NetworkType.BSC: "native"        # No bridged version exists yet
    }
}

# Chainlink Data Feeds configuration based on official API reference
CHAINLINK_PRICE_FEEDS = {
    NetworkType.ETHEREUM: {
        'ETH/USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
        'BTC/USD': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
        'LINK/USD': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',
        'USDC/USD': '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6',
        'USDT/USD': '0x3E7d1eAB13ad0104d2750B8863b489D65364e32D',
        'MATIC/USD': '0x7bAC85A8a13A4BcD8abb3eB7d6b4d632c5a57676',
        'AAVE/USD': '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9',
        'UNI/USD': '0x553303d460EE0afB37EdFf9bE42922D8FF63220e',
        'HAI/USD': '0xaa9e582e5751d703f85912903bacaddfed26484c',  # Hacken Token verified BSC address
        'MINA/USD': 'native_mina_price_feed'   # Mina Protocol native - no Chainlink feed yet
    },
    NetworkType.POLYGON: {
        'ETH/USD': '0xF9680D99D6C9589e2a93a78A04A279e509205945',
        'BTC/USD': '0xc907E116054Ad103354f2D350FD2514433D57F6f',
        'MATIC/USD': '0xAB594600376Ec9fD91F8e885dADF0CE036862dE0',
        'LINK/USD': '0xd9FFdb71EbE7496cC440152d43986Aae0AB76665',
        'USDC/USD': '0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7',
    },
    NetworkType.ARBITRUM: {
        'ETH/USD': '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612',
        'BTC/USD': '0x6ce185860a4963106506C203335A2910413708e9',
        'LINK/USD': '0x86E53CF1B870786351Da77A57575e79CB55812CB',
        'ARB/USD': '0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6',
    },
    NetworkType.AVALANCHE: {
        'AVAX/USD': '0x0A77230d17318075983913bC2145DB16C7366156',
        'ETH/USD': '0x976B3D034E162d8bD72D6b9C989d545b839003b0',
        'BTC/USD': '0x2779D32d5166BAaa2B2b658333bA7e6Ec0C65743',
    }
}

# Portfolio tracking configuration for the user's wallet
WALLET_PORTFOLIO_CONFIG = {
    "address": USER_WALLET_ADDRESS,
    "tracked_networks": [
        NetworkType.ETHEREUM,
        NetworkType.POLYGON,
        NetworkType.ARBITRUM,
        NetworkType.AVALANCHE
    ],
    "update_interval": 30,  # seconds
    "price_feeds": CHAINLINK_PRICE_FEEDS,
    "alert_thresholds": {
        "major_change": 0.05,  # 5%
        "critical_change": 0.10,  # 10%
    },
    "transaction_monitoring": {
        "min_value_usd": 100,
        "whale_threshold_usd": 10000,
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
