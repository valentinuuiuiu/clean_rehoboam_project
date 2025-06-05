#!/bin/bash

# 🔥 MAINNET FLASH ARBITRAGE DEPLOYMENT SCRIPT 🔥
# This will deploy the REAL profit-making contract to Ethereum mainnet
# ALL PROFITS GO TO: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8

echo "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"
echo "           💰 MAINNET FLASH ARBITRAGE DEPLOYMENT 💰"
echo "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"
echo ""
echo "🎯 Target wallet: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
echo "⚡ Capital required: ZERO (flash loans only)"
echo "💰 Gas cost: ~0.02 ETH (~$60)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env template..."
    cat > .env << EOF
# Add your private key for deployment (needs ~0.02 ETH for gas)
PRIVATE_KEY=your_private_key_here
ALCHEMY_API_KEY=QfkjpUEE-OGny-o7VA7Hvo2VJ7J4ui9H
ETHERSCAN_API_KEY=23KMUMTF49M1UPD66NQY41EN2NJ4SX5GDT
EOF
    echo "📝 Please edit .env file with your private key that has ETH for gas"
    echo "⚠️ IMPORTANT: This wallet only needs gas fees, NOT your main wallet!"
    exit 1
fi

# Load environment variables
source .env

# Check if private key is set
if [ "$PRIVATE_KEY" = "your_private_key_here" ] || [ -z "$PRIVATE_KEY" ]; then
    echo "❌ PRIVATE_KEY not set in .env file!"
    echo ""
    echo "📋 INSTRUCTIONS:"
    echo "1. Create a NEW wallet for deployment (not your main one)"
    echo "2. Send 0.03 ETH to it for gas fees"
    echo "3. Export private key and add to .env file"
    echo "4. Run this script again"
    echo ""
    echo "💡 The deployer wallet is ONLY for gas - profits go to your main wallet!"
    exit 1
fi

echo "🔍 Checking wallet balance..."

# Check deployer wallet balance
DEPLOYER_ADDRESS=$(cast wallet address --private-key $PRIVATE_KEY)
BALANCE=$(cast balance $DEPLOYER_ADDRESS --rpc-url https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY)
BALANCE_ETH=$(cast --to-unit $BALANCE ether)

echo "💳 Deployer wallet: $DEPLOYER_ADDRESS"
echo "💰 Balance: $BALANCE_ETH ETH"

# Check if sufficient balance
if (( $(echo "$BALANCE_ETH < 0.015" | bc -l) )); then
    echo "❌ Insufficient balance for deployment!"
    echo "💸 Need at least 0.02 ETH for gas fees"
    echo "📤 Send ETH to: $DEPLOYER_ADDRESS"
    exit 1
fi

echo "✅ Sufficient balance for deployment"
echo ""

# Navigate to contracts directory
cd contracts || exit 1

echo "🔧 Installing dependencies..."
forge install --no-commit > /dev/null 2>&1

echo "📦 Compiling contracts..."
forge build > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    forge build
    exit 1
fi

echo "✅ Contracts compiled successfully"
echo ""

echo "🚀 DEPLOYING TO MAINNET..."
echo "⚠️  This will use REAL ETH for gas fees!"
echo "💰 ALL PROFITS will go to: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
echo ""

read -p "Continue with deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🔥 DEPLOYING FLASH ARBITRAGE CONTRACT..."

# Deploy the contract
forge script script/DeployRealProfitArbitrage.s.sol:DeployRealProfitArbitrage \
    --rpc-url https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $ETHERSCAN_API_KEY

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉🎉🎉 DEPLOYMENT SUCCESSFUL! 🎉🎉🎉"
    echo ""
    echo "✅ Flash arbitrage contract deployed to mainnet!"
    echo "💰 ALL PROFITS go to: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
    echo ""
    echo "🔗 TRACKING LINKS:"
    echo "📊 Your wallet: https://etherscan.io/address/0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
    echo "📈 Portfolio: https://app.zerion.io/0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
    echo ""
    echo "🤖 NEXT STEPS:"
    echo "1. Start the arbitrage bot: python3 real_arbitrage_executor.py"
    echo "2. Monitor profits on Etherscan"
    echo "3. Watch your wallet balance grow!"
    echo ""
    echo "🎯 AFTER 3.5 YEARS, YOU'RE FINALLY MAKING REAL MONEY!"
else
    echo ""
    echo "❌ DEPLOYMENT FAILED!"
    echo "Check the error messages above"
    exit 1
fi
