"""Advanced Trading Controller with RehoboamAI integration."""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from web3 import Web3

from utils.rehoboam_ai import RehoboamAI
from utils.trading_orchestrator import AITradingOrchestrator
from utils.price_feed_service import PriceFeedService
from utils.portfolio_optimizer import PortfolioOptimizer
from utils.safety_checks import SafetyChecks
from utils.smart_order_router import smart_router

logger = logging.getLogger(__name__)

class AdvancedTradingController:
    """Main controller for the AI-driven trading system."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize core components
        self.orchestrator = AITradingOrchestrator()
        self.price_feed = PriceFeedService()
        self.llm_decision_cache = {}
        self.llm_prompt_template = {
            'system': "You are a trading strategy enhancer. Analyze the proposed trade and suggest improvements.",
            'user': """Given market conditions: {market_conditions}
            
            Proposed trade: {decision}
            
            Please analyze and suggest enhancements considering:
            1. Risk/reward ratio
            2. Market volatility
            3. Gas cost implications
            4. Portfolio balance"""
        }
        
        # Trading settings
        self.trading_active = False
        self.supported_assets = [
            'ETH', 'BTC', 'LINK', 'UNI', 'AAVE', 'MKR',
            'SNX', 'COMP', 'YFI', 'SUSHI'
        ]
        
        # Performance tracking
        self.trading_stats = {
            'trades_executed': 0,
            'successful_trades': 0,
            'total_profit_loss': 0.0,
            'start_time': datetime.now(),
            'asset_performance': {}
        }

    async def _apply_llm_enhancement(self, decision: dict, market_data: dict) -> dict:
        """Enhance trading decision with LLM analysis."""
        try:
            # Check cache first
            decision_hash = hash(json.dumps(decision, sort_keys=True))
            if decision_hash in self.llm_decision_cache:
                return self.llm_decision_cache[decision_hash]
                
            # Prepare LLM prompt
            prompt = {
                **self.llm_prompt_template,
                'market_conditions': market_data,
                'decision': decision
            }
            
            # Get LLM enhancement
            enhanced_decision = await self.orchestrator.llm_enhance_decision(prompt)
            self.llm_decision_cache[decision_hash] = enhanced_decision
            return enhanced_decision
            
        except Exception as e:
            logger.error(f"LLM enhancement failed: {str(e)}")
            return decision
        
        # Initialize Web3 connections for each chain
        self.web3_connections = self._initialize_web3_connections()
        
        logger.info("Advanced Trading Controller initialized")
        
    async def start_trading(self):
        """Start the trading system with continuous monitoring."""
        self.trading_active = True
        logger.info("Starting advanced trading system...")
        
        try:
            while self.trading_active:
                await self._trading_cycle()
                await asyncio.sleep(60)  # Main loop interval
                
        except Exception as e:
            logger.error(f"Critical error in trading system: {str(e)}")
            await self.stop_trading()
            
    async def stop_trading(self):
        """Safely stop the trading system."""
        logger.info("Stopping trading system...")
        self.trading_active = False
        
        # Close all positions if needed
        await self._close_positions()
        
        # Save performance metrics
        self._save_performance_metrics()
        
    async def _trading_cycle(self):
        """Execute one full trading cycle."""
        try:
            # 1. Gather market data
            market_data = await self._gather_market_data()
            
            # 2. Get enhanced decision with LLM analysis
            raw_decision = await self.orchestrator.analyze_and_execute(market_data)
            decision = await self._apply_llm_enhancement(raw_decision, market_data)
            
            if decision:
                # 3. Log decision and reasoning
                self._log_trading_decision(decision)
                
                # 4. Update performance metrics
                if hasattr(decision, 'success') and decision.success:
                    self._update_performance_metrics(decision)
                    
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            
    async def _gather_market_data(self) -> Dict[str, Any]:
        """Gather comprehensive market data for analysis."""
        market_data = {
            'timestamp': datetime.now(),
            'assets': {}
        }
        
        for asset in self.supported_assets:
            try:
                # Get price data
                price_data = await self._get_price_data(asset)
                
                # Get on-chain data
                chain_data = await self._get_chain_data(asset)
                
                # Combine data
                market_data['assets'][asset] = {
                    'price': price_data['price'],
                    'volume': price_data['volume'],
                    'volatility': price_data['volatility'],
                    'chain_data': chain_data,
                    'timestamp': datetime.now()
                }
                
            except Exception as e:
                logger.error(f"Error gathering data for {asset}: {str(e)}")
                continue
                
        return market_data
        
    async def _get_price_data(self, asset: str) -> Dict[str, Any]:
        """Get price and market data for an asset."""
        try:
            # Get data from price feed service
            price_data = self.price_feed.get_price_data(asset)
            
            # Calculate additional metrics
            volatility = self._calculate_volatility(price_data['price_history'])
            
            return {
                'price': price_data['current_price'],
                'volume': price_data['volume_24h'],
                'volatility': volatility,
                'price_change_24h': price_data['price_change_24h']
            }
            
        except Exception as e:
            logger.error(f"Error getting price data for {asset}: {str(e)}")
            raise
            
    async def _get_chain_data(self, asset: str) -> Dict[str, Any]:
        """Get on-chain data for asset across different networks."""
        chain_data = {}
        
        for chain, web3 in self.web3_connections.items():
            try:
                # Get relevant contract addresses
                contracts = self._get_asset_contracts(asset, chain)
                
                # Get liquidity data
                liquidity = await self._get_liquidity_data(
                    web3, contracts['pool_address']
                )
                
                # Get gas prices
                gas_price = await self._get_gas_price(web3)
                
                chain_data[chain] = {
                    'liquidity': liquidity,
                    'gas_price': gas_price,
                    'contracts': contracts
                }
                
            except Exception as e:
                logger.error(f"Error getting chain data for {asset} on {chain}: {str(e)}")
                continue
                
        return chain_data
        
    def _initialize_web3_connections(self) -> Dict[str, Web3]:
        """Initialize Web3 connections for all supported chains."""
        connections = {}
        
        # RPC endpoints (would be loaded from config in production)
        rpc_endpoints = {
            'ethereum': 'https://eth-mainnet.g.alchemy.com/v2/your-key',
            'polygon': 'https://polygon-mainnet.g.alchemy.com/v2/your-key',
            'arbitrum': 'https://arb-mainnet.g.alchemy.com/v2/your-key',
            'optimism': 'https://opt-mainnet.g.alchemy.com/v2/your-key'
        }
        
        for chain, rpc in rpc_endpoints.items():
            try:
                web3 = Web3(Web3.HTTPProvider(rpc))
                if web3.is_connected():
                    connections[chain] = web3
                else:
                    logger.error(f"Failed to connect to {chain}")
            except Exception as e:
                logger.error(f"Error initializing Web3 for {chain}: {str(e)}")
                
        return connections
        
    def _get_asset_contracts(self, asset: str, chain: str) -> Dict[str, str]:
        """Get relevant contract addresses for an asset on a specific chain."""
        # This would load from a contract registry in production
        return {
            'token_address': '0x...',
            'pool_address': '0x...',
            'oracle_address': '0x...'
        }
        
    async def _get_liquidity_data(self, web3: Web3, pool_address: str) -> Dict[str, Any]:
        """Get liquidity data from a pool contract."""
        # Implementation would interact with actual pool contracts
        return {
            'total_liquidity': 1000000,
            'utilization': 0.75
        }
        
    async def _get_gas_price(self, web3: Web3) -> int:
        """Get current gas price from network."""
        try:
            return web3.eth.gas_price
        except Exception as e:
            logger.error(f"Error getting gas price: {str(e)}")
            return 0
            
    def _calculate_volatility(self, price_history: List[float]) -> float:
        """Calculate volatility from price history."""
        if len(price_history) < 2:
            return 0.0
            
        returns = [
            (price_history[i] - price_history[i-1]) / price_history[i-1]
            for i in range(1, len(price_history))
        ]
        
        return float(np.std(returns) * np.sqrt(365 * 24))  # Annualized hourly volatility
        
    def _log_trading_decision(self, decision: Any):
        """Log trading decision and reasoning."""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'action': decision.action,
            'asset': decision.asset,
            'amount': decision.amount,
            'confidence': decision.confidence,
            'reasoning': decision.reasoning
        }
        
        logger.info(f"Trading decision: {json.dumps(log_data, indent=2)}")
        
        # Save to file for analysis
        with open('trading_decisions.log', 'a') as f:
            json.dump(log_data, f)
            f.write('\n')
            
    def _update_performance_metrics(self, decision: Any):
        """Update performance tracking metrics."""
        self.trading_stats['trades_executed'] += 1
        
        if hasattr(decision, 'success') and decision.success:
            self.trading_stats['successful_trades'] += 1
            
        # Update asset-specific metrics
        if decision.asset not in self.trading_stats['asset_performance']:
            self.trading_stats['asset_performance'][decision.asset] = {
                'trades': 0,
                'successful_trades': 0,
                'total_profit_loss': 0.0
            }
            
        asset_stats = self.trading_stats['asset_performance'][decision.asset]
        asset_stats['trades'] += 1
        if hasattr(decision, 'success') and decision.success:
            asset_stats['successful_trades'] += 1
            if hasattr(decision, 'profit_loss'):
                asset_stats['total_profit_loss'] += decision.profit_loss
                self.trading_stats['total_profit_loss'] += decision.profit_loss
                
    async def _close_positions(self):
        """Safely close all open positions."""
        for asset in self.orchestrator.active_positions:
            try:
                position = self.orchestrator.active_positions[asset]
                if position['size'] > 0:
                    await self.orchestrator.analyze_and_execute({
                        'action': 'sell',
                        'asset': asset,
                        'amount': position['size'],
                        'reason': 'system_shutdown'
                    })
            except Exception as e:
                logger.error(f"Error closing position for {asset}: {str(e)}")
                
    async def _apply_llm_enhancement(self, decision, market_data):
        """Apply LLM reasoning to trading decisions with caching."""
        if not decision:
            return None
            
        try:
            # Check cache first
            decision_hash = hash(json.dumps(decision.__dict__ if hasattr(decision, '__dict__') else str(decision), sort_keys=True))
            if decision_hash in self.llm_decision_cache:
                return self.llm_decision_cache[decision_hash]
                
            # Prepare enhanced context
            context = {
                **self.llm_prompt_template,
                'decision': decision.__dict__ if hasattr(decision, '__dict__') else str(decision),
                'market_conditions': {
                    'timestamp': market_data['timestamp'],
                    'asset_count': len(market_data['assets']),
                    'assets': {k: v['price'] for k,v in market_data['assets'].items()}
                }
            }
            
            # Get enhanced decision
            enhanced_decision = await self.orchestrator.llm_enhance_decision(context)
            if enhanced_decision:
                self.llm_decision_cache[decision_hash] = enhanced_decision
                return enhanced_decision
            return decision
            
        except Exception as e:
            logger.error(f"LLM enhancement failed: {str(e)}")
            return decision

    def _save_performance_metrics(self):
        """Save performance metrics to file."""
        metrics = {
            'trading_stats': self.trading_stats,
            'end_time': datetime.now().isoformat(),
            'total_runtime': (datetime.now() - self.trading_stats['start_time']).total_seconds()
        }
        
        with open('performance_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
            
        logger.info("Performance metrics saved")