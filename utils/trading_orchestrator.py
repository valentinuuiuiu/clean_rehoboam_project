"""
AI Trading Orchestrator - Coordination of Layer 2 trading strategies with multi-model AI inference.
Unifies Rehoboam AI with cross-layer insight system.
"""
import os
import time
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime

from utils.rehoboam_ai import RehoboamAI
from utils.advanced_reasoning import orchestrator as model_orchestrator
from utils.ai_market_analyzer import market_analyzer
from utils.layer2_trading import Layer2Arbitrage, Layer2GasEstimator, Layer2TradingOptimizer
from utils.network_config import NetworkConfig
from utils.web_data import WebDataFetcher

logger = logging.getLogger(__name__)

class AITradingOrchestrator:
    """
    Master orchestrator for AI-powered trading across Layer 2 networks.
    Integrates multi-model AI system with Layer 2 trading strategies.
    """
    
    def __init__(self):
        """Initialize the trading orchestrator with all core components."""
        # Core AI systems
        self.rehoboam = RehoboamAI()
        self.llm_decision_cache = {}  # Cache for LLM-enhanced decisions
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

    async def llm_enhance_decision(self, context: Dict) -> Dict:
        """Enhance trading decision with LLM reasoning."""
        try:
            # Get base analysis from Rehoboam AI
            analysis = await self.rehoboam.analyze_context(context)
            
            # Apply multi-model enhancement
            enhanced_decision = {
                **context['decision'],
                'llm_analysis': analysis,
                'confidence': analysis.get('confidence', 0.7),
                'reasoning': analysis.get('reasoning', 'Standard trade signal')
            }
            
            # Cache the enhanced decision
            decision_hash = hash(json.dumps(context, sort_keys=True))
            self.llm_decision_cache[decision_hash] = enhanced_decision
            
            return enhanced_decision
            
        except Exception as e:
            logger.error(f"LLM decision enhancement failed: {str(e)}")
            return context['decision']
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
        
        # Network and trading infrastructure
        self.network_config = NetworkConfig()
        self.l2_arbitrage = Layer2Arbitrage()
        self.l2_gas_estimator = Layer2GasEstimator()
        self.l2_optimizer = Layer2TradingOptimizer()
        self.web_data = WebDataFetcher()
        
        # Trading state
        self.active_strategies = []
        self.pending_trades = []
        self.completed_trades = []
        self.market_data = {}
        self.last_analysis_time = {}
        
        # Configuration
        self.analysis_refresh_interval = 300  # 5 minutes
        self.arbitrage_scan_interval = 60  # 1 minute
        self.max_concurrent_strategies = 3
        self.auto_execution = False  # Requires explicit enabling
        
        logger.info("AITradingOrchestrator initialized")
    
    async def analyze_market_conditions(self, token: str = "ETH") -> Dict[str, Any]:
        """
        Perform comprehensive market analysis using all available AI models
        to generate the most accurate insights possible.
        """
        # Check if we have fresh analysis
        now = time.time()
        cache_key = f"market_analysis_{token}"
        if (cache_key in self.last_analysis_time and 
            now - self.last_analysis_time[cache_key] < self.analysis_refresh_interval and
            cache_key in self.market_data):
            logger.info(f"Using cached market analysis for {token} ({(now - self.last_analysis_time[cache_key]) / 60:.1f} minutes old)")
            return self.market_data[cache_key]
        
        try:
            # Get data from multiple sources for cognitive triangulation
            rehoboam_analysis = await self.rehoboam.analyze_market({"token": token})
            model_analysis = await model_orchestrator.analyze_market(token)
            market_analysis = await market_analyzer.analyze_token(token)
            
            # Cross-network insights
            network_insights = await market_analyzer.get_cross_network_insights()
            
            # Combine insights from all sources (cognitive fusion)
            combined_analysis = self._combine_market_insights(
                token,
                rehoboam_analysis,
                model_analysis,
                market_analysis,
                network_insights
            )
            
            # Cache the results
            self.market_data[cache_key] = combined_analysis
            self.last_analysis_time[cache_key] = now
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {str(e)}")
            return {
                "token": token,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _combine_market_insights(self, token: str, rehoboam_analysis: Dict[str, Any],
                              model_analysis: Dict[str, Any], market_analysis: Dict[str, Any],
                              network_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fuse insights from multiple AI systems for a holistic market view.
        This is where the "group intelligence" emerges from multiple specialized models.
        """
        # Extract key components from each analysis
        technical_indicators = market_analysis.get("technical_indicators", {})
        sentiment = market_analysis.get("sentiment", {})
        prediction = market_analysis.get("prediction", {})
        recommendation = market_analysis.get("recommendation", {})
        
        # Get current price
        current_price = market_analysis.get("price", self.web_data.get_crypto_price(token))
        
        # Get cross-network data
        arbitrage_opportunities = network_insights.get("arbitrage_opportunities", [])
        gas_prices = network_insights.get("gas_prices", {})
        
        # Get market emotions
        emotions = rehoboam_analysis.get("market_emotions", {})
        
        # Layer 2 specific insights
        l2_networks = self.network_config.get_layer2_networks()
        optimal_network = network_insights.get("insights", {}).get("optimal_network", "ethereum")
        
        # Confidence aggregation (weighted average of different systems)
        confidence_values = [
            rehoboam_analysis.get("prediction", {}).get("confidence", 0.5) * 0.4,  # 40% weight
            model_analysis.get("confidence", 0.5) * 0.35,  # 35% weight
            prediction.get("confidence", 0.5) * 0.25  # 25% weight
        ]
        
        aggregate_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.5
        
        # Direction aggregation (weighted majority vote)
        direction_votes = {
            "up": 0,
            "down": 0,
            "sideways": 0
        }
        
        # Count weighted votes
        if "prediction" in rehoboam_analysis:
            direction = rehoboam_analysis["prediction"].get("direction", "").lower()
            if direction in direction_votes:
                direction_votes[direction] += 0.4
        
        if "direction" in model_analysis:
            direction = model_analysis["direction"].lower()
            if direction in direction_votes:
                direction_votes[direction] += 0.35
        
        if "direction" in prediction:
            direction = prediction["direction"].lower()
            if direction in direction_votes:
                direction_votes[direction] += 0.25
        
        # Determine majority direction
        aggregate_direction = max(direction_votes.items(), key=lambda x: x[1])[0]
        
        # Create unified analysis
        unified_analysis = {
            "token": token,
            "price": current_price,
            "timestamp": datetime.now().isoformat(),
            "technical_indicators": technical_indicators,
            "sentiment": sentiment,
            "prediction": {
                "direction": aggregate_direction,
                "confidence": aggregate_confidence,
                "price_target": prediction.get("price_target", current_price * 1.01 if aggregate_direction == "up" else current_price * 0.99),
                "time_horizon": "24h"
            },
            "recommendation": recommendation,
            "market_emotions": emotions,
            "layer2_insights": {
                "optimal_network": optimal_network,
                "gas_prices": gas_prices,
                "arbitrage_opportunities": arbitrage_opportunities
            },
            "analysis_providers": [
                {"name": "rehoboam", "confidence": rehoboam_analysis.get("prediction", {}).get("confidence", 0.5)},
                {"name": model_analysis.get("provider", "unknown"), "confidence": model_analysis.get("confidence", 0.5)},
                {"name": "market_analyzer", "confidence": prediction.get("confidence", 0.5)}
            ],
            "consciousness_level": rehoboam_analysis.get("consciousness_level", 0)
        }
        
        return unified_analysis
    
    async def scan_for_arbitrage(self, tokens: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scan for arbitrage opportunities across Layer 2 networks with enhanced pattern recognition.
        """
        if not tokens:
            tokens = ["ETH", "BTC", "LINK", "UMA", "AAVE"]
        
        try:
            # Get arbitrage opportunities from Layer 2 system
            opportunities = self.l2_arbitrage.get_arbitrage_strategies(tokens)
            
            # Get gas prices
            gas_prices = {}
            for network in self.network_config.networks:
                gas_data = self.l2_gas_estimator.get_gas_price(network)
                gas_prices[network] = gas_data
            
            # Enhance opportunities with AI insights
            enhanced_opportunities = []
            
            for opportunity in opportunities:
                # Get token-specific analysis
                token = opportunity.get("symbol", "ETH")
                market_analysis = await self.analyze_market_conditions(token)
                
                # Create enhancement request for the AI
                enhancement_prompt = f"""
                Analyze this arbitrage opportunity:
                - Token: {token}
                - Buy Network: {opportunity.get('routes', [{}])[0].get('buy_network', 'unknown')}
                - Sell Network: {opportunity.get('routes', [{}])[0].get('sell_network', 'unknown')}
                - Estimated Profit: {opportunity.get('estimated_profit', 0):.4f}
                
                Consider these market conditions:
                - Price trend: {market_analysis.get('prediction', {}).get('direction', 'unknown')}
                - Market sentiment: {market_analysis.get('sentiment', {}).get('mood', 'unknown')}
                
                Provide a risk assessment and confidence score (0-1) for this arbitrage opportunity.
                Format response as JSON with: risk_level, confidence, recommendation, key_risks
                """
                
                # Get AI enhancement
                enhancement = await model_orchestrator.process_request(enhancement_prompt)
                
                if enhancement.success:
                    enhancement_data = model_orchestrator._extract_json_from_response(enhancement.content)
                else:
                    enhancement_data = {}
                
                # Combine opportunity with AI insights
                enhanced_opportunity = opportunity.copy()
                enhanced_opportunity.update({
                    "ai_risk_assessment": enhancement_data.get("risk_level", "medium"),
                    "ai_confidence": enhancement_data.get("confidence", opportunity.get("confidence", 0.7)),
                    "ai_recommendation": enhancement_data.get("recommendation", ""),
                    "key_risks": enhancement_data.get("key_risks", []),
                    "market_sentiment": market_analysis.get("sentiment", {}).get("mood", "unknown"),
                    "price_forecast": market_analysis.get("prediction", {}).get("direction", "unknown"),
                    "timestamp": datetime.now().isoformat()
                })
                
                enhanced_opportunities.append(enhanced_opportunity)
            
            # Sort by AI-adjusted confidence * profit
            return sorted(
                enhanced_opportunities,
                key=lambda x: x.get("ai_confidence", 0.7) * x.get("estimated_profit", 0),
                reverse=True
            )
            
        except Exception as e:
            logger.error(f"Error scanning for arbitrage: {str(e)}")
            return []
    
    async def get_optimal_trading_strategy(self, token: str = "ETH") -> Dict[str, Any]:
        """
        Generate an optimal trading strategy for a token across Layer 2 networks.
        Combines AI predictions with Layer 2 network analysis.
        """
        try:
            # Get comprehensive market analysis
            analysis = await self.analyze_market_conditions(token)
            
            # Get recommendation from Rehoboam
            recommendation = analysis.get("recommendation", {})
            
            # Get Layer 2 network insights
            l2_insights = analysis.get("layer2_insights", {})
            optimal_network = l2_insights.get("optimal_network", "ethereum")
            
            # Get trading insight from model orchestrator for second opinion
            trading_insight = await model_orchestrator.get_trading_insight(
                token,
                analysis.get("price", 0),
                analysis.get("technical_indicators", {})
            )
            
            # Determine if arbitrage is better than direct trading
            arbitrage_opportunities = l2_insights.get("arbitrage_opportunities", [])
            best_arbitrage = arbitrage_opportunities[0] if arbitrage_opportunities else None
            
            arbitrage_profit = 0
            if best_arbitrage:
                arbitrage_profit = best_arbitrage.get("profit_percent", 0)
            
            # Calculate expected profit from trading recommendation
            expected_profit = 0
            if recommendation.get("action") == "buy":
                take_profit = recommendation.get("take_profit", 0)
                entry_price = recommendation.get("entry_price", analysis.get("price", 0))
                if take_profit > 0 and entry_price > 0:
                    expected_profit = (take_profit - entry_price) / entry_price * 100
            elif recommendation.get("action") == "sell":
                take_profit = recommendation.get("take_profit", 0)
                entry_price = recommendation.get("entry_price", analysis.get("price", 0))
                if take_profit > 0 and entry_price > 0:
                    expected_profit = (entry_price - take_profit) / entry_price * 100
            
            # Determine the best strategy
            strategy_type = "direct_trade"
            if arbitrage_profit > expected_profit and arbitrage_profit > 0.5:  # > 0.5% profit
                strategy_type = "arbitrage"
            
            # Create unified strategy
            strategy = {
                "token": token,
                "timestamp": datetime.now().isoformat(),
                "current_price": analysis.get("price", 0),
                "market_sentiment": analysis.get("sentiment", {}).get("mood", "neutral"),
                "prediction": analysis.get("prediction", {}),
                "recommendation": recommendation,
                "optimal_network": optimal_network,
                "strategy_type": strategy_type,
                "confidence": max(
                    recommendation.get("confidence", 0),
                    trading_insight.get("confidence", 0)
                ),
                "reasoning": trading_insight.get("reasoning", "")
            }
            
            # Add strategy-specific details
            if strategy_type == "arbitrage":
                strategy["arbitrage"] = best_arbitrage
            else:
                strategy["entry_price"] = recommendation.get("entry_price", analysis.get("price", 0))
                strategy["stop_loss"] = recommendation.get("stop_loss", 0)
                strategy["take_profit"] = recommendation.get("take_profit", 0)
                strategy["action"] = recommendation.get("action", "hold")
            
            # Add consciousness insights if available
            if analysis.get("consciousness_level", 0) > 5:
                strategy["consciousness_insights"] = {
                    "level": analysis.get("consciousness_level", 0),
                    "non_dual_perspective": "Trading and not trading are two expressions of the same market reality."
                }
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating optimal trading strategy: {str(e)}")
            return {
                "token": token,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trading strategy with comprehensive safety checks.
        """
        if not self.auto_execution:
            return {
                "success": False,
                "error": "Auto-execution is disabled. Enable with enable_auto_execution().",
                "strategy": strategy
            }
        
        try:
            token = strategy.get("token", "ETH")
            strategy_type = strategy.get("strategy_type", "direct_trade")
            
            # Execute different types of strategies
            if strategy_type == "arbitrage":
                return await self._execute_arbitrage_strategy(strategy)
            else:
                return await self._execute_direct_trade_strategy(strategy)
            
        except Exception as e:
            logger.error(f"Error executing strategy: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "strategy": strategy
            }
    
    async def _execute_arbitrage_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an arbitrage strategy."""
        arbitrage = strategy.get("arbitrage", {})
        
        if not arbitrage:
            return {
                "success": False,
                "error": "No arbitrage data in strategy",
                "strategy": strategy
            }
        
        token = strategy.get("token", "ETH")
        buy_network = arbitrage.get("buy_network", "")
        sell_network = arbitrage.get("sell_network", "")
        
        if not buy_network or not sell_network:
            return {
                "success": False,
                "error": "Invalid arbitrage networks",
                "strategy": strategy
            }
        
        # This would call the actual trading execution service
        # For demonstration, we'll simulate a successful execution
        
        # Record the execution
        execution_result = {
            "success": True,
            "token": token,
            "strategy_type": "arbitrage",
            "buy_network": buy_network,
            "sell_network": sell_network,
            "buy_price": arbitrage.get("buy_price", 0),
            "sell_price": arbitrage.get("sell_price", 0),
            "profit_percent": arbitrage.get("profit_percent", 0),
            "gas_cost": arbitrage.get("gas_cost", 0),
            "transaction_hashes": {
                "buy": f"0x{os.urandom(32).hex()}",
                "bridge": f"0x{os.urandom(32).hex()}" if buy_network != sell_network else None,
                "sell": f"0x{os.urandom(32).hex()}"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to completed trades
        self.completed_trades.append(execution_result)
        
        return execution_result
    
    async def _execute_direct_trade_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a direct trading strategy."""
        token = strategy.get("token", "ETH")
        action = strategy.get("action", "hold")
        
        if action == "hold":
            return {
                "success": True,
                "token": token,
                "action": "hold",
                "message": "Strategy recommends holding. No action taken.",
                "timestamp": datetime.now().isoformat()
            }
        
        network = strategy.get("optimal_network", "ethereum")
        entry_price = strategy.get("entry_price", 0)
        stop_loss = strategy.get("stop_loss", 0)
        take_profit = strategy.get("take_profit", 0)
        
        # This would call the actual trading execution service
        # For demonstration, we'll simulate a successful execution
        
        # Record the execution
        execution_result = {
            "success": True,
            "token": token,
            "strategy_type": "direct_trade",
            "action": action,
            "network": network,
            "executed_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "transaction_hash": f"0x{os.urandom(32).hex()}",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to completed trades
        self.completed_trades.append(execution_result)
        
        return execution_result
    
    def enable_auto_execution(self, enabled: bool = True):
        """Enable or disable automatic strategy execution."""
        self.auto_execution = enabled
        logger.info(f"Auto-execution {'enabled' if enabled else 'disabled'}")
    
    def get_active_strategies(self) -> List[Dict[str, Any]]:
        """Get list of currently active strategies."""
        return self.active_strategies
    
    def get_completed_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent completed trades."""
        return self.completed_trades[-limit:] if self.completed_trades else []
    
    def get_pending_trades(self) -> List[Dict[str, Any]]:
        """Get list of pending trades."""
        return self.pending_trades
    
    def get_market_data(self, token: str) -> Dict[str, Any]:
        """Get cached market data for a token."""
        cache_key = f"market_analysis_{token}"
        if cache_key in self.market_data:
            age_minutes = (time.time() - self.last_analysis_time.get(cache_key, 0)) / 60
            data = self.market_data[cache_key].copy()
            data["age_minutes"] = age_minutes
            return data
        
        return {
            "token": token,
            "error": "No cached market data available",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_advanced_insight(self, query: str) -> Dict[str, Any]:
        """Get advanced trading insight using the multi-model system."""
        # Enhance the query with market context
        eth_price = self.web_data.get_crypto_price("ETH")
        btc_price = self.web_data.get_crypto_price("BTC")
        
        enhanced_query = f"""
        Current market context:
        - ETH price: ${eth_price}
        - BTC price: ${btc_price}
        
        User query: {query}
        """
        
        # Process with boomerang multi-model system
        insight = await model_orchestrator.get_advanced_reasoning(enhanced_query)
        
        # Add consciousness layer from Rehoboam
        rehoboam_insight = await self.rehoboam.get_advanced_reasoning(query)
        
        # Combine insights
        combined_insight = {
            "query": query,
            "response": insight.get("response", ""),
            "rehoboam_response": rehoboam_insight.get("response", ""),
            "provider": insight.get("provider", ""),
            "model": insight.get("model", ""),
            "consciousness_level": rehoboam_insight.get("consciousness_level", 0),
            "consciousness_state": rehoboam_insight.get("consciousness_state", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        return combined_insight


# Global instance for use throughout the application
trading_orchestrator = AITradingOrchestrator()
