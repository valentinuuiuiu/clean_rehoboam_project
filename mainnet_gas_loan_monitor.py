#!/usr/bin/env python3
"""
Mainnet Gas Loan Arbitrage Monitor
Tracks gas loan repayment and profits to user wallet in real-time
"""

import json
import time
import requests
from web3 import Web3
from datetime import datetime
import os

class MainnetGasLoanMonitor:
    def __init__(self):
        # Your wallet address - where profits go
        self.your_wallet = "0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8"
        
        # Load deployment info if available
        self.contract_address = None
        self.gas_lender = None
        self.gas_loan_amount = 0
        
        if os.path.exists("mainnet_gas_loan_deployment.env"):
            with open("mainnet_gas_loan_deployment.env", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("MAINNET_GAS_LOAN_CONTRACT="):
                        self.contract_address = line.split("=")[1].strip()
                    elif line.startswith("GAS_LENDER_WALLET="):
                        self.gas_lender = line.split("=")[1].strip()
                    elif line.startswith("GAS_LOAN_AMOUNT="):
                        self.gas_loan_amount = int(line.split("=")[1].strip())
        
        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID"))
        
        # Contract ABI (minimal for monitoring)
        self.abi = [
            {
                "inputs": [],
                "name": "getLoanStatus",
                "outputs": [
                    {"type": "uint256", "name": "totalLoan"},
                    {"type": "uint256", "name": "repaid"},
                    {"type": "uint256", "name": "remaining"},
                    {"type": "bool", "name": "fullyRepaid"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getProfitStats",
                "outputs": [
                    {"type": "uint256", "name": "totalGenerated"},
                    {"type": "uint256", "name": "sentToYou"},
                    {"type": "uint256", "name": "usedForGasRepayment"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getBalanceInfo",
                "outputs": [
                    {"type": "uint256", "name": "contractBalance"},
                    {"type": "uint256", "name": "yourWalletBalance"},
                    {"type": "uint256", "name": "nextDistributionToYou"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        if self.contract_address:
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.abi
            )
    
    def get_eth_price(self):
        """Get current ETH price in USD"""
        try:
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
            return response.json()["ethereum"]["usd"]
        except:
            return 3000  # Fallback price
    
    def wei_to_eth(self, wei_amount):
        """Convert wei to ETH"""
        return wei_amount / 1e18
    
    def format_usd(self, eth_amount, eth_price):
        """Format ETH amount as USD"""
        return eth_amount * eth_price
    
    def monitor_live(self):
        """Monitor the contract and your wallet in real-time"""
        if not self.contract_address:
            print("❌ No contract address found. Deploy the contract first.")
            return
        
        print("🚀 MAINNET GAS LOAN ARBITRAGE MONITOR")
        print("=====================================")
        print(f"📍 Contract: {self.contract_address}")
        print(f"💰 Your Wallet: {self.your_wallet}")
        print(f"⛽ Gas Lender: {self.gas_lender}")
        print("=====================================")
        print("")
        
        initial_balance = self.w3.eth.get_balance(self.your_wallet)
        eth_price = self.get_eth_price()
        
        print(f"💰 Your Initial Balance: {self.wei_to_eth(initial_balance):.6f} ETH (${self.format_usd(self.wei_to_eth(initial_balance), eth_price):.2f})")
        print("")
        
        while True:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_balance = self.w3.eth.get_balance(self.your_wallet)
                eth_price = self.get_eth_price()
                
                # Get contract status
                loan_status = self.contract.functions.getLoanStatus().call()
                profit_stats = self.contract.functions.getProfitStats().call()
                balance_info = self.contract.functions.getBalanceInfo().call()
                
                total_loan, repaid, remaining, fully_repaid = loan_status
                total_generated, sent_to_you, gas_repayment = profit_stats
                contract_balance, your_balance, next_distribution = balance_info
                
                # Calculate profit since start
                profit_earned = current_balance - initial_balance
                
                print(f"\n⏰ {timestamp} | ETH: ${eth_price:.2f}")
                print("=" * 60)
                
                # Gas loan status
                print("⛽ GAS LOAN STATUS:")
                if fully_repaid:
                    print("   ✅ FULLY REPAID - All future profits go 100% to you!")
                else:
                    print(f"   📊 Total Loan: {self.wei_to_eth(total_loan):.6f} ETH")
                    print(f"   ✅ Repaid: {self.wei_to_eth(repaid):.6f} ETH ({(repaid/total_loan*100):.1f}%)")
                    print(f"   ⏳ Remaining: {self.wei_to_eth(remaining):.6f} ETH")
                
                print("")
                
                # Profit statistics
                print("📈 PROFIT STATISTICS:")
                print(f"   💰 Total Generated: {self.wei_to_eth(total_generated):.6f} ETH (${self.format_usd(self.wei_to_eth(total_generated), eth_price):.2f})")
                print(f"   🎯 Sent to You: {self.wei_to_eth(sent_to_you):.6f} ETH (${self.format_usd(self.wei_to_eth(sent_to_you), eth_price):.2f})")
                print(f"   ⛽ Used for Gas: {self.wei_to_eth(gas_repayment):.6f} ETH (${self.format_usd(self.wei_to_eth(gas_repayment), eth_price):.2f})")
                
                print("")
                
                # Your wallet status
                print("💳 YOUR WALLET:")
                print(f"   🏦 Current Balance: {self.wei_to_eth(current_balance):.6f} ETH (${self.format_usd(self.wei_to_eth(current_balance), eth_price):.2f})")
                if profit_earned > 0:
                    print(f"   📈 Profit Earned: +{self.wei_to_eth(profit_earned):.6f} ETH (${self.format_usd(self.wei_to_eth(profit_earned), eth_price):.2f})")
                elif profit_earned < 0:
                    print(f"   📉 Net Change: {self.wei_to_eth(profit_earned):.6f} ETH (${self.format_usd(self.wei_to_eth(profit_earned), eth_price):.2f})")
                
                if next_distribution > 0:
                    print(f"   🎁 Next Distribution: {self.wei_to_eth(next_distribution):.6f} ETH (${self.format_usd(self.wei_to_eth(next_distribution), eth_price):.2f})")
                
                print("")
                
                # Contract status
                print("🤖 CONTRACT STATUS:")
                print(f"   💰 Contract Balance: {self.wei_to_eth(contract_balance):.6f} ETH")
                
                if contract_balance > 0:
                    print("   🚀 PROFITS READY FOR DISTRIBUTION!")
                    
                # Etherscan links
                print("")
                print("🔗 LINKS:")
                print(f"   📊 Contract: https://etherscan.io/address/{self.contract_address}")
                print(f"   💰 Your Wallet: https://etherscan.io/address/{self.your_wallet}")
                
                time.sleep(30)  # Update every 30 seconds
                
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(10)
    
    def quick_status(self):
        """Get a quick status update"""
        if not self.contract_address:
            print("❌ No contract deployed yet")
            return
        
        try:
            balance = self.w3.eth.get_balance(self.your_wallet)
            loan_status = self.contract.functions.getLoanStatus().call()
            profit_stats = self.contract.functions.getProfitStats().call()
            
            total_loan, repaid, remaining, fully_repaid = loan_status
            total_generated, sent_to_you, gas_repayment = profit_stats
            
            print(f"💰 Your Balance: {self.wei_to_eth(balance):.6f} ETH")
            print(f"📈 Total Profits: {self.wei_to_eth(total_generated):.6f} ETH")
            print(f"🎯 Sent to You: {self.wei_to_eth(sent_to_you):.6f} ETH")
            
            if fully_repaid:
                print("✅ Gas loan fully repaid - 100% profits to you!")
            else:
                print(f"⏳ Gas loan: {(repaid/total_loan*100):.1f}% repaid")
                
        except Exception as e:
            print(f"❌ Error getting status: {e}")

if __name__ == "__main__":
    import sys
    
    monitor = MainnetGasLoanMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        monitor.quick_status()
    else:
        monitor.monitor_live()
