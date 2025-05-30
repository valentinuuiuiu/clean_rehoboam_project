#!/usr/bin/env python3
import requests
import json

def check_real_arbitrage():
    print("🔍 CHECKING REAL ARBITRAGE OPPORTUNITIES RIGHT NOW...")
    print("=" * 50)
    
    try:
        # Get ETH price from different sources
        coingecko = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd', timeout=5)
        coinbase = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=ETH', timeout=5)
        
        if coingecko.status_code == 200:
            cg_price = float(coingecko.json()['ethereum']['usd'])
            print(f"CoinGecko ETH: ${cg_price:,.2f}")
        else:
            cg_price = None
            print("❌ CoinGecko API failed")
            
        if coinbase.status_code == 200:
            cb_price = float(coinbase.json()['data']['rates']['USD'])
            print(f"Coinbase ETH:  ${cb_price:,.2f}")
        else:
            cb_price = None
            print("❌ Coinbase API failed")
            
        if cg_price and cb_price:
            diff = abs(cg_price - cb_price)
            avg = (cg_price + cb_price) / 2
            spread = (diff / avg) * 100
            
            print(f"\n📊 ANALYSIS:")
            print(f"Price Difference: ${diff:.2f}")
            print(f"Spread: {spread:.4f}%")
            
            if spread > 0.05:  # 0.05% threshold
                profit_1k = 1000 * (spread / 100) - 20   # $20 gas cost
                profit_10k = 10000 * (spread / 100) - 50  # $50 gas cost
                
                print(f"\n💰 PROFIT POTENTIAL:")
                print(f"$1K trade profit:  ${profit_1k:.2f}")
                print(f"$10K trade profit: ${profit_10k:.2f}")
                
                if profit_1k > 0:
                    print(f"✅ PROFITABLE OPPORTUNITY EXISTS!")
                    return True
                else:
                    print(f"❌ Spread too small for profit after gas")
            else:
                print(f"📊 Spread too small for arbitrage")
                
    except Exception as e:
        print(f"❌ Error checking prices: {e}")
        
    print(f"\n🤖 REALITY: Most profitable arbitrage happens in:")
    print(f"- Smaller altcoins (higher spreads)")
    print(f"- During high volatility periods") 
    print(f"- Cross-chain opportunities")
    print(f"- Flash crashes/pumps")
    
    return False

if __name__ == "__main__":
    check_real_arbitrage()
