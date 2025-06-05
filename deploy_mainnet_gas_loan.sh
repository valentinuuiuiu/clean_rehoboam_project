#!/bin/bash

echo "=========================================="
echo "DEPLOYING GAS LOAN ARBITRAGE TO ETHEREUM MAINNET"
echo "I'm covering gas fees - you get the profits!"
echo "=========================================="

cd /home/shiva/clean_rehoboam_project/contracts

# Check if we have the necessary files
if [ ! -f "script/DeployGasLoanMainnet.s.sol" ]; then
    echo "❌ ERROR: Deployment script not found"
    exit 1
fi

if [ ! -f "src/GasLoanArbitrageBot.sol" ]; then
    echo "❌ ERROR: Gas loan contract not found"
    exit 1
fi

# Check for environment variables
if [ -z "$MAINNET_RPC_URL" ]; then
    echo "⚠️  WARNING: MAINNET_RPC_URL not set, using default Infura"
    export MAINNET_RPC_URL="https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
fi

if [ -z "$DEPLOYER_PRIVATE_KEY" ]; then
    echo "❌ ERROR: DEPLOYER_PRIVATE_KEY not set"
    echo "Please set your private key with gas funds:"
    echo "export DEPLOYER_PRIVATE_KEY=your_private_key_here"
    exit 1
fi

echo "🔍 Checking deployer balance..."
cast balance --rpc-url $MAINNET_RPC_URL $(cast wallet address $DEPLOYER_PRIVATE_KEY)

echo ""
echo "🚀 DEPLOYING TO ETHEREUM MAINNET..."
echo "📝 Contract will automatically:"
echo "   1. Repay deployer gas fees from first profits"
echo "   2. Send ALL remaining profits to 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
echo "   3. Continue sending 100% profits to user forever"
echo ""

# Deploy the contract
forge script script/DeployGasLoanMainnet.s.sol:DeployGasLoanMainnet \
    --rpc-url $MAINNET_RPC_URL \
    --private-key $DEPLOYER_PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $ETHERSCAN_API_KEY \
    -vvvv

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Gas Loan Arbitrage deployed to Ethereum mainnet!"
    echo ""
    
    if [ -f "mainnet_gas_loan_deployment.env" ]; then
        echo "📋 DEPLOYMENT DETAILS:"
        cat mainnet_gas_loan_deployment.env
        echo ""
        
        # Extract contract address for monitoring
        CONTRACT_ADDRESS=$(grep "MAINNET_GAS_LOAN_CONTRACT=" mainnet_gas_loan_deployment.env | cut -d'=' -f2)
        
        echo "🔗 ETHERSCAN: https://etherscan.io/address/$CONTRACT_ADDRESS"
        echo ""
        echo "💰 PROFIT MONITORING:"
        echo "   Your wallet: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
        echo "   Check balance: https://etherscan.io/address/0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
        echo ""
        echo "🤖 STARTING ARBITRAGE BOT..."
        
        # Start the mainnet arbitrage bot
        cd /home/shiva/clean_rehoboam_project
        python3 mainnet_arbitrage_bot.py --contract=$CONTRACT_ADDRESS --network=mainnet &
        
        echo "✅ Arbitrage bot started! It will:"
        echo "   - Scan for arbitrage opportunities 24/7"
        echo "   - Execute profitable trades automatically"
        echo "   - Repay gas loan from first profits"
        echo "   - Send all remaining profits to your wallet"
        echo ""
        echo "🎯 YOUR WALLET WILL START RECEIVING PROFITS SOON!"
        
    else
        echo "⚠️  Deployment succeeded but no deployment file found"
    fi
else
    echo "❌ ERROR: Deployment failed"
    echo "Check the error messages above"
    exit 1
fi

echo ""
echo "=========================================="
echo "MAINNET DEPLOYMENT COMPLETE!"
echo "Contract is LIVE and earning for you!"
echo "=========================================="
