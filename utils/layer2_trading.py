"""
Layer 2 Trading Utilities - Enhanced trading capabilities across Layer 2 networks.
"""
import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from decimal import Decimal
from web3 import Web3
from web3.exceptions import ContractLogicError

from utils.network_config import network_config
from utils.web_data import WebDataFetcher
from utils.logging_config import setup_logging

logger = setup_logging()

class Layer2TradingException(Exception):
    """Custom exception for layer 2 trading errors."""
    pass

class Layer2GasEstimator:
    """Gas price estimator for Layer 2 networks with enhanced precision."""
    
    def __init__(self):
        self.web3_connections = {}
        self.gas_price_cache = {}
        self.cache_duration = 60  # 60 seconds
        self.setup_connections()
        
    def setup_connections(self):
        """Setup Web3 connections for supported Layer 2 networks."""
        try:
            # Get all Layer 2 networks
            l2_networks = network_config.get_layer2_networks()
            
            # Initialize connection for each network
            for network in l2_networks:
                network_id = next((k for k, v in network_config.networks.items() if v == network), None)
                if not network_id:
                    continue
                    
                rpc_url = network.get('rpc_url')
                if not rpc_url:
                    logger.warning(f"No RPC URL found for {network_id}")
                    continue
                    
                try:
                    web3 = Web3(Web3.HTTPProvider(rpc_url))
                    if web3.is_connected():
                        self.web3_connections[network_id] = web3
                        logger.info(f"Connected to {network_id} at {rpc_url}")
                    else:
                        logger.warning(f"Failed to connect to {network_id} at {rpc_url}")
                except Exception as e:
                    logger.error(f"Error connecting to {network_id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error in setup_connections: {str(e)}")
            
    def get_gas_price(self, network_id: str) -> Dict[str, Any]:
        """
        Get current gas price for a Layer 2 network with advanced priority fee calculation.
        
        Returns:
            Dict with gas price info:
            {
                'base_fee': float,  # Base fee in gwei
                'priority_fee': float,  # Priority fee in gwei
                'max_fee': float,  # Recommended max fee in gwei
                'gas_price': float,  # Legacy gas price in gwei
                'usd_cost': float,  # Estimated cost in USD for standard transaction
                'updated_at': int,  # Timestamp when this data was fetched
            }
        """
        # Check cache first
        current_time = time.time()
        if network_id in self.gas_price_cache:
            cache_entry = self.gas_price_cache[network_id]
            if current_time - cache_entry['updated_at'] < self.cache_duration:
                return cache_entry
                
        # Default response
        result = {
            'base_fee': 0.0,
            'priority_fee': 0.0,
            'max_fee': 0.0,
            'gas_price': 0.0,
            'usd_cost': 0.0,
            'updated_at': current_time
        }
        
        try:
            # Get the Web3 connection
            web3 = self.web3_connections.get(network_id)
            if not web3:
                logger.warning(f"No Web3 connection for {network_id}")
                return result
                
            # Get network info
            network_info = network_config.get_network(network_id)
            
            # For EIP-1559 compatible networks
            try:
                # Get latest block to extract fee data
                latest_block = web3.eth.get_block('latest')
                
                if hasattr(latest_block, 'baseFeePerGas'):
                    # Convert Wei to Gwei
                    base_fee_gwei = web3.from_wei(latest_block.baseFeePerGas, 'gwei')
                    
                    # Get max priority fee
                    priority_fee_gwei = 1.0  # Default priority fee
                    try:
                        priority_fee_wei = web3.eth.max_priority_fee
                        priority_fee_gwei = web3.from_wei(priority_fee_wei, 'gwei')
                    except (AttributeError, ContractLogicError):
                        # Estimate based on network
                        if network_id == 'arbitrum':
                            priority_fee_gwei = 0.1
                        elif network_id == 'optimism':
                            priority_fee_gwei = 0.5
                        elif network_id == 'polygon':
                            priority_fee_gwei = 30.0
                            
                    # Calculate max fee (base fee + priority fee with buffer)
                    buffer_multiplier = 1.2
                    max_fee_gwei = (base_fee_gwei * buffer_multiplier) + priority_fee_gwei
                    
                    result.update({
                        'base_fee': float(base_fee_gwei),
                        'priority_fee': float(priority_fee_gwei),
                        'max_fee': float(max_fee_gwei)
                    })
                    
            except Exception as e:
                logger.warning(f"Error getting EIP-1559 fees for {network_id}: {str(e)}")
            
            # Get legacy gas price as fallback
            try:
                gas_price_wei = web3.eth.gas_price
                gas_price_gwei = web3.from_wei(gas_price_wei, 'gwei')
                result['gas_price'] = float(gas_price_gwei)
                
                # Use legacy price as max fee if EIP-1559 failed
                if result['max_fee'] == 0:
                    result['max_fee'] = float(gas_price_gwei)
                    
            except Exception as e:
                logger.warning(f"Error getting gas price for {network_id}: {str(e)}")
                
            # Estimate USD cost for a standard transaction (21000 gas)
            gas_token_price = self._get_gas_token_price(network_info.get('gas_token', 'ETH'))
            gas_units = 100000  # Estimated gas for a standard token transfer
            gas_cost_eth = (result['max_fee'] * gas_units) / 1e9  # gwei to ETH
            result['usd_cost'] = gas_cost_eth * gas_token_price
            
            # Update cache
            self.gas_price_cache[network_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error in get_gas_price for {network_id}: {str(e)}")
            return result
            
    def _get_gas_token_price(self, token: str) -> float:
        """Get the USD price of a gas token."""
        try:
            # Use our existing data fetcher
            web_data = WebDataFetcher()
            return web_data.get_crypto_price(token, verify=False)
        except Exception as e:
            logger.error(f"Error getting {token} price: {str(e)}")
            # Fallback prices
            fallback_prices = {
                'ETH': 3000.0,
                'MATIC': 1.0,
                'AVAX': 30.0
            }
            return fallback_prices.get(token, 1.0)
    
    def compare_gas_prices(self) -> List[Dict[str, Any]]:
        """Compare gas prices across all connected Layer 2 networks."""
        results = []
        
        for network_id, web3 in self.web3_connections.items():
            try:
                gas_data = self.get_gas_price(network_id)
                network_info = network_config.get_network(network_id)
                
                results.append({
                    'network': network_id,
                    'name': network_info.get('name', network_id),
                    'type': network_info.get('type', ''),
                    'rollup_type': network_info.get('rollup_type', ''),
                    'gas_token': network_info.get('gas_token', 'ETH'),
                    'max_fee_gwei': gas_data['max_fee'],
                    'base_fee_gwei': gas_data['base_fee'],
                    'priority_fee_gwei': gas_data['priority_fee'],
                    'usd_cost': gas_data['usd_cost'],
                    'updated_at': gas_data['updated_at']
                })
                
            except Exception as e:
                logger.error(f"Error comparing gas price for {network_id}: {str(e)}")
                
        # Sort by USD cost ascending
        return sorted(results, key=lambda x: x['usd_cost'])

class Layer2Arbitrage:
    """Layer 2 arbitrage detection and execution engine."""
    
    def __init__(self):
        self.web_data = WebDataFetcher()
        self.gas_estimator = Layer2GasEstimator()
        self.price_cache = {}
        self.cache_duration = 60  # 60 seconds
        self.min_profit_threshold = 0.01  # 1% minimum profit after fees
        self.token_addresses = {
            'ethereum': {
                'ETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
                'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
                'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
            }
        }
        
    def get_price(self, token: str, network: str) -> float:
        """Get price of token on a specific network with caching."""
        cache_key = f"{token}_{network}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.price_cache:
            cache_entry = self.price_cache[cache_key]
            if current_time - cache_entry['timestamp'] < self.cache_duration:
                return cache_entry['price']
                
        try:
            # Get token price
            # For now, using the same price across networks as a simplification
            price = self.web_data.get_crypto_price(token)
            
            # Update cache
            self.price_cache[cache_key] = {
                'price': price,
                'timestamp': current_time
            }
            
            return price
            
        except Exception as e:
            logger.error(f"Error getting price for {token} on {network}: {str(e)}")
            return 0.0
            
    def analyze_price_differences(self, token: str = 'ETH') -> List[Dict[str, Any]]:
        """
        Analyze price differences across Layer 2 networks for arbitrage opportunities.
        
        Args:
            token: Token symbol to analyze (e.g., 'ETH', 'USDC')
            
        Returns:
            List of arbitrage opportunities sorted by potential profit
        """
        opportunities = []
        networks = []
        network_prices = {}
        
        try:
            # Get all Layer 2 networks
            l2_networks = network_config.get_layer2_networks()
            for network in l2_networks:
                network_id = next((k for k, v in network_config.networks.items() if v == network), None)
                if not network_id:
                    continue
                networks.append(network_id)
                
            # Get current token price on each network
            for network_id in networks:
                price = self.get_price(token, network_id)
                if price > 0:
                    network_prices[network_id] = price
                    
            # Also include Ethereum mainnet for comparison
            price = self.get_price(token, 'ethereum')
            if price > 0:
                network_prices['ethereum'] = price
                
            # Find arbitrage opportunities
            for buy_network, buy_price in network_prices.items():
                for sell_network, sell_price in network_prices.items():
                    if buy_network == sell_network:
                        continue
                        
                    price_diff = sell_price - buy_price
                    diff_percent = price_diff / buy_price
                    
                    # Estimate gas costs
                    buy_gas = self.gas_estimator.get_gas_price(buy_network)
                    sell_gas = self.gas_estimator.get_gas_price(sell_network)
                    
                    # Estimate bridging costs
                    bridge_cost = network_config.estimate_bridging_costs(
                        from_network=buy_network,
                        to_network=sell_network,
                        amount=1.0  # Assuming 1 token
                    )
                    
                    # Calculate potential profit (excluding slippage for now)
                    estimated_gas_cost = buy_gas['usd_cost'] + sell_gas['usd_cost']
                    bridge_fee = bridge_cost.get('fee_estimate', 0.0) * buy_price
                    total_cost = estimated_gas_cost + bridge_fee
                    
                    # Calculate profit after costs
                    profit_after_costs = price_diff - total_cost
                    profit_percent = profit_after_costs / buy_price
                    
                    # Calculate confidence level
                    confidence_factors = [
                        min(1.0, diff_percent * 10),  # Price difference weight
                        min(1.0, 1.0 / (1.0 + total_cost / price_diff)) if price_diff > 0 else 0,  # Cost efficiency
                        0.8 if 'ethereum' not in [buy_network, sell_network] else 0.6,  # L2-to-L2 preferred
                        0.9 if network_config.get_network(buy_network).get('layer') == network_config.get_network(sell_network).get('layer') else 0.7  # Same layer preferred
                    ]
                    confidence = sum(confidence_factors) / len(confidence_factors)
                    
                    # Only include opportunities with potential profit
                    if profit_percent >= self.min_profit_threshold:
                        opportunities.append({
                            'buy_network': buy_network,
                            'sell_network': sell_network,
                            'token': token,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'price_difference': price_diff,
                            'price_difference_percent': diff_percent * 100,
                            'estimated_gas_cost': estimated_gas_cost,
                            'bridge_fee': bridge_fee,
                            'total_cost': total_cost,
                            'profit_after_costs': profit_after_costs,
                            'profit_percent': profit_percent * 100,
                            'confidence': confidence,
                            'bridge_time': bridge_cost.get('time_estimate', 0),
                            'execution_timing': self._determine_execution_timing(bridge_cost.get('time_estimate', 0))
                        })
            
            # Sort by profit percent (descending)
            return sorted(opportunities, key=lambda x: x['profit_percent'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error analyzing price differences for {token}: {str(e)}")
            return []
            
    def _determine_execution_timing(self, bridge_time: int) -> str:
        """Determine execution timing category based on bridge time."""
        if bridge_time <= 60 * 5:  # 5 minutes or less
            return 'immediate'
        elif bridge_time <= 60 * 60:  # 1 hour or less
            return 'standard'
        else:
            return 'delayed'
            
    def get_arbitrage_strategies(self, tokens: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get arbitrage strategies across multiple tokens and networks.
        
        Args:
            tokens: List of token symbols to analyze. If None, uses default list.
            
        Returns:
            List of arbitrage strategies sorted by potential profit
        """
        if tokens is None:
            tokens = ['ETH', 'USDC', 'USDT', 'DAI', 'WBTC']
            
        strategies = []
        
        for token in tokens:
            try:
                opportunities = self.analyze_price_differences(token)
                
                if not opportunities:
                    continue
                    
                # Group opportunities by token
                best_opportunity = opportunities[0]  # Highest profit opportunity
                
                strategies.append({
                    'symbol': token,
                    'routes': opportunities[:3],  # Top 3 opportunities
                    'estimated_profit': best_opportunity['profit_percent'],
                    'confidence': best_opportunity['confidence'],
                    'execution_timing': best_opportunity['execution_timing']
                })
                
            except Exception as e:
                logger.error(f"Error getting arbitrage strategy for {token}: {str(e)}")
                
        # Sort by estimated profit (descending)
        return sorted(strategies, key=lambda x: x['estimated_profit'], reverse=True)

class Layer2Liquidation:
    """Layer 2 liquidation risk and opportunity analyzer."""
    
    def __init__(self):
        self.web_data = WebDataFetcher()
        self.liquidation_thresholds = {
            'ETH': 0.825,  # 82.5% collateralization needed
            'BTC': 0.85,
            'LINK': 0.80,
            'AAVE': 0.75,
            'SNX': 0.70
        }
        self.collateral_factors = {
            'ETH': 0.85,
            'BTC': 0.80,
            'LINK': 0.75,
            'AAVE': 0.70,
            'SNX': 0.65
        }
        
    def calculate_liquidation_price(self, 
                                    collateral_token: str, 
                                    collateral_amount: float,
                                    debt_token: str,
                                    debt_amount: float) -> Dict[str, Any]:
        """
        Calculate liquidation price for a position.
        
        Args:
            collateral_token: Token used as collateral (e.g., 'ETH')
            collateral_amount: Amount of collateral token
            debt_token: Borrowed token (e.g., 'DAI')
            debt_amount: Amount of borrowed token
            
        Returns:
            Dict with liquidation details
        """
        try:
            # Get current prices
            collateral_price = self.web_data.get_crypto_price(collateral_token)
            debt_price = self.web_data.get_crypto_price(debt_token)
            
            if collateral_price <= 0 or debt_price <= 0:
                raise ValueError("Invalid token prices")
                
            # Get liquidation threshold
            threshold = self.liquidation_thresholds.get(collateral_token, 0.75)
            
            # Calculate current position
            collateral_value = collateral_amount * collateral_price
            debt_value = debt_amount * debt_price
            
            # Calculate liquidation price
            liquidation_price = (debt_value / threshold) / collateral_amount
            
            # Calculate health factor
            health_factor = (collateral_value * threshold) / debt_value if debt_value > 0 else float('inf')
            
            # Calculate liquidation buffer (how far from liquidation)
            price_buffer = collateral_price - liquidation_price
            buffer_percent = (price_buffer / collateral_price) * 100
            
            return {
                'collateral_token': collateral_token,
                'collateral_amount': collateral_amount,
                'debt_token': debt_token,
                'debt_amount': debt_amount,
                'current_collateral_price': collateral_price,
                'current_debt_price': debt_price,
                'liquidation_price': liquidation_price,
                'health_factor': health_factor,
                'price_buffer': price_buffer,
                'buffer_percent': buffer_percent,
                'collateral_value': collateral_value,
                'debt_value': debt_value,
                'safe': health_factor >= 1.0,
                'risk_level': self._calculate_risk_level(health_factor)
            }
            
        except Exception as e:
            logger.error(f"Error calculating liquidation price: {str(e)}")
            raise Layer2TradingException(f"Failed to calculate liquidation price: {str(e)}")
            
    def _calculate_risk_level(self, health_factor: float) -> str:
        """Calculate risk level based on health factor."""
        if health_factor < 1.0:
            return 'liquidated'
        elif health_factor < 1.05:
            return 'critical'
        elif health_factor < 1.1:
            return 'high'
        elif health_factor < 1.25:
            return 'medium'
        elif health_factor < 1.5:
            return 'moderate'
        else:
            return 'low'
            
    def calculate_max_borrowable(self, 
                                collateral_token: str,
                                collateral_amount: float,
                                borrow_token: str,
                                buffer_percent: float = 20.0) -> Dict[str, Any]:
        """
        Calculate maximum borrowable amount.
        
        Args:
            collateral_token: Token used as collateral (e.g., 'ETH')
            collateral_amount: Amount of collateral token
            borrow_token: Token to borrow (e.g., 'DAI')
            buffer_percent: Safety buffer percentage
            
        Returns:
            Dict with borrowing details
        """
        try:
            # Get current prices
            collateral_price = self.web_data.get_crypto_price(collateral_token)
            borrow_price = self.web_data.get_crypto_price(borrow_token)
            
            if collateral_price <= 0 or borrow_price <= 0:
                raise ValueError("Invalid token prices")
                
            # Get collateral factor
            collateral_factor = self.collateral_factors.get(collateral_token, 0.75)
            
            # Apply buffer
            effective_factor = collateral_factor * (1 - buffer_percent / 100)
            
            # Calculate max borrowable value
            collateral_value = collateral_amount * collateral_price
            max_borrow_value = collateral_value * effective_factor
            max_borrow_amount = max_borrow_value / borrow_price
            
            return {
                'collateral_token': collateral_token,
                'collateral_amount': collateral_amount,
                'borrow_token': borrow_token,
                'collateral_price': collateral_price,
                'borrow_price': borrow_price,
                'collateral_value': collateral_value,
                'collateral_factor': collateral_factor,
                'effective_factor': effective_factor,
                'safety_buffer': buffer_percent,
                'max_borrow_value': max_borrow_value,
                'max_borrow_amount': max_borrow_amount,
                'recommended_borrow_amount': max_borrow_amount * 0.9,  # 90% of max for extra safety
                'liquidation_threshold': self.liquidation_thresholds.get(collateral_token, 0.75)
            }
            
        except Exception as e:
            logger.error(f"Error calculating max borrowable: {str(e)}")
            raise Layer2TradingException(f"Failed to calculate max borrowable: {str(e)}")

class Layer2TradingOptimizer:
    """Optimize trading strategies for Layer 2 networks."""
    
    def __init__(self):
        self.gas_estimator = Layer2GasEstimator()
        self.arbitrage = Layer2Arbitrage()
        self.liquidation = Layer2Liquidation()
        
    def recommend_network(self, token: str, transaction_type: str, 
                         amount: float = 1.0) -> Dict[str, Any]:
        """
        Recommend the best network for a specific transaction.
        
        Args:
            token: Token symbol
            transaction_type: Type of transaction ('swap', 'transfer', 'liquidity')
            amount: Transaction amount
            
        Returns:
            Dict with network recommendation
        """
        try:
            # Get gas prices across networks
            gas_prices = self.gas_estimator.compare_gas_prices()
            
            # Filter networks based on token availability
            available_networks = []
            for network_data in gas_prices:
                # For simplicity, assuming all tokens are available on all networks
                available_networks.append(network_data)
                
            if not available_networks:
                return {
                    'success': False,
                    'error': f"No networks found supporting {token}",
                    'recommendation': None
                }
                
            # Calculate weighted scores
            weighted_networks = []
            for network in available_networks:
                # Adjust score based on transaction type
                if transaction_type == 'swap':
                    # For swaps, prioritize low cost 
                    cost_weight = 0.7
                    speed_weight = 0.3
                elif transaction_type == 'transfer':
                    # For transfers, prioritize speed
                    cost_weight = 0.3
                    speed_weight = 0.7
                elif transaction_type == 'liquidity':
                    # For LP, balance cost and speed
                    cost_weight = 0.5
                    speed_weight = 0.5
                else:
                    cost_weight = 0.5
                    speed_weight = 0.5
                    
                # Calculate scores
                # Lower cost is better
                max_cost = max(n['usd_cost'] for n in available_networks) or 1.0
                cost_score = 1.0 - (network['usd_cost'] / max_cost) if max_cost > 0 else 0.5
                
                # Network speed score based on type
                speed_score = 0.5
                network_info = network_config.get_network(network['network'])
                if network_info:
                    speed_rating = network_config._rate_speed(network_info)
                    speed_score = speed_rating / 10.0  # Convert 1-10 to 0-1
                    
                # Calculate weighted score
                weighted_score = (cost_score * cost_weight) + (speed_score * speed_weight)
                
                weighted_networks.append({
                    **network,
                    'cost_score': cost_score,
                    'speed_score': speed_score,
                    'weighted_score': weighted_score
                })
                
            # Sort by weighted score
            sorted_networks = sorted(weighted_networks, key=lambda x: x['weighted_score'], reverse=True)
            
            # Return recommendation
            return {
                'success': True,
                'recommendation': sorted_networks[0]['network'],
                'details': sorted_networks[0],
                'alternatives': sorted_networks[1:3],  # Next 2 best options
                'transaction_type': transaction_type,
                'token': token,
                'amount': amount
            }
            
        except Exception as e:
            logger.error(f"Error recommending network: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recommendation': None
            }
            
    def find_best_cross_network_path(self, from_token: str, to_token: str, 
                                   amount: float) -> Dict[str, Any]:
        """
        Find best path for cross-network token exchange.
        
        Args:
            from_token: Starting token
            to_token: Target token
            amount: Amount to exchange
            
        Returns:
            Dict with optimal path
        """
        try:
            # Map networks supporting each token (simplified for illustration)
            networks_map = {
                'ETH': ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync', 'polygon_zkevm', 'scroll'],
                'USDC': ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync'],
                'USDT': ['ethereum', 'arbitrum', 'optimism', 'polygon'],
                'DAI': ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base'],
                'WBTC': ['ethereum', 'arbitrum', 'optimism', 'polygon']
            }
            
            from_networks = networks_map.get(from_token, [])
            to_networks = networks_map.get(to_token, [])
            
            if not from_networks or not to_networks:
                return {
                    'success': False,
                    'error': f"No networks found supporting {from_token} or {to_token}",
                    'path': None
                }
                
            # Calculate paths and costs
            paths = []
            
            for source_network in from_networks:
                for target_network in to_networks:
                    # Skip if same token and same network (no action needed)
                    if from_token == to_token and source_network == target_network:
                        continue
                        
                    # Calculate bridging costs if networks differ
                    bridging_cost = None
                    if source_network != target_network:
                        bridging_cost = network_config.estimate_bridging_costs(
                            from_network=source_network,
                            to_network=target_network,
                            amount=amount
                        )
                        
                    # Calculate swap costs if tokens differ
                    swap_cost = None
                    if from_token != to_token:
                        # Gas cost for token swap
                        swap_gas = self.gas_estimator.get_gas_price(target_network)
                        swap_cost = {
                            'fee_estimate': swap_gas['usd_cost'] / amount,
                            'time_estimate': 60  # 1 minute estimate for swap
                        }
                        
                    # Calculate total cost and time
                    total_fee = 0
                    total_time = 0
                    
                    if bridging_cost:
                        total_fee += bridging_cost.get('fee_estimate', 0)
                        total_time += bridging_cost.get('time_estimate', 0)
                        
                    if swap_cost:
                        total_fee += swap_cost.get('fee_estimate', 0)
                        total_time += swap_cost.get('time_estimate', 0)
                        
                    # Create path
                    path = {
                        'from_token': from_token,
                        'to_token': to_token,
                        'from_network': source_network,
                        'to_network': target_network,
                        'amount': amount,
                        'requires_bridge': source_network != target_network,
                        'requires_swap': from_token != to_token,
                        'bridging_cost': bridging_cost,
                        'swap_cost': swap_cost,
                        'total_fee': total_fee,
                        'total_time': total_time,
                        'score': self._calculate_path_score(total_fee, total_time)
                    }
                    
                    paths.append(path)
                    
            # Sort by score (higher is better)
            sorted_paths = sorted(paths, key=lambda x: x['score'], reverse=True)
            
            if not sorted_paths:
                return {
                    'success': False,
                    'error': "No valid paths found",
                    'path': None
                }
                
            # Return best path
            return {
                'success': True,
                'best_path': sorted_paths[0],
                'alternatives': sorted_paths[1:3],  # Next 2 best options
                'from_token': from_token,
                'to_token': to_token,
                'amount': amount
            }
            
        except Exception as e:
            logger.error(f"Error finding best cross-network path: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'path': None
            }
            
    def _calculate_path_score(self, fee: float, time: float) -> float:
        """Calculate path score based on fee and time."""
        # Lower fee and time are better
        # Normalize fee and time to 0-1 range
        max_fee = 0.1  # Assume 0.1 ETH is a very high fee
        max_time = 7 * 24 * 60 * 60  # 7 days is maximum wait time
        
        normalized_fee = 1.0 - min(1.0, fee / max_fee) if max_fee > 0 else 0.5
        normalized_time = 1.0 - min(1.0, time / max_time) if max_time > 0 else 0.5
        
        # Weight fee more than time
        return (normalized_fee * 0.7) + (normalized_time * 0.3)