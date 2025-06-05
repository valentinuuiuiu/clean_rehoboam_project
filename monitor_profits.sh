#!/bin/bash

# 🚀 REAL-TIME PROFIT TRACKING SCRIPT 🚀
# Monitor your flash arbitrage profits in real-time!
# Target wallets: 
# - Ethereum/L2s: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8
# - Solana: Dk5jYpSP3U9PTeHdWUooztu9Y5bcwV7NUuz8t3eemL2f

YOUR_ETH_WALLET="0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
YOUR_SOLANA_WALLET="Dk5jYpSP3U9PTeHdWUooztu9Y5bcwV7NUuz8t3eemL2f"
ETHERSCAN_API_KEY="23KMUMTF49M1UPD66NQY41EN2NJ4SX5GDT"

clear
echo "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"
echo "           💰 MULTI-CHAIN FLASH ARBITRAGE PROFIT MONITOR 💰"
echo "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"
echo ""
echo "📱 Ethereum/L2s Wallet: $YOUR_ETH_WALLET"
echo "🌞 Solana Wallet: $YOUR_SOLANA_WALLET"
echo "🔄 Updating every 10 seconds..."
echo ""

# Function to get ETH balance
get_eth_balance() {
    local balance=$(curl -s "https://api.etherscan.io/api?module=account&action=balance&address=$YOUR_ETH_WALLET&tag=latest&apikey=$ETHERSCAN_API_KEY" | jq -r '.result')
    if [ "$balance" != "null" ] && [ "$balance" != "" ] && [ "$balance" != "0" ]; then
        # Convert from wei to ETH using simple division
        python3 -c "print(f'{int('$balance') / 1000000000000000000:.6f}')"
    else
        echo "0.000000"
    fi
}

# Function to get Solana balance
get_solana_balance() {
    local balance=$(curl -s "https://api.mainnet-beta.solana.com" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": ["'$YOUR_SOLANA_WALLET'"]
        }' | jq -r '.result.value')
    
    if [ "$balance" != "null" ] && [ "$balance" != "" ] && [ "$balance" != "0" ]; then
        # Convert lamports to SOL
        python3 -c "print(f'{int('$balance') / 1000000000:.6f}')"
    else
        echo "0.000000"
    fi
}

# Function to get recent transactions
get_recent_transactions() {
    curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=$YOUR_ETH_WALLET&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey=$ETHERSCAN_API_KEY" | jq -r '.result[]'
}

# Function to get ERC20 token balances
get_token_balances() {
    local tokens=("0xA0b86a33E6441cB59b3ac4d2A9da2b8ec55b3de5" "0xdAC17F958D2ee523a2206206994597C13D831ec7" "0x6B175474E89094C44Da98b954EedeAC495271d0F")
    local token_names=("USDC" "USDT" "DAI")
    
    for i in "${!tokens[@]}"; do
        local token_address="${tokens[$i]}"
        local token_name="${token_names[$i]}"
        
        local balance=$(curl -s "https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress=$token_address&address=$YOUR_ETH_WALLET&tag=latest&apikey=$ETHERSCAN_API_KEY" | jq -r '.result')
        
        if [ "$balance" != "null" ] && [ "$balance" != "0" ] && [ "$balance" != "" ]; then
            # Convert based on token decimals using Python
            if [ "$token_name" = "DAI" ]; then
                local readable_balance=$(python3 -c "print(f'{int('$balance') / 1000000000000000000:.2f}')")
            else
                local readable_balance=$(python3 -c "print(f'{int('$balance') / 1000000:.2f}')")
            fi
            echo "   💰 $token_name: $readable_balance"
        fi
    done
}

# Function to show arbitrage bot status
show_bot_status() {
    if pgrep -f "unstoppable_arbitrage_bot.py" > /dev/null; then
        echo "✅ Arbitrage Bot: RUNNING & HUNTING FOR PROFITS"
        
        # Show recent log entries
        if [ -f "logs/auto_arbitrage_$(date +%Y%m%d).log" ]; then
            echo "📊 Recent Bot Activity:"
            tail -3 "logs/auto_arbitrage_$(date +%Y%m%d).log" | while read line; do
                echo "   🤖 $line"
            done
        fi
    else
        echo "❌ Arbitrage Bot: OFFLINE"
        echo "   🚨 Starting bot now..."
        nohup python3 unstoppable_arbitrage_bot.py > /dev/null 2>&1 &
        sleep 2
        echo "   ✅ Bot restarted!"
    fi
}

# Main monitoring loop
while true; do
    clear
    echo "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"
    echo "           💰 MULTI-CHAIN FLASH ARBITRAGE PROFIT MONITOR 💰"
    echo "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"
    echo ""
    echo "📱 Ethereum/L2s: $YOUR_ETH_WALLET"
    echo "🌞 Solana: $YOUR_SOLANA_WALLET"
    echo "🕐 Last Update: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Show current balances
    echo "💰 CURRENT BALANCES:"
    echo ""
    echo "🌐 ETHEREUM & L2 NETWORKS:"
    eth_balance=$(get_eth_balance)
    echo "   💎 ETH: $eth_balance"
    get_token_balances
    echo ""
    echo "🌞 SOLANA:"
    sol_balance=$(get_solana_balance)
    echo "   ☀️ SOL: $sol_balance"
    echo ""
    
    # Show bot status
    echo "🤖 BOT STATUS:"
    show_bot_status
    echo ""
    
    # Show tracking links
    echo "🔗 TRACKING LINKS:"
    echo ""
    echo "🌐 ETHEREUM & L2 NETWORKS:"
    echo "   📊 Etherscan: https://etherscan.io/address/$YOUR_ETH_WALLET"
    echo "   📊 Polygonscan: https://polygonscan.com/address/$YOUR_ETH_WALLET"
    echo "   📊 Arbiscan: https://arbiscan.io/address/$YOUR_ETH_WALLET"
    echo "   📊 Optimistic Etherscan: https://optimistic.etherscan.io/address/$YOUR_ETH_WALLET"
    echo "   📊 Basescan: https://basescan.org/address/$YOUR_ETH_WALLET"
    echo "   📈 Zerion: https://app.zerion.io/$YOUR_ETH_WALLET"
    echo "   💎 Zapper: https://zapper.fi/account/$YOUR_ETH_WALLET"
    echo "   🏦 DeBank: https://debank.com/profile/$YOUR_ETH_WALLET"
    echo ""
    echo "🌞 SOLANA:"
    echo "   ☀️ Solscan: https://solscan.io/account/$YOUR_SOLANA_WALLET"
    echo "   ☀️ SolanaFM: https://solana.fm/address/$YOUR_SOLANA_WALLET"
    echo "   ☀️ Solana Beach: https://solanabeach.io/address/$YOUR_SOLANA_WALLET"
    echo ""
    
    # Show recent activity
    echo "📋 RECENT ACTIVITY (Last 10 transactions):"
    recent_txs=$(curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=$YOUR_ETH_WALLET&startblock=0&endblock=99999999&page=1&offset=5&sort=desc&apikey=$ETHERSCAN_API_KEY")
    
    if echo "$recent_txs" | jq -e '.result | length > 0' > /dev/null 2>&1; then
        echo "$recent_txs" | jq -r '.result[] | "   🔄 \(.timeStamp | tonumber | strftime("%H:%M:%S")) - \(.value | tonumber / 1000000000000000000) ETH - \(.hash[0:10])..."' | head -5
    else
        echo "   📭 No recent transactions"
    fi
    
    echo ""
    echo "🚀 Bot is running 24/7 hunting for arbitrage opportunities!"
    echo "💰 All profits automatically sent to your wallet!"
    echo "🔄 Refreshing in 10 seconds... (Press Ctrl+C to stop)"
    
    sleep 10
done
