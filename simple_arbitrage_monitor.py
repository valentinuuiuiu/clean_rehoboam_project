#!/usr/bin/env python3
"""
Simplified Arbitrage Monitor for Backend Integration
"""

import os
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleArbitrageMonitor:
    def __init__(self):
        self.backend_url = f"http://localhost:{os.getenv('API_PORT', 5002)}"
        self.sepolia_contract = os.getenv('SEPOLIA_ARBITRAGE_CONTRACT')
        self.wallet_address = os.getenv('USER_WALLET_ADDRESS')
        
        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider(f"https://eth-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}"))
        
        print(f"🔧 Backend URL: {self.backend_url}")
        print(f"📜 Sepolia Contract: {self.sepolia_contract}")
        print(f"💰 Wallet: {self.wallet_address}")
        
    def check_backend_status(self):
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is running")
                return True
            else:
                print(f"❌ Backend returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend not accessible: {e}")
            return False
            
    def check_wallet_balance(self):
        """Check wallet balance"""
        try:
            balance_wei = self.w3.eth.get_balance(self.wallet_address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            print(f"💰 Wallet Balance: {balance_eth:.6f} SepoliaETH")
            return balance_eth
        except Exception as e:
            print(f"❌ Error checking balance: {e}")
            return 0
            
    def check_contract_balance(self):
        """Check contract balance"""
        try:
            balance_wei = self.w3.eth.get_balance(self.sepolia_contract)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            print(f"📜 Contract Balance: {balance_eth:.6f} ETH")
            return balance_eth
        except Exception as e:
            print(f"❌ Error checking contract: {e}")
            return 0
            
    def send_arbitrage_request(self, opportunity):
        """Send arbitrage opportunity to backend"""
        try:
            payload = {
                "token_pair": opportunity["pair"],
                "buy_price": opportunity["buy_price"],
                "sell_price": opportunity["sell_price"],
                "profit_potential": opportunity["profit"],
                "network": "sepolia",
                "contract": self.sepolia_contract
            }
            
            response = requests.post(
                f"{self.backend_url}/api/arbitrage/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Arbitrage request sent: {result}")
                return result
            else:
                print(f"❌ Backend error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error sending request: {e}")
            return None
            
    def mock_arbitrage_opportunities(self):
        """Generate mock arbitrage opportunities for testing"""
        return [
            {
                "pair": "WETH/USDC",
                "buy_price": 2000.50,
                "sell_price": 2002.75,
                "profit": 2.25,
                "confidence": 0.85
            },
            {
                "pair": "DAI/USDT", 
                "buy_price": 0.998,
                "sell_price": 1.001,
                "profit": 0.003,
                "confidence": 0.70
            }
        ]
        
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        print("\n🔍 === ARBITRAGE MONITORING CYCLE ===")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check system status
        backend_ok = self.check_backend_status()
        wallet_balance = self.check_wallet_balance()
        contract_balance = self.check_contract_balance()
        
        # Find opportunities
        opportunities = self.mock_arbitrage_opportunities()
        
        for i, opp in enumerate(opportunities, 1):
            print(f"\n💡 Opportunity #{i}:")
            print(f"   Pair: {opp['pair']}")
            print(f"   Buy: ${opp['buy_price']}")
            print(f"   Sell: ${opp['sell_price']}")
            print(f"   Profit: ${opp['profit']}")
            print(f"   Confidence: {opp['confidence']:.1%}")
            
            # Only send to backend if it's running and profitable
            if backend_ok and opp['profit'] > 1.0 and opp['confidence'] > 0.8:
                print(f"🚀 Sending high-confidence opportunity to backend...")
                result = self.send_arbitrage_request(opp)
                if result:
                    print(f"✅ Backend response: {result}")
                    
        print("\n" + "="*50)
        
    def start_monitoring(self, interval_seconds=30):
        """Start continuous monitoring"""
        print("🔥 REHOBOAM ARBITRAGE MONITOR STARTING 🔥")
        print(f"Monitoring every {interval_seconds} seconds...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")

def main():
    monitor = SimpleArbitrageMonitor()
    
    print("🔧 System Check:")
    monitor.check_backend_status()
    monitor.check_wallet_balance()
    monitor.check_contract_balance()
    
    print("\n" + "="*50)
    choice = input("Start continuous monitoring? (y/n): ").lower()
    
    if choice == 'y':
        monitor.start_monitoring(interval_seconds=30)
    else:
        print("Running single cycle...")
        monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()
