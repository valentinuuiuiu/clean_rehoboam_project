#!/bin/bash

# Flash Loan Arbitrage - No Gas Money Setup Script
# For users who want to profit with zero upfront capital

echo "🔥 VETAL SHABAR RAKSHA - FLASH ARBITRAGE SETUP 🔥"
echo "=================================================="
echo "🎯 Goal: Profit from arbitrage with ZERO upfront capital"
echo "💡 Method: Flash loans + DEX arbitrage across rollups"
echo ""

# Check if we're in the contracts directory
if [ ! -f "foundry.toml" ]; then
    echo "❌ Please run this from the contracts directory"
    exit 1
fi

echo "📋 Prerequisites Check:"
echo "-----------------------"

# Check for Foundry
if command -v forge &> /dev/null; then
    echo "✅ Foundry installed"
else
    echo "❌ Foundry not found. Install from https://getfoundry.sh/"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# Flash Arbitrage Configuration - Deployment Keys
PRIVATE_KEY=your_private_key_here
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-key
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/your-key
OPTIMISM_RPC_URL=https://opt-mainnet.g.alchemy.com/v2/your-key
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/your-key
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/your-key

# Etherscan API keys for verification
ETHERSCAN_API_KEY=your_etherscan_key
ARBISCAN_API_KEY=your_arbiscan_key
OPTIMISTIC_ETHERSCAN_API_KEY=your_optimism_key
BASESCAN_API_KEY=your_base_key
POLYGONSCAN_API_KEY=your_polygon_key
EOF

    # Also create a .env.local for the frontend
    cat > ../.env.local << 'EOF'
# Flash Arbitrage Frontend Configuration - Alchemy Keys
VITE_ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-key
VITE_ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/your-key
VITE_OPTIMISM_RPC_URL=https://opt-mainnet.g.alchemy.com/v2/your-key
VITE_BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/your-key
VITE_POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/your-key

# Flash Arbitrage Contract Addresses (fill after deployment)
VITE_FLASH_ARBITRAGE_ETHEREUM=0x...
VITE_FLASH_ARBITRAGE_ARBITRUM=0x...
VITE_FLASH_ARBITRAGE_OPTIMISM=0x...
VITE_FLASH_ARBITRAGE_BASE=0x...
VITE_FLASH_ARBITRAGE_POLYGON=0x...
EOF
    echo "📄 Created .env template for contracts AND .env.local for frontend!"
    echo "🔑 You'll need:"
    echo "   - Private key (for deployment)"
    echo "   - Alchemy RPC URLs (get free keys from alchemy.com)"
    echo "   - API keys for contract verification (optional but recommended)"
    echo ""
    echo "💡 TIP: The frontend uses VITE_ prefixed variables for security"
    echo "💡 TIP: Even with no money for gas, you can use testnets first!"
    echo "💡 TIP: Alchemy provides free tier with 300M compute units/month"
    exit 1
fi

echo "✅ Environment file found"

echo ""
echo "🏗️  Building Flash Arbitrage Contract:"
echo "--------------------------------------"

# Build the contracts
forge build

if [ $? -eq 0 ]; then
    echo "✅ Contract built successfully"
else
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "🧪 Running Tests:"
echo "-----------------"

# Run tests
forge test -vv

echo ""
echo "📊 Flash Arbitrage System Overview:"
echo "==================================="
echo ""
echo "🎯 How it works:"
echo "   1. Scan DEXs for price differences across chains"
echo "   2. When profitable arbitrage found (>0.25% profit):"
echo "   3. → Flash loan 5-100 ETH from Aave (no collateral needed)"
echo "   4. → Buy token on cheaper DEX"
echo "   5. → Sell token on expensive DEX"
echo "   6. → Repay flash loan + fees"
echo "   7. → Keep the profit!"
echo ""
echo "💰 Profit sources:"
echo "   • Cross-DEX price differences (Uniswap vs Sushiswap)"
echo "   • Cross-chain arbitrage (Ethereum → Arbitrum)"
echo "   • Layer 2 opportunities (Optimism, Base, Polygon)"
echo "   • MEV opportunities on rollups"
echo ""
echo "🛡️  Risk protection:"
echo "   • If not profitable → entire transaction reverts"
echo "   • You pay $0 gas if arbitrage fails"
echo "   • Built-in slippage protection"
echo "   • Vetal guardian emergency functions"
echo ""
echo "🚀 Deployment Options:"
echo "======================"
echo ""
echo "🧪 Option 1: Testnet (Recommended first):"
echo "   forge script script/DeployFlashArbitrage.s.sol --rpc-url \$SEPOLIA_RPC_URL --broadcast --verify"
echo ""
echo "💰 Option 2: Mainnet (Real money):"
echo "   forge script script/DeployFlashArbitrage.s.sol --rpc-url \$ETHEREUM_RPC_URL --broadcast --verify"
echo ""
echo "⚡ Option 3: Layer 2 (Lower fees):"
echo "   forge script script/DeployFlashArbitrage.s.sol --rpc-url \$ARBITRUM_RPC_URL --broadcast --verify"
echo ""
echo "📱 Frontend Integration:"
echo "========================"
echo "After deployment, update the contract address in:"
echo "   src/components/NoGasArbitrage.tsx"
echo ""
echo "Then start the frontend:"
echo "   cd .. && npm run dev"
echo ""
echo "🎉 You're ready to profit with zero upfront capital!"
echo "✨ May Vetal guide your arbitrage to prosperity! ✨"
