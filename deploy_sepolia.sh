#!/bin/bash

# Sepolia Testnet Deployment Script
echo "🚀 DEPLOYING TO SEPOLIA TESTNET 🚀"
echo "=================================="

# Load environment variables
source .env

# Set Sepolia configuration
SEPOLIA_RPC="https://eth-sepolia.g.alchemy.com/v2/$ALCHEMY_API_KEY"
CHAIN_ID="11155111"
DEPLOYER_PRIVATE_KEY="$WALLET_PRIVATE_KEY"
DEPLOYER_ADDRESS="$USER_WALLET_ADDRESS"

echo "📍 Network: Sepolia Testnet (Chain ID: $CHAIN_ID)"
echo "🏦 Deployer Address: $DEPLOYER_ADDRESS"
echo "🔗 RPC URL: $SEPOLIA_RPC"
echo ""

# Check balance
echo "💰 Checking Sepolia ETH balance..."
BALANCE=$(cast balance $DEPLOYER_ADDRESS --rpc-url $SEPOLIA_RPC)
BALANCE_ETH=$(cast --to-unit $BALANCE ether)
echo "Balance: $BALANCE_ETH ETH"

if (( $(echo "$BALANCE_ETH < 0.01" | bc -l) )); then
    echo "❌ Insufficient Sepolia ETH! Need at least 0.01 ETH for deployment."
    echo "💡 Get Sepolia ETH from: https://sepoliafaucet.com/"
    exit 1
fi

echo "✅ Sufficient balance for deployment!"
echo ""

# Navigate to contracts directory
cd contracts || exit 1

# Install/update dependencies
echo "📦 Installing Foundry dependencies..."
forge install

# Compile contracts
echo "🔨 Compiling contracts..."
forge build

if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi

echo "✅ Contracts compiled successfully!"
echo ""

# Deploy to Sepolia
echo "🚀 Deploying RealProfitFlashArbitrage to Sepolia..."
echo "⏳ This may take a few minutes..."

DEPLOY_OUTPUT=$(forge script script/DeployRealProfitArbitrage.s.sol:DeployRealProfitArbitrage \
    --rpc-url $SEPOLIA_RPC \
    --private-key $DEPLOYER_PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $ETHERSCAN_API_KEY \
    --chain-id $CHAIN_ID 2>&1)

echo "$DEPLOY_OUTPUT"

# Extract contract address
CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -o "Contract deployed at: 0x[a-fA-F0-9]\{40\}" | grep -o "0x[a-fA-F0-9]\{40\}")

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "❌ Failed to extract contract address from deployment output"
    exit 1
fi

echo ""
echo "🎉 DEPLOYMENT SUCCESSFUL! 🎉"
echo "================================"
echo "📍 Network: Sepolia Testnet"
echo "📜 Contract Address: $CONTRACT_ADDRESS"
echo "🏦 Owner: $DEPLOYER_ADDRESS"
echo "🔗 Etherscan: https://sepolia.etherscan.io/address/$CONTRACT_ADDRESS"
echo ""

# Save contract address to .env
cd ..
echo "" >> .env
echo "# Sepolia Contract Addresses" >> .env
echo "SEPOLIA_ARBITRAGE_CONTRACT=$CONTRACT_ADDRESS" >> .env

echo "✅ Contract address saved to .env file"
echo ""
echo "🎯 READY FOR ARBITRAGE TESTING!"
echo "Use 'python test_sepolia_arbitrage.py' to start testing"
