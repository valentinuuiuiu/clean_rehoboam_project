#!/bin/bash

# CONTINUOUS ARBITRAGE BOT SERVICE
# Starts your AI brother automatically and keeps it running 24/7

echo "🤖 STARTING YOUR AI BROTHER - CONTINUOUS ARBITRAGE BOT"
echo "💰 Target: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
echo "⚡ Mode: 24/7 AUTOMATIC OPERATION"
echo ""

# Create logs directory
mkdir -p /home/shiva/clean_rehoboam_project/logs

# Function to start the bot
start_bot() {
    echo "🚀 Starting continuous arbitrage bot..."
    cd /home/shiva/clean_rehoboam_project
    
    # Run the bot with auto-restart on failure
    while true; do
        echo "🤖 Your AI brother is now working..."
        python3 continuous_arbitrage_bot.py
        
        echo "⚠️  Bot stopped. Restarting in 10 seconds..."
        sleep 10
    done
}

# Function to stop the bot
stop_bot() {
    echo "⏹️  Stopping arbitrage bot..."
    pkill -f continuous_arbitrage_bot.py
    echo "🤖 Your AI brother is resting."
}

# Function to check bot status
status_bot() {
    if pgrep -f continuous_arbitrage_bot.py > /dev/null; then
        echo "✅ Your AI brother is working!"
        echo "💰 Making you money right now..."
        echo "📊 Check logs: tail -f /home/shiva/clean_rehoboam_project/logs/arbitrage_bot.log"
    else
        echo "😴 Your AI brother is not running."
        echo "💡 Start with: ./start_arbitrage_service.sh start"
    fi
}

# Function to show profits
show_profits() {
    echo "💰 PROFIT TRACKER"
    echo "================="
    echo "🔗 Your wallet: https://etherscan.io/address/0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
    echo ""
    
    if [ -f "/home/shiva/clean_rehoboam_project/logs/bot_state.json" ]; then
        echo "📊 Bot Statistics:"
        cat /home/shiva/clean_rehoboam_project/logs/bot_state.json
    else
        echo "🤖 Bot not started yet or no profits recorded."
    fi
}

case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 2
        start_bot
        ;;
    status)
        status_bot
        ;;
    profits)
        show_profits
        ;;
    *)
        echo "🤖 ARBITRAGE BOT SERVICE CONTROL"
        echo "================================"
        echo "Usage: $0 {start|stop|restart|status|profits}"
        echo ""
        echo "Commands:"
        echo "  start   - Start your AI brother (24/7 money making)"
        echo "  stop    - Stop your AI brother" 
        echo "  restart - Restart your AI brother"
        echo "  status  - Check if your AI brother is working"
        echo "  profits - Check your profits and bot stats"
        echo ""
        echo "💰 Your wallet: 0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
        echo "🔗 Monitor: https://etherscan.io/address/0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
        ;;
esac
