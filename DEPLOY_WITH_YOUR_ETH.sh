#!/bin/bash

echo "🚀 MAINNET FLASH ARBITRAGE DEPLOYMENT"
echo "🎯 Profit wallet: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
echo ""

# Using environment variable for security - SET THIS BEFORE RUNNING:
# export DEPLOYER_PRIVATE_KEY="your_private_key_here"
DEPLOYER_PRIVATE_KEY="${DEPLOYER_PRIVATE_KEY:-}"

if [ -z "$DEPLOYER_PRIVATE_KEY" ]; then
    echo "❌ ERROR: DEPLOYER_PRIVATE_KEY environment variable not set"
    echo "Set it with: export DEPLOYER_PRIVATE_KEY=\"your_private_key_here\""
    exit 1
fi

echo "💰 Checking wallet balance..."
cast balance --rpc-url https://rpc.flashbots.net 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8

echo "🔧 Deploying contract..."
cd contracts

forge script script/DeployRealProfitArbitrage.s.sol:DeployRealProfitArbitrage \
    --rpc-url https://rpc.flashbots.net \
    --private-key $DEPLOYER_PRIVATE_KEY \
    --broadcast \
    --legacy \
    -vvv

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Contract deployed!"
    echo "💰 Profits will flow to: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
    echo ""
    echo "🤖 Starting arbitrage bot..."
    cd ..
    python3 real_arbitrage_executor.py &
    echo "🚀 BOT RUNNING! Money incoming!"
else
    echo "❌ Deployment failed"
fi
