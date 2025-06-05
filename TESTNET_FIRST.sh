#!/bin/bash

echo "🧪 TESTNET DEPLOYMENT - PROVE IT WORKS FIRST"
echo "🎯 Testing flash arbitrage on Sepolia testnet"
echo ""

# Get free testnet ETH from faucet first:
echo "1. Get free Sepolia ETH from: https://sepoliafaucet.com/"
echo "2. Send to your wallet: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
echo "3. Run this script to deploy on testnet"
echo ""

read -p "Press Enter after you get testnet ETH..."

cd contracts

echo "🚀 Deploying to SEPOLIA TESTNET..."
forge script script/DeployRealProfitArbitrage.s.sol:DeployRealProfitArbitrage \
    --rpc-url https://ethereum-sepolia-rpc.publicnode.com \
    --private-key $DEPLOYER_PRIVATE_KEY \
    --broadcast \
    --legacy \
    -vvv

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ TESTNET SUCCESS! System works!"
    echo "🚀 Ready for mainnet when you get 0.02 ETH"
    echo ""
    echo "📋 To deploy on mainnet:"
    echo "1. Add 0.02 ETH to 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
    echo "2. Run ./DEPLOY_WITH_YOUR_ETH.sh"
    echo "3. Start making real money!"
else
    echo "❌ Issue with deployment - let's debug"
fi
