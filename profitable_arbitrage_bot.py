import ccxt
import time
import numpy as np
from threading import Thread

# CONFIG - CHANGE THESE TO YOUR EXCHANGE API KEYS
EXCHANGES = {
    'binance': {
        'apiKey': 'YOUR_API_KEY',
        'secret': 'YOUR_SECRET',
        'enableRateLimit': True
    },
    'kucoin': {
        'apiKey': 'YOUR_API_KEY',
        'secret': 'YOUR_SECRET',
        'enableRateLimit': True
    }
}

# ARBITRAGE SETTINGS
PAIRS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
MIN_PROFIT_PERCENT = 0.3  # 0.3% profit threshold
TRADE_AMOUNT = 100  # USDT amount per trade

class ArbitrageBot:
    def __init__(self):
        self.exchanges = {name: ccxt.__dict__[name](config) for name, config in EXCHANGES.items()}
        self.running = True
        
    def get_prices(self):
        prices = {}
        for pair in PAIRS:
            prices[pair] = {}
            for exchange_name, exchange in self.exchanges.items():
                try:
                    orderbook = exchange.fetch_order_book(pair)
                    prices[pair][exchange_name] = {
                        'bid': orderbook['bids'][0][0],
                        'ask': orderbook['asks'][0][0]
                    }
                except Exception as e:
                    print(f"Error fetching {pair} from {exchange_name}: {str(e)}")
        return prices

    def find_opportunities(self, prices):
        opportunities = []
        for pair in PAIRS:
            exchanges = list(prices[pair].keys())
            for i in range(len(exchanges)):
                for j in range(i+1, len(exchanges)):
                    ex1 = exchanges[i]
                    ex2 = exchanges[j]
                    
                    # Check buy low (ex1), sell high (ex2)
                    if prices[pair][ex1]['ask'] < prices[pair][ex2]['bid']:
                        spread = prices[pair][ex2]['bid'] - prices[pair][ex1]['ask']
                        profit_percent = (spread / prices[pair][ex1]['ask']) * 100
                        if profit_percent >= MIN_PROFIT_PERCENT:
                            opportunities.append({
                                'type': 'buy-sell',
                                'pair': pair,
                                'buy_exchange': ex1,
                                'sell_exchange': ex2,
                                'buy_price': prices[pair][ex1]['ask'],
                                'sell_price': prices[pair][ex2]['bid'],
                                'profit_percent': profit_percent
                            })
                    
                    # Check buy low (ex2), sell high (ex1)
                    if prices[pair][ex2]['ask'] < prices[pair][ex1]['bid']:
                        spread = prices[pair][ex1]['bid'] - prices[pair][ex2]['ask']
                        profit_percent = (spread / prices[pair][ex2]['ask']) * 100
                        if profit_percent >= MIN_PROFIT_PERCENT:
                            opportunities.append({
                                'type': 'buy-sell',
                                'pair': pair,
                                'buy_exchange': ex2,
                                'sell_exchange': ex1,
                                'buy_price': prices[pair][ex2]['ask'],
                                'sell_price': prices[pair][ex1]['bid'],
                                'profit_percent': profit_percent
                            })
        return opportunities

    def execute_trade(self, opportunity):
        try:
            buy_ex = self.exchanges[opportunity['buy_exchange']]
            sell_ex = self.exchanges[opportunity['sell_exchange']]
            
            # Calculate amount to buy
            amount = TRADE_AMOUNT / opportunity['buy_price']
            
            # Execute buy order
            print(f"Buying {amount} {opportunity['pair'].split('/')[0]} on {opportunity['buy_exchange']} at {opportunity['buy_price']}")
            buy_order = buy_ex.create_market_buy_order(opportunity['pair'], amount)
            
            # Execute sell order
            print(f"Selling {amount} {opportunity['pair'].split('/')[0]} on {opportunity['sell_exchange']} at {opportunity['sell_price']}")
            sell_order = sell_ex.create_market_sell_order(opportunity['pair'], amount)
            
            profit = (amount * opportunity['sell_price']) - TRADE_AMOUNT
            print(f"Trade completed! Profit: ${profit:.2f}")
            return profit
            
        except Exception as e:
            print(f"Trade failed: {str(e)}")
            return 0

    def run(self):
        total_profit = 0
        while self.running:
            try:
                prices = self.get_prices()
                opportunities = self.find_opportunities(prices)
                
                if opportunities:
                    best_opp = max(opportunities, key=lambda x: x['profit_percent'])
                    print(f"\nBest opportunity: {best_opp['pair']} | "
                          f"Buy @ {best_opp['buy_exchange']} ({best_opp['buy_price']}), "
                          f"Sell @ {best_opp['sell_exchange']} ({best_opp['sell_price']}) | "
                          f"Profit: {best_opp['profit_percent']:.2f}%")
                    
                    profit = self.execute_trade(best_opp)
                    total_profit += profit
                    print(f"Total profit today: ${total_profit:.2f}")
                    
                    if total_profit >= 50:
                        print("\n🎉 DAILY $50 TARGET REACHED! 🎉")
                        self.running = False
                else:
                    print("No profitable opportunities found. Waiting...")
                
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.running = False
                print("\nBot stopped by user")
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                time.sleep(30)

if __name__ == "__main__":
    bot = ArbitrageBot()
    print("Starting crypto arbitrage bot...")
    bot.run()