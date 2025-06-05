#!/bin/bash

# Flash Arbitrage Setup Script
# This script deploys the flash arbitrage contract and sets up the entire system

echo "🚀 Setting up Flash Loan Arbitrage System..."
echo "💰 This is where you'll make REAL money!"

# Check if we're in the right directory
if [ ! -f "contracts/foundry.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Navigate to contracts directory
cd contracts

echo "📦 Installing Foundry dependencies..."
forge install

echo "🔧 Building smart contracts..."
forge build

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Contract build failed. Please check your Solidity code."
    exit 1
fi

echo "✅ Contracts built successfully!"

# Check if we have a private key set
if [ -z "$PRIVATE_KEY" ]; then
    echo "⚠️  PRIVATE_KEY environment variable not set"
    echo "💡 For testnet deployment, you can use a test private key"
    echo "🔑 For mainnet, NEVER share your real private key!"
    
    # Generate a test private key for demonstration
    TEST_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    echo "🧪 Using test private key for demonstration: $TEST_KEY"
    export PRIVATE_KEY=$TEST_KEY
fi

# Deploy to local network first for testing
echo "🏠 Starting local test deployment..."

# Start anvil in background if not running
if ! pgrep -f "anvil" > /dev/null; then
    echo "🔧 Starting local blockchain (Anvil)..."
    anvil --host 0.0.0.0 --port 8545 &
    ANVIL_PID=$!
    sleep 3
fi

# Deploy to local network
echo "📡 Deploying Flash Arbitrage Bot to local network..."
forge script script/DeployFlashArbitrage.s.sol:DeployFlashArbitrage --rpc-url http://localhost:8545 --broadcast --private-key $PRIVATE_KEY

if [ $? -eq 0 ]; then
    echo "✅ Local deployment successful!"
    
    # Extract deployed contract address
    CONTRACT_ADDRESS=$(forge script script/DeployFlashArbitrage.s.sol:DeployFlashArbitrage --rpc-url http://localhost:8545 --private-key $PRIVATE_KEY | grep "FlashArbitrageBot deployed at:" | awk '{print $4}')
    
    if [ ! -z "$CONTRACT_ADDRESS" ]; then
        echo "📋 Contract deployed at: $CONTRACT_ADDRESS"
        
        # Save contract address to config file
        echo "{\"flashArbitrageBot\": \"$CONTRACT_ADDRESS\"}" > ../src/config/contracts.json
        echo "💾 Contract address saved to src/config/contracts.json"
    fi
else
    echo "❌ Local deployment failed"
fi

# Instructions for mainnet deployment
echo ""
echo "🌐 FOR MAINNET DEPLOYMENT:"
echo "========================="
echo "1. Get ETH for gas fees (about 0.01 ETH should be enough)"
echo "2. Set your real private key: export PRIVATE_KEY=your_real_key"
echo "3. Deploy to mainnet:"
echo "   forge script script/DeployFlashArbitrage.s.sol:DeployFlashArbitrage --rpc-url https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY --broadcast --private-key \$PRIVATE_KEY --verify"
echo ""

# Set up environment file
echo "📝 Creating environment configuration..."
cat > ../.env.local << EOF
# Flash Arbitrage Configuration
VITE_FLASH_ARBITRAGE_CONTRACT=$CONTRACT_ADDRESS
VITE_NETWORK=localhost
VITE_RPC_URL=http://localhost:8545

# For production, replace with real values:
# VITE_NETWORK=mainnet
# VITE_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
# VITE_ALCHEMY_API_KEY=your_alchemy_key
EOF

echo "🎯 FLASH ARBITRAGE SYSTEM READY!"
echo "================================"
echo "💰 Your contract is deployed and ready to make money!"
echo "⚡ The frontend will automatically connect to your contract"
echo "🚀 Start the development server and begin arbitrage trading!"
echo ""
echo "💡 Remember: Flash loans let you trade with millions without having millions!"
echo "🎪 Price differences between DEXs = FREE MONEY for those who know how to grab it!"

# Return to project root
cd ..

echo "✅ Setup complete! Your flash arbitrage system is ready to generate profits! 💰"
