"""Core Web3 integration service."""
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Web3Service:
    def __init__(self):
        self.providers = {}
        self.wallets = {}
        
    def add_provider(self, chain_id: int, rpc_url: str):
        """Add a blockchain provider."""
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if 'poa' in rpc_url.lower():
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.providers[chain_id] = w3
        logger.info(f"Added provider for chain {chain_id}")
        
    def create_wallet(self) -> Dict[str, str]:
        """Generate a new wallet."""
        account = Account.create()
        self.wallets[account.address] = account.key.hex()
        return {
            'address': account.address,
            'private_key': account.key.hex()
        }
        
    def get_balance(self, address: str, chain_id: int) -> float:
        """Get native token balance."""
        if chain_id not in self.providers:
            raise ValueError(f"Provider for chain {chain_id} not configured")
            
        w3 = self.providers[chain_id]
        balance_wei = w3.eth.get_balance(address)
        return w3.from_wei(balance_wei, 'ether')
        
    def send_transaction(
        self,
        chain_id: int,
        from_address: str,
        to_address: str,
        value: float,
        private_key: str,
        gas_limit: int = 21000,
        max_priority_fee: Optional[float] = None,
        max_fee: Optional[float] = None
    ) -> str:
        """Send a transaction."""
        if chain_id not in self.providers:
            raise ValueError(f"Provider for chain {chain_id} not configured")
            
        w3 = self.providers[chain_id]
        
        # Build transaction
        tx = {
            'chainId': chain_id,
            'from': from_address,
            'to': to_address,
            'value': w3.to_wei(value, 'ether'),
            'gas': gas_limit,
            'nonce': w3.eth.get_transaction_count(from_address)
        }
        
        # Set gas fees
        if max_priority_fee and max_fee:
            tx['maxPriorityFeePerGas'] = w3.to_wei(max_priority_fee, 'gwei')
            tx['maxFeePerGas'] = w3.to_wei(max_fee, 'gwei')
        else:
            tx['gasPrice'] = w3.eth.gas_price
        
        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()

# Initialize global instance
web3_service = Web3Service()