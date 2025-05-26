"""
Etherscan Integration for Rehoboam

This module provides comprehensive Ethereum blockchain analysis capabilities using the Etherscan API.
It's designed to give Rehoboam advanced blockchain intelligence for trading and market analysis.

Features:
- Transaction analysis and pattern detection
- Wallet behavior analysis
- Contract interaction monitoring
- Gas optimization insights
- MEV detection
- Whale activity monitoring
"""

import os
import requests
import time
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger("EtherscanIntegration")

# User's MetaMask wallet address for focused analysis
USER_WALLET_ADDRESS = os.getenv('USER_WALLET_ADDRESS', '0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8')

class EtherscanAnalyzer:
    """
    Advanced Ethereum blockchain analyzer using Etherscan API.
    
    Provides Rehoboam with sophisticated blockchain intelligence capabilities
    including transaction pattern analysis, MEV detection, and market insights.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the Etherscan analyzer."""
        self.api_key = api_key or os.getenv('ETHERSCAN_API_KEY')
        self.base_url = "https://api.etherscan.io/api"
        self.rate_limit_delay = 0.2  # 200ms between requests
        self.last_request_time = 0
        
        if not self.api_key:
            logger.warning("No Etherscan API key provided. Some features may be limited.")
    
    def _rate_limit(self):
        """Implement rate limiting for API requests."""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Etherscan API with rate limiting."""
        if not self.api_key:
            logger.error("Etherscan API key not available")
            return {"status": "0", "message": "API key not available", "result": []}
        
        self._rate_limit()
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Etherscan API request failed: {e}")
            return {"status": "0", "message": str(e), "result": []}
    
    def get_account_balance(self, address: str) -> Dict[str, Any]:
        """Get the ETH balance of an address."""
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest'
        }
        
        result = self._make_request(params)
        
        if result['status'] == '1':
            balance_wei = int(result['result'])
            balance_eth = balance_wei / 10**18
            
            return {
                'address': address,
                'balance_wei': balance_wei,
                'balance_eth': balance_eth,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'address': address,
                'error': result.get('message', 'Unknown error'),
                'balance_wei': 0,
                'balance_eth': 0
            }
    
    def get_transaction_history(self, address: str, start_block: int = 0, 
                              end_block: str = 'latest', page: int = 1, 
                              offset: int = 100) -> Dict[str, Any]:
        """Get transaction history for an address with analysis."""
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc'
        }
        
        result = self._make_request(params)
        
        if result['status'] == '1':
            transactions = result['result']
            analysis = self._analyze_transactions(transactions)
            
            return {
                'address': address,
                'transactions': transactions,
                'analysis': analysis,
                'total_transactions': len(transactions)
            }
        else:
            return {
                'address': address,
                'error': result.get('message', 'Unknown error'),
                'transactions': [],
                'analysis': {},
                'total_transactions': 0
            }
    
    def analyze_wallet_behavior(self, address: str, transaction_limit: int = 200) -> Dict[str, Any]:
        """Comprehensive wallet behavior analysis."""
        # Get transaction history
        tx_data = self.get_transaction_history(address, offset=transaction_limit)
        
        if 'error' in tx_data:
            return tx_data
        
        transactions = tx_data['transactions']
        
        # Perform advanced analysis
        patterns = self._detect_patterns(transactions)
        risk_assessment = self._assess_risk(transactions, patterns)
        trading_behavior = self._analyze_trading_behavior(transactions)
        
        return {
            'address': address,
            'analysis_timestamp': datetime.now().isoformat(),
            'transaction_count': len(transactions),
            'patterns': patterns,
            'risk_assessment': risk_assessment,
            'trading_behavior': trading_behavior,
            'summary': self._generate_summary(transactions, patterns, risk_assessment)
        }
    
    def detect_mev_activity(self, address: str) -> Dict[str, Any]:
        """Detect potential MEV (Maximal Extractable Value) activity."""
        tx_data = self.get_transaction_history(address, offset=500)
        
        if 'error' in tx_data:
            return tx_data
        
        transactions = tx_data['transactions']
        mev_patterns = []
        
        # Look for MEV indicators
        for i in range(len(transactions) - 1):
            tx1 = transactions[i]
            tx2 = transactions[i + 1]
            
            # Check for rapid consecutive transactions
            time_diff = abs(int(tx1['timeStamp']) - int(tx2['timeStamp']))
            
            if time_diff < 30:  # Within 30 seconds
                # Check for value patterns that suggest MEV
                gas_price_1 = int(tx1.get('gasPrice', 0))
                gas_price_2 = int(tx2.get('gasPrice', 0))
                
                pattern = {
                    'type': 'rapid_consecutive_transactions',
                    'tx1_hash': tx1['hash'],
                    'tx2_hash': tx2['hash'],
                    'time_difference_seconds': time_diff,
                    'gas_price_difference': abs(gas_price_1 - gas_price_2),
                    'potential_mev_score': min(100, (60 - time_diff) * 2)
                }
                
                mev_patterns.append(pattern)
        
        # Calculate overall MEV score
        mev_score = min(100, len(mev_patterns) * 15)
        
        return {
            'address': address,
            'mev_patterns': mev_patterns,
            'mev_score': mev_score,
            'analysis_timestamp': datetime.now().isoformat(),
            'interpretation': self._interpret_mev_score(mev_score)
        }
    
    def get_contract_info(self, contract_address: str) -> Dict[str, Any]:
        """Get information about a smart contract."""
        # Get contract ABI
        abi_params = {
            'module': 'contract',
            'action': 'getabi',
            'address': contract_address
        }
        
        abi_result = self._make_request(abi_params)
        
        # Get contract source code
        source_params = {
            'module': 'contract',
            'action': 'getsourcecode',
            'address': contract_address
        }
        
        source_result = self._make_request(source_params)
        
        contract_info = {
            'address': contract_address,
            'timestamp': datetime.now().isoformat()
        }
        
        if abi_result['status'] == '1':
            try:
                contract_info['abi'] = json.loads(abi_result['result'])
                contract_info['has_abi'] = True
            except:
                contract_info['abi'] = None
                contract_info['has_abi'] = False
        else:
            contract_info['abi'] = None
            contract_info['has_abi'] = False
        
        if source_result['status'] == '1' and source_result['result']:
            source_data = source_result['result'][0]
            contract_info.update({
                'contract_name': source_data.get('ContractName', 'Unknown'),
                'compiler_version': source_data.get('CompilerVersion', 'Unknown'),
                'optimization_used': source_data.get('OptimizationUsed', 'Unknown'),
                'source_code': source_data.get('SourceCode', ''),
                'verified': True
            })
        else:
            contract_info.update({
                'contract_name': 'Unknown',
                'verified': False
            })
        
        return contract_info
    
    def _analyze_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze transaction patterns."""
        if not transactions:
            return {}
        
        total_value = 0
        gas_prices = []
        unique_addresses = set()
        contract_interactions = 0
        
        for tx in transactions:
            # Calculate total value
            value = int(tx.get('value', 0))
            total_value += value
            
            # Collect gas prices
            gas_price = int(tx.get('gasPrice', 0))
            if gas_price > 0:
                gas_prices.append(gas_price)
            
            # Track unique addresses
            unique_addresses.add(tx.get('from', '').lower())
            unique_addresses.add(tx.get('to', '').lower())
            
            # Count contract interactions
            if tx.get('input', '0x') != '0x':
                contract_interactions += 1
        
        return {
            'total_value_wei': total_value,
            'total_value_eth': total_value / 10**18,
            'average_gas_price_gwei': (sum(gas_prices) / len(gas_prices) / 10**9) if gas_prices else 0,
            'unique_addresses': len(unique_addresses),
            'contract_interaction_ratio': contract_interactions / len(transactions) if transactions else 0,
            'transaction_frequency': self._calculate_frequency(transactions)
        }
    
    def _detect_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect various patterns in transaction data."""
        patterns = {
            'time_patterns': self._analyze_time_patterns(transactions),
            'value_patterns': self._analyze_value_patterns(transactions),
            'gas_patterns': self._analyze_gas_patterns(transactions),
            'address_patterns': self._analyze_address_patterns(transactions)
        }
        
        return patterns
    
    def _analyze_time_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in transactions."""
        if not transactions:
            return {}
        
        timestamps = [int(tx['timeStamp']) for tx in transactions]
        timestamps.sort()
        
        # Calculate time intervals
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            min_interval = min(intervals)
            max_interval = max(intervals)
            
            # Detect regular patterns
            regular_intervals = [i for i in intervals if abs(i - avg_interval) < avg_interval * 0.1]
            regularity_score = len(regular_intervals) / len(intervals) * 100
            
            return {
                'average_interval_seconds': avg_interval,
                'min_interval_seconds': min_interval,
                'max_interval_seconds': max_interval,
                'regularity_score': regularity_score,
                'is_automated': regularity_score > 70 and min_interval < 300  # Less than 5 minutes
            }
        
        return {}
    
    def _analyze_value_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze value patterns in transactions."""
        values = [int(tx.get('value', 0)) for tx in transactions if int(tx.get('value', 0)) > 0]
        
        if not values:
            return {}
        
        # Calculate statistics
        total_value = sum(values)
        avg_value = total_value / len(values)
        min_value = min(values)
        max_value = max(values)
        
        # Detect round numbers (potential bot behavior)
        round_values = [v for v in values if v % (10**18) == 0]  # Round ETH amounts
        round_ratio = len(round_values) / len(values)
        
        return {
            'total_value_eth': total_value / 10**18,
            'average_value_eth': avg_value / 10**18,
            'min_value_eth': min_value / 10**18,
            'max_value_eth': max_value / 10**18,
            'round_number_ratio': round_ratio,
            'suggests_automation': round_ratio > 0.5
        }
    
    def _analyze_gas_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze gas usage patterns."""
        gas_prices = [int(tx.get('gasPrice', 0)) for tx in transactions if int(tx.get('gasPrice', 0)) > 0]
        gas_used = [int(tx.get('gasUsed', 0)) for tx in transactions if int(tx.get('gasUsed', 0)) > 0]
        
        patterns = {}
        
        if gas_prices:
            avg_gas_price = sum(gas_prices) / len(gas_prices)
            min_gas_price = min(gas_prices)
            max_gas_price = max(gas_prices)
            
            patterns['gas_price_analysis'] = {
                'average_gwei': avg_gas_price / 10**9,
                'min_gwei': min_gas_price / 10**9,
                'max_gwei': max_gas_price / 10**9,
                'price_variance': (max_gas_price - min_gas_price) / avg_gas_price if avg_gas_price > 0 else 0
            }
        
        if gas_used:
            avg_gas_used = sum(gas_used) / len(gas_used)
            patterns['gas_usage_analysis'] = {
                'average_gas_used': avg_gas_used,
                'total_gas_used': sum(gas_used),
                'efficiency_score': self._calculate_gas_efficiency(gas_used)
            }
        
        return patterns
    
    def _analyze_address_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze address interaction patterns."""
        to_addresses = [tx.get('to', '').lower() for tx in transactions if tx.get('to')]
        from_addresses = [tx.get('from', '').lower() for tx in transactions if tx.get('from')]
        
        # Count address frequencies
        to_freq = {}
        from_freq = {}
        
        for addr in to_addresses:
            to_freq[addr] = to_freq.get(addr, 0) + 1
        
        for addr in from_addresses:
            from_freq[addr] = from_freq.get(addr, 0) + 1
        
        # Find most frequent interactions
        most_frequent_to = sorted(to_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        most_frequent_from = sorted(from_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'unique_to_addresses': len(set(to_addresses)),
            'unique_from_addresses': len(set(from_addresses)),
            'most_frequent_recipients': most_frequent_to,
            'most_frequent_senders': most_frequent_from,
            'address_diversity_score': len(set(to_addresses + from_addresses)) / len(transactions) if transactions else 0
        }
    
    def _assess_risk(self, transactions: List[Dict[str, Any]], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level based on transaction patterns."""
        risk_score = 0
        risk_factors = []
        
        # Check for automation indicators
        time_patterns = patterns.get('time_patterns', {})
        if time_patterns.get('is_automated', False):
            risk_score += 30
            risk_factors.append("Potential automated trading detected")
        
        # Check for round number preference
        value_patterns = patterns.get('value_patterns', {})
        if value_patterns.get('suggests_automation', False):
            risk_score += 20
            risk_factors.append("High round number usage suggests bot activity")
        
        # Check for high-frequency trading
        if time_patterns.get('min_interval_seconds', 0) < 60:
            risk_score += 25
            risk_factors.append("Very high frequency trading detected")
        
        # Check for large value transactions
        if value_patterns.get('max_value_eth', 0) > 1000:
            risk_score += 15
            risk_factors.append("Large value transactions present")
        
        risk_level = "Low"
        if risk_score > 70:
            risk_level = "High"
        elif risk_score > 40:
            risk_level = "Medium"
        
        return {
            'risk_score': min(risk_score, 100),
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }
    
    def _analyze_trading_behavior(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trading behavior patterns."""
        contract_txs = [tx for tx in transactions if tx.get('input', '0x') != '0x']
        
        behavior = {
            'total_transactions': len(transactions),
            'contract_interactions': len(contract_txs),
            'defi_activity_ratio': len(contract_txs) / len(transactions) if transactions else 0
        }
        
        # Classify trading behavior
        if behavior['defi_activity_ratio'] > 0.8:
            behavior['classification'] = "Heavy DeFi User"
        elif behavior['defi_activity_ratio'] > 0.5:
            behavior['classification'] = "Active DeFi User"
        elif behavior['defi_activity_ratio'] > 0.2:
            behavior['classification'] = "Occasional DeFi User"
        else:
            behavior['classification'] = "Simple Transfer User"
        
        return behavior
    
    def _generate_summary(self, transactions: List[Dict[str, Any]], 
                         patterns: Dict[str, Any], risk_assessment: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the analysis."""
        if not transactions:
            return "No transactions found for analysis."
        
        tx_count = len(transactions)
        total_value = patterns.get('value_patterns', {}).get('total_value_eth', 0)
        risk_level = risk_assessment.get('risk_level', 'Unknown')
        
        summary = f"Analyzed {tx_count} transactions with total value of {total_value:.4f} ETH. "
        summary += f"Risk assessment: {risk_level}. "
        
        if patterns.get('time_patterns', {}).get('is_automated', False):
            summary += "Shows signs of automated trading. "
        
        if risk_assessment.get('risk_score', 0) > 50:
            summary += "Exhibits several risk factors requiring attention."
        else:
            summary += "Shows normal trading patterns."
        
        return summary
    
    def _calculate_frequency(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate transaction frequency (transactions per day)."""
        if len(transactions) < 2:
            return 0
        
        timestamps = [int(tx['timeStamp']) for tx in transactions]
        time_span = max(timestamps) - min(timestamps)
        
        if time_span == 0:
            return len(transactions)
        
        days = time_span / (24 * 60 * 60)
        return len(transactions) / days if days > 0 else len(transactions)
    
    def _calculate_gas_efficiency(self, gas_used: List[int]) -> float:
        """Calculate gas efficiency score."""
        if not gas_used:
            return 0
        
        avg_gas = sum(gas_used) / len(gas_used)
        max_gas = max(gas_used)
        min_gas = min(gas_used)
        
        # Efficiency based on consistency and optimization
        variance = (max_gas - min_gas) / avg_gas if avg_gas > 0 else 0
        efficiency = max(0, 100 - variance * 50)
        
        return efficiency
    
    def _interpret_mev_score(self, score: int) -> str:
        """Interpret MEV score."""
        if score > 70:
            return "High probability of MEV extraction activity"
        elif score > 40:
            return "Moderate signs of MEV-related patterns"
        elif score > 20:
            return "Some MEV-like patterns detected"
        else:
            return "No significant MEV activity detected"
