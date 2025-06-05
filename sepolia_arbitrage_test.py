#!/usr/bin/env python3
"""
REAL Arbitrage Testing on Sepolia Testnet
Contract: 0x9Dc01D22faB8d46331cc833d92Fa1da4eEcCb36d
"""

import os
import time
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SEPOLIA_RPC = f"https://eth-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}"
PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('USER_WALLET_ADDRESS')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')

# Deployed contract address
ARBITRAGE_CONTRACT = "0x9Dc01D22faB8d46331cc833d92Fa1da4eEcCb36d"

# Sepolia testnet token addresses (common test tokens)
SEPOLIA_TOKENS = {
    "WETH": "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14",  # Sepolia WETH
    "USDC": "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8",  # Mock USDC on Sepolia
    "DAI": "0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6",   # Mock DAI on Sepolia
    "USDT": "0x7169D38820dfd117C3FA1f22a697dBA58d90BA06", # Mock USDT on Sepolia
}

# Uniswap V2 Router on Sepolia
UNISWAP_V2_ROUTER = "0xC532a74256D3Db42D0Bf7a0400fEFDbad7694008"

print("🔥 REHOBOAM FLASH ARBITRAGE - SEPOLIA TESTNET 🔥")
print("=" * 60)
print(f"Contract Address: {ARBITRAGE_CONTRACT}")
print(f"Your Wallet: {WALLET_ADDRESS}")
print(f"Network: Sepolia Testnet")
print("=" * 60)

class SepoliaArbitrageBot:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        
        # Contract ABI (updated with the actual function)
        self.contract_abi = [
            {
                "inputs": [
                    {
                        "components": [
                            {"name": "tokenToBorrow", "type": "address"},
                            {"name": "amountToBorrow", "type": "uint256"},
                            {"name": "tokenToArbitrage", "type": "address"},
                            {"name": "dexA", "type": "address"},
                            {"name": "dexB", "type": "address"},
                            {"name": "minProfit", "type": "uint256"}
                        ],
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "executeArbitrage",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "token", "type": "address"},
                    {"indexed": False, "name": "amount", "type": "uint256"},
                    {"indexed": False, "name": "profit", "type": "uint256"},
                    {"indexed": True, "name": "profitReceiver", "type": "address"}
                ],
                "name": "ArbitrageExecuted",
                "type": "event"
            }
        ]
        
        self.contract = self.w3.eth.contract(
            address=ARBITRAGE_CONTRACT,
            abi=self.contract_abi
        )
        
    def check_balance(self):
        """Check wallet balance"""
        balance_wei = self.w3.eth.get_balance(WALLET_ADDRESS)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        print(f"💰 Wallet Balance: {balance_eth:.6f} SepoliaETH")
        return balance_eth
        
    def check_contract_profits(self):
        """Check contract owner and basic info"""
        try:
            # Check contract balance
            contract_balance = self.w3.eth.get_balance(ARBITRAGE_CONTRACT)
            balance_eth = self.w3.from_wei(contract_balance, 'ether')
            print(f"📈 Contract Balance: {balance_eth:.6f} ETH")
            return balance_eth
        except Exception as e:
            print(f"❌ Error checking contract: {e}")
            return 0
            
    def execute_test_arbitrage(self):
        """Execute a real arbitrage test using the flash loan contract"""
        try:
            print("\n🚀 Executing Real Flash Arbitrage...")
            
            # Arbitrage parameters - using Sepolia testnet addresses
            arbitrage_params = {
                'tokenToBorrow': SEPOLIA_TOKENS["WETH"],      # Borrow WETH
                'amountToBorrow': self.w3.to_wei(0.01, 'ether'),  # 0.01 WETH
                'tokenToArbitrage': SEPOLIA_TOKENS["USDC"],   # Arbitrage USDC
                'dexA': UNISWAP_V2_ROUTER,                   # Buy from Uniswap
                'dexB': UNISWAP_V2_ROUTER,                   # Sell to Uniswap (same for test)
                'minProfit': self.w3.to_wei(0.001, 'ether')  # Min 0.001 ETH profit
            }
            
            print(f"📝 Borrowing: {self.w3.from_wei(arbitrage_params['amountToBorrow'], 'ether')} WETH")
            print(f"💰 Min Profit: {self.w3.from_wei(arbitrage_params['minProfit'], 'ether')} ETH")
            
            # Build transaction
            tx = self.contract.functions.executeArbitrage(
                arbitrage_params
            ).build_transaction({
                'from': self.account.address,
                'gas': 1000000,  # Higher gas limit for flash loan
                'gasPrice': self.w3.to_wei(10, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': 11155111  # Sepolia chain ID
            })
            
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            print(f"📝 Transaction sent: {tx_hash.hex()}")
            print(f"🔍 Etherscan: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
            
            # Wait for confirmation
            print("⏳ Waiting for confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                print(f"✅ FLASH ARBITRAGE EXECUTED SUCCESSFULLY!")
                print(f"⛽ Gas Used: {receipt.gasUsed:,}")
                
                # Check for arbitrage events
                events = self.contract.events.ArbitrageExecuted().process_receipt(receipt)
                if events:
                    for event in events:
                        profit = self.w3.from_wei(event['args']['profit'], 'ether')
                        print(f"� Profit Generated: {profit} ETH")
                        print(f"🎯 Sent to: {event['args']['profitReceiver']}")
                else:
                    print("ℹ️  No ArbitrageExecuted events found (might be expected for test)")
                
                return True
            else:
                print(f"❌ Transaction failed!")
                print(f"🔍 Transaction Hash: {tx_hash.hex()}")
                print(f"⛽ Gas Used: {receipt.gasUsed:,}")
                print(f"📊 Block Number: {receipt.blockNumber}")
                print(f"❗ This might be due to insufficient liquidity on Sepolia testnet")
                return False
                
        except Exception as e:
            print(f"❌ Error executing arbitrage: {e}")
            return False
            
    def find_arbitrage_opportunities(self):
        """Mock function to find arbitrage opportunities"""
        print("\n🔍 Scanning for arbitrage opportunities...")
        
        # This is a simplified mock - in reality you'd check DEX prices
        opportunities = [
            {
                "token_pair": "WETH/USDC",
                "buy_price": 2000.50,
                "sell_price": 2002.00,
                "profit_potential": 1.50,
                "confidence": "HIGH"
            },
            {
                "token_pair": "DAI/USDT",
                "buy_price": 0.998,
                "sell_price": 1.001,
                "profit_potential": 0.003,
                "confidence": "MEDIUM"
            }
        ]
        
        for i, opp in enumerate(opportunities, 1):
            print(f"💡 Opportunity #{i}:")
            print(f"   Pair: {opp['token_pair']}")
            print(f"   Buy: ${opp['buy_price']}")
            print(f"   Sell: ${opp['sell_price']}")
            print(f"   Potential Profit: ${opp['profit_potential']}")
            print(f"   Confidence: {opp['confidence']}")
            print()
            
        return opportunities

def main():
    bot = SepoliaArbitrageBot()
    
    print("\n🔧 SYSTEM STATUS CHECK")
    print("-" * 30)
    
    # Check connection
    if bot.w3.is_connected():
        print("✅ Connected to Sepolia")
    else:
        print("❌ Connection failed")
        return
        
    # Check balance
    balance = bot.check_balance()
    if balance < 0.01:
        print("⚠️  Low balance! Get more Sepolia ETH from faucet:")
        print("   https://sepoliafaucet.com/")
        print("   https://faucet.sepolia.dev/")
        
    # Check contract profits
    bot.check_contract_profits()
    
    # Find opportunities
    opportunities = bot.find_arbitrage_opportunities()
    
    # Execute test arbitrage
    print("\n" + "=" * 60)
    user_input = input("🚀 Execute test arbitrage? (y/n): ").lower()
    
    if user_input == 'y':
        success = bot.execute_test_arbitrage()
        if success:
            print("\n🎉 ARBITRAGE TEST COMPLETED!")
            time.sleep(3)
            bot.check_contract_profits()
            bot.check_balance()
        else:
            print("\n💥 ARBITRAGE TEST FAILED!")
    else:
        print("👋 Test cancelled by user")
        
    print("\n🔥 REHOBOAM ARBITRAGE BOT - READY FOR MAINNET! 🔥")

if __name__ == "__main__":
    main()
