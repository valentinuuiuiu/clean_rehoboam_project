#!/usr/bin/env python3
"""Test script to check environment variables usage"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print('=== ENVIRONMENT VARIABLES STATUS ===')
print(f'OPENAI_API_KEY: {"✅ SET" if os.getenv("OPENAI_API_KEY") else "❌ NOT SET"}')
print(f'ALCHEMY_API_KEY: {"✅ SET" if os.getenv("ALCHEMY_API_KEY") else "❌ NOT SET"}')
print(f'WALLET_PRIVATE_KEY: {"✅ SET" if os.getenv("WALLET_PRIVATE_KEY") else "❌ NOT SET"}')
print(f'ETHERSCAN_API_KEY: {"✅ SET" if os.getenv("ETHERSCAN_API_KEY") else "❌ NOT SET"}')
print(f'API_PORT: {os.getenv("API_PORT", "default")}')
print(f'USER_WALLET_ADDRESS: {os.getenv("USER_WALLET_ADDRESS", "not set")}')
print(f'DATABASE_URL: {"✅ SET" if os.getenv("DATABASE_URL") else "❌ NOT SET"}')
print(f'JWT_SECRET: {"✅ SET" if os.getenv("JWT_SECRET") else "❌ NOT SET"}')
print(f'MCP_TOKEN: {"✅ SET" if os.getenv("MCP_TOKEN") else "❌ NOT SET"}')
print()

# Test key imports
try:
    from config.wallet_config import USER_WALLET
    print(f'✅ Wallet Config: {USER_WALLET.address}')
except Exception as e:
    print(f'❌ Wallet Config Error: {e}')

try:
    from utils.web3_service import web3_service
    print('✅ Web3 Service: OK')
except Exception as e:
    print(f'❌ Web3 Service Error: {e}')

try:
    from utils.mcp_auth import JWT_SECRET, MCP_TOKEN
    print('✅ MCP Auth: OK')
except Exception as e:
    print(f'❌ MCP Auth Error: {e}')

print('\n=== ENVIRONMENT VARIABLES USAGE SUMMARY ===')
print("""
🔧 Core Configuration:
   • API_PORT: Controls backend server port (currently: 5002)
   • DATABASE_URL: PostgreSQL connection string
   • JWT_SECRET: Authentication token encryption
   
🔑 API Keys:
   • OPENAI_API_KEY: AI/ML model access for trading intelligence
   • ALCHEMY_API_KEY: Ethereum/L2 RPC access for blockchain interactions
   • ETHERSCAN_API_KEY: Transaction verification and gas estimation
   • INFURA_API_KEY: Backup RPC provider
   • DEEPSEEK_API_KEY: Alternative AI provider
   • GEMINI_API_KEY: Alternative AI provider
   
💰 Wallet & Security:
   • WALLET_PRIVATE_KEY: Main wallet for executing trades
   • USER_WALLET_ADDRESS: Public address for monitoring
   • ENCRYPTION_KEY: Additional data encryption
   
🌐 Network Configuration:
   • ETHEREUM_RPC_URL: Custom Ethereum mainnet RPC
   • POLYGON_RPC_URL: Polygon network access
   • ARBITRUM_RPC_URL: Arbitrum L2 access
   • OPTIMISM_RPC_URL: Optimism L2 access
   
🔧 Trading Parameters:
   • MAX_SLIPPAGE_PERCENT: Maximum acceptable slippage (2.0%)
   • GAS_PRICE_MULTIPLIER: Gas price adjustment factor (1.2x)
   • LOG_LEVEL: Application logging verbosity
   
🔗 MCP (Model Context Protocol):
   • MCP_ENDPOINT: AI model communication endpoint
   • MCP_TOKEN: Authentication for MCP services
   • MCP_REGISTRY_URL: Service discovery endpoint
""")
