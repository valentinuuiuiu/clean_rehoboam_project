#!/bin/bash

# Flash Arbitrage Environment Checker
# Verifies that Alchemy RPC URLs are working

echo "🔍 FLASH ARBITRAGE - ENVIRONMENT CHECK"
echo "======================================"

# Check if .env.local exists
if [ ! -f "../.env.local" ]; then
    echo "❌ .env.local not found in parent directory"
    echo "💡 Run ./setup_flash_arbitrage.sh first to create template"
    exit 1
fi

echo "✅ Found .env.local file"

# Source the environment variables
set -a
source ../.env.local
set +a

echo ""
echo "🌐 Testing RPC Connections:"
echo "-------------------------"

# Function to test RPC endpoint
test_rpc() {
    local name=$1
    local url=$2
    
    if [ -z "$url" ] || [ "$url" = "https://eth-mainnet.g.alchemy.com/v2/your-key" ]; then
        echo "⚠️  $name: Not configured (using template URL)"
        return 1
    fi
    
    # Test with a simple eth_blockNumber call
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
        "$url" 2>/dev/null)
    
    if echo "$response" | grep -q '"result"'; then
        echo "✅ $name: Connected successfully"
        return 0
    else
        echo "❌ $name: Connection failed"
        return 1
    fi
}

# Test all networks
test_rpc "Ethereum" "$VITE_ETHEREUM_RPC_URL"
test_rpc "Arbitrum" "$VITE_ARBITRUM_RPC_URL"
test_rpc "Optimism" "$VITE_OPTIMISM_RPC_URL"
test_rpc "Base" "$VITE_BASE_RPC_URL"
test_rpc "Polygon" "$VITE_POLYGON_RPC_URL"

echo ""
echo "💰 Contract Addresses:"
echo "---------------------"

if [ -n "$VITE_FLASH_ARBITRAGE_ETHEREUM" ] && [ "$VITE_FLASH_ARBITRAGE_ETHEREUM" != "0x..." ]; then
    echo "✅ Ethereum: $VITE_FLASH_ARBITRAGE_ETHEREUM"
else
    echo "⚠️  Ethereum: Not deployed yet"
fi

if [ -n "$VITE_FLASH_ARBITRAGE_ARBITRUM" ] && [ "$VITE_FLASH_ARBITRAGE_ARBITRUM" != "0x..." ]; then
    echo "✅ Arbitrum: $VITE_FLASH_ARBITRAGE_ARBITRUM"
else
    echo "⚠️  Arbitrum: Not deployed yet"
fi

echo ""
echo "🎯 Flash Arbitrage Readiness:"
echo "----------------------------"

configured_networks=0
deployed_contracts=0

# Count configured networks
[ -n "$VITE_ETHEREUM_RPC_URL" ] && [ "$VITE_ETHEREUM_RPC_URL" != "https://eth-mainnet.g.alchemy.com/v2/your-key" ] && ((configured_networks++))
[ -n "$VITE_ARBITRUM_RPC_URL" ] && [ "$VITE_ARBITRUM_RPC_URL" != "https://arb-mainnet.g.alchemy.com/v2/your-key" ] && ((configured_networks++))
[ -n "$VITE_OPTIMISM_RPC_URL" ] && [ "$VITE_OPTIMISM_RPC_URL" != "https://opt-mainnet.g.alchemy.com/v2/your-key" ] && ((configured_networks++))
[ -n "$VITE_BASE_RPC_URL" ] && [ "$VITE_BASE_RPC_URL" != "https://base-mainnet.g.alchemy.com/v2/your-key" ] && ((configured_networks++))
[ -n "$VITE_POLYGON_RPC_URL" ] && [ "$VITE_POLYGON_RPC_URL" != "https://polygon-mainnet.g.alchemy.com/v2/your-key" ] && ((configured_networks++))

# Count deployed contracts
[ -n "$VITE_FLASH_ARBITRAGE_ETHEREUM" ] && [ "$VITE_FLASH_ARBITRAGE_ETHEREUM" != "0x..." ] && ((deployed_contracts++))
[ -n "$VITE_FLASH_ARBITRAGE_ARBITRUM" ] && [ "$VITE_FLASH_ARBITRAGE_ARBITRUM" != "0x..." ] && ((deployed_contracts++))

echo "📊 Networks configured: $configured_networks/5"
echo "🚀 Contracts deployed: $deployed_contracts/5"

if [ $configured_networks -eq 0 ]; then
    echo ""
    echo "❌ NO NETWORKS CONFIGURED"
    echo "🔧 Next steps:"
    echo "   1. Get free Alchemy API key from https://alchemy.com"
    echo "   2. Edit ../.env.local with your Alchemy URLs"
    echo "   3. Run this check again"
elif [ $configured_networks -lt 3 ]; then
    echo ""
    echo "⚠️  PARTIAL CONFIGURATION"
    echo "💡 You have some networks configured but consider adding more for better arbitrage opportunities"
elif [ $deployed_contracts -eq 0 ]; then
    echo ""
    echo "🏗️  READY FOR DEPLOYMENT"
    echo "🔧 Next steps:"
    echo "   1. Deploy contracts: forge script script/DeployFlashArbitrage.s.sol --rpc-url \$ETHEREUM_RPC_URL --broadcast"
    echo "   2. Update contract addresses in .env.local"
    echo "   3. Start the frontend: cd .. && npm run dev"
else
    echo ""
    echo "🎉 FLASH ARBITRAGE READY!"
    echo "✨ You can now profit with zero upfront capital!"
    echo "🚀 Start the frontend: cd .. && npm run dev"
fi

echo ""
echo "📚 Quick Reference:"
echo "   • Test deployment: Use testnets first (Sepolia, Arbitrum Goerli)"
echo "   • Minimum profit: 0.25% to cover flash loan fees + gas"
echo "   • Best opportunities: High volume tokens during market volatility"
echo "   • Risk: Zero! Failed arbitrage = transaction reverts = no gas cost"
echo ""
echo "🌟 May Vetal guide your arbitrage to prosperity!"
