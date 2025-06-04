"""Web3 Wallet Management Utilities"""
from web3 import Web3
from eth_account import Account
import logging
import time
import asyncio
import websockets
import json
from typing import Optional, Dict, List, Callable, AsyncGenerator, Union

logger = logging.getLogger(__name__)

# Standard ERC-20 ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

class TokenService:
    """Handle token-related operations"""
    def __init__(self, w3: Web3):
        self.w3 = w3
        
    def get_token_balance(self, wallet_address: str, token_address: str) -> Dict:
        """Get balance of specific ERC-20 token"""
        contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        balance = contract.functions.balanceOf(
            self.w3.to_checksum_address(wallet_address)
        ).call()
        decimals = contract.functions.decimals().call()
        symbol = contract.functions.symbol().call()
        
        return {
            'balance': balance,
            'decimals': decimals,
            'symbol': symbol,
            'value': balance / (10 ** decimals),
            'token_address': token_address,
            'wallet_address': wallet_address
        }

class WalletManager:
    def __init__(self, rpc_url: str, max_retries: int = 3):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.accounts = {}
        self.max_retries = max_retries
        
    def create_wallet(self) -> Dict[str, str]:
        """Generate a new wallet"""
        account = Account.create()
        self.accounts[account.address] = account.key.hex()
        return {
            'address': account.address,
            'private_key': account.key.hex()  # Warning: For demo only
        }
        
    def get_balance(self, address: str) -> Optional[float]:
        """Get balance in ETH with retry logic"""
        for attempt in range(self.max_retries):
            try:
                balance_wei = self.w3.eth.get_balance(address)
                return self.w3.from_wei(balance_wei, 'ether')
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Balance check failed after {self.max_retries} attempts: {str(e)}")
                    return None
                time.sleep(1)
                
    def get_transactions(self, address: str) -> List[Dict]:
        """Get recent transactions (empty for new wallets)"""
        # Placeholder - would require Etherscan API or full node
        logger.warning("Transaction history requires Etherscan API or full node")
        return []
        
    def validate_address(self, address: str) -> bool:
        """Check if address is valid"""
        return self.w3.is_address(address)

    def sign_transaction(self, private_key: str, tx_params: Dict) -> Dict:
        """Sign a transaction securely"""
        account = self.w3.eth.account.from_key(private_key)
        signed_tx = self.w3.eth.account.sign_transaction(tx_params, private_key)
        return {
            'rawTransaction': signed_tx.rawTransaction.hex(),
            'hash': signed_tx.hash.hex(),
            'sender': account.address
        }

    def send_transaction(self, signed_tx: Dict) -> str:
        """Send a signed transaction"""
        tx_hash = self.w3.eth.send_raw_transaction(bytes.fromhex(signed_tx['rawTransaction']))
        return tx_hash.hex()

class TransactionMonitor:
    """Enhanced real-time transaction monitoring with address filtering"""
    def __init__(self, ws_url: str, rpc_url: str):
        self.ws_url = ws_url
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
    async def watch_transactions(self, callback: Callable[[Dict], None], address_filter: str = None) -> None:
        """Monitor transactions with optional address filtering"""
        async with websockets.connect(self.ws_url) as ws:
            await ws.send('{"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":["newPendingTransactions"]}')
            subscription_response = await ws.recv()
            logger.info(f"Subscription established: {subscription_response}")
            
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=60)
                    tx_data = json.loads(message)
                    tx_hash = tx_data.get('params', {}).get('result')
                    
                    if tx_hash:
                        # Get full transaction details
                        tx = self.w3.eth.get_transaction(tx_hash)
                        if tx:
                            # Apply address filter if provided
                            if not address_filter or (
                                tx['from'].lower() == address_filter.lower() or 
                                (tx.get('to') and tx['to'].lower() == address_filter.lower())
                            ):
                                decoded_tx = {
                                    'hash': tx_hash,
                                    'from': tx['from'],
                                    'to': tx.get('to'),
                                    'value': self.w3.from_wei(tx['value'], 'ether'),
                                    'gas': tx['gas'],
                                    'gasPrice': self.w3.from_wei(tx['gasPrice'], 'gwei'),
                                    'input': tx['input'][:100] + '...' if tx['input'] else None
                                }
                                callback(decoded_tx)
                except asyncio.TimeoutError:
                    logger.warning("WebSocket timeout, reconnecting...")
                    break
                except Exception as e:
                    logger.error(f"Error processing transaction: {str(e)}")
                    continue

# Example usage:
# manager = WalletManager('https://cloudflare-eth.com')
# wallet = manager.create_wallet()
# print(wallet['address'])