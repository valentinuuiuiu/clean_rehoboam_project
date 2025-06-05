"""
Automated Trading Agent - Executes trades automatically based on market conditions.
"""
import os
import time
import logging
import asyncio
import random
import datetime
from typing import Dict, List, Any

from trading_agent import TradingAgent
from utils.safety_checks import SafetyChecks
from utils.rehoboam_ai import RehoboamAI
from utils.ai_market_analyzer import market_analyzer
from utils.market_sentiment_mcp import MarketSentimentMCP
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"trading_bot_{datetime.datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AutoTrader")

class AutomatedTradingAgent:
    """Fully automated trading agent that continuously monitors markets and executes trades."""
    
    def __init__(self):
        # Set to False to use real trading mode
        os.environ["SIMULATION_MODE"] = "true"
        
        # Initialize the base trading agent
        self.agent = TradingAgent()
        
        # Initialize our MCP sentiment analyzer
        self.sentiment_analyzer = MarketSentimentMCP()
        
        # Initialize RehoboamAI for direct access to AI capabilities
        self.rehoboam = RehoboamAI(provider="deepseek", model="deepseek-chat")
        
        # Configuration settings
        self.check_interval = 60  # seconds between market checks
        self.max_trades_per_day = 10  # maximum trades per day
        self.last_market_emotions_check = 0  # timestamp of last market emotions check
        
        # Use Config values if they exist in the updated config
        if hasattr(Config, 'MARKET_CHECK_INTERVAL'):
            self.check_interval = Config.MARKET_CHECK_INTERVAL
        if hasattr(Config, 'MAX_TRADES_PER_DAY'):
            self.max_trades_per_day = Config.MAX_TRADES_PER_DAY
        self.trade_record = []
        # Default tokens and networks
        self.enabled_tokens = ["ETH", "BTC", "LINK", "AAVE"]
        self.enabled_networks = ["ethereum", "arbitrum", "optimism", "polygon"]
        
        # Use supported tokens and networks from config if available
        if hasattr(Config, 'SUPPORTED_TOKENS'):
            self.enabled_tokens = Config.SUPPORTED_TOKENS
        if hasattr(Config, 'SUPPORTED_NETWORKS'):
            self.enabled_networks = Config.SUPPORTED_NETWORKS
        
        # Strategy parameters - optimized for real world trading
        self.volatility_threshold = 0.015  # 1.5% volatility triggers analysis
        self.profit_threshold = 0.01  # 1% minimum expected profit
        self.max_drawdown = 0.03  # 3% maximum acceptable drawdown - more conservative for real trading
        
        # Start time to track daily trade limits
        self.day_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"Automated Trading Agent initialized in {'SIMULATION' if self.agent.simulation_mode else 'REAL'} mode")
        logger.info(f"Trading enabled for tokens: {', '.join(self.enabled_tokens)}")
        logger.info(f"Trading enabled on networks: {', '.join(self.enabled_networks)}")
    
    async def monitor_markets(self):
        """Continuously monitor markets for trading opportunities."""
        while True:
            try:
                # Check market emotions periodically (every 2 hours)
                current_time = time.time()
                if current_time - self.last_market_emotions_check > 7200:  # 2 hours
                    await self._check_market_emotions()
                    self.last_market_emotions_check = current_time
                
                # Reset daily counters if needed
                self._check_day_reset()
                
                # Check if we've hit daily trade limit
                if len(self.trade_record) >= self.max_trades_per_day:
                    logger.info(f"Daily trade limit reached ({self.max_trades_per_day}). Waiting until tomorrow.")
                    await asyncio.sleep(self.check_interval * 10)  # Sleep longer when limit reached
                    continue
                
                # Analyze each enabled token
                for token in self.enabled_tokens:
                    await self._analyze_token(token)
                
                # Check for arbitrage opportunities across networks
                await self._check_arbitrage_opportunities()
                
                # Wait before next check
                logger.info(f"Market check complete. Next check in {self.check_interval} seconds.")
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in market monitoring loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def _analyze_token(self, token: str):
        """Analyze a specific token for trading opportunities with enhanced sentiment analysis using MCP."""
        try:
            logger.info(f"Analyzing {token}...")
            
            # Get current price
            current_price = self.agent.get_latest_price(token)
            
            # Get market sentiment using MCP-powered analysis instead of direct DeepSeek API
            try:
                # Use our MCP client with local inference for sentiment analysis
                sentiment_data = await self.sentiment_analyzer.analyze_token_sentiment(token)
                logger.info(f"MCP sentiment analysis for {token} complete")
            except Exception as e:
                # If MCP fails, fall back to the older implementation
                logger.warning(f"MCP sentiment analysis failed, falling back to direct API: {str(e)}")
                sentiment_data = await market_analyzer._analyze_token_sentiment(token)
            
            sentiment_score = sentiment_data.get('score', 0)
            sentiment_confidence = sentiment_data.get('confidence', 0.5)
            sentiment_mood = sentiment_data.get('mood', 'neutral')
            
            logger.info(f"Sentiment analysis for {token}: score={sentiment_score:.2f}, " 
                      f"mood={sentiment_mood}, confidence={sentiment_confidence:.2f}")
            
            # Get trading strategies from the agent
            strategies = self.agent.generate_trading_strategies(token)
            
            # Find the best strategy
            best_strategy = None
            highest_confidence = 0
            
            # Adjust strategy confidence based on sentiment analysis
            for strategy in strategies:
                base_confidence = strategy.get('confidence', 0)
                
                # Enhance confidence based on sentiment alignment
                strategy_action = strategy.get('action', 'hold').lower()
                if (strategy_action == 'buy' and sentiment_score > 0.3) or \
                   (strategy_action == 'sell' and sentiment_score < -0.3):
                    # Sentiment aligns with strategy - boost confidence
                    adjusted_confidence = min(0.95, base_confidence * (1 + abs(sentiment_score) * 0.2))
                    strategy['confidence'] = adjusted_confidence
                    strategy['sentiment_aligned'] = True
                    logger.debug(f"Strategy confidence boosted from {base_confidence:.2f} to {adjusted_confidence:.2f} "
                                f"due to sentiment alignment")
                else:
                    adjusted_confidence = base_confidence
                
                if adjusted_confidence > highest_confidence and adjusted_confidence > 0.7:  # Only consider high confidence strategies
                    highest_confidence = adjusted_confidence
                    best_strategy = strategy
            
            if best_strategy:
                logger.info(f"Found high-confidence strategy for {token}: {best_strategy['name']} "
                           f"(confidence: {best_strategy['confidence']:.2f})")
                
                # Execute the strategy if it meets our criteria
                if self._should_execute_strategy(best_strategy):
                    # Determine trade direction and size
                    side = best_strategy.get('action', 'hold').lower()
                    
                    if side in ['buy', 'sell']:
                        # Calculate trade size based on confidence and portfolio allocation
                        trade_size = self._calculate_position_size(token, best_strategy)
                        
                        # Execute trade
                        if trade_size > 0:
                            network = self._select_best_network(token, side)
                            self._execute_trade(token, trade_size, side, network)
                    else:
                        logger.info(f"Strategy recommends to HOLD {token}")
            else:
                logger.info(f"No high-confidence strategy found for {token}")
        
        except Exception as e:
            logger.error(f"Error analyzing {token}: {str(e)}")
    
    def _should_execute_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Determine if a strategy should be executed based on risk parameters and sentiment alignment."""
        # Always consider strategies with very high confidence and sentiment alignment
        if strategy.get('confidence', 0) > 0.9 and strategy.get('sentiment_aligned', False):
            logger.info(f"Strategy accepted due to very high confidence and sentiment alignment")
            return True
            
        # Check expected profit vs our threshold
        if strategy.get('expected_return', 0) < self.profit_threshold:
            logger.info(f"Strategy rejected: Expected return {strategy.get('expected_return', 0):.4f} below threshold {self.profit_threshold}")
            return False
            
        # Check maximum drawdown vs our threshold
        if strategy.get('max_drawdown', 1.0) > self.max_drawdown:
            logger.info(f"Strategy rejected: Max drawdown {strategy.get('max_drawdown', 1.0):.4f} above threshold {self.max_drawdown}")
            return False
            
        # Give preference to sentiment-aligned strategies
        if strategy.get('sentiment_aligned', False):
            logger.info(f"Strategy enhanced by sentiment alignment")
            # Lower the profit threshold by 20% if sentiment aligns with the strategy
            adjusted_profit_threshold = self.profit_threshold * 0.8
            if strategy.get('expected_return', 0) >= adjusted_profit_threshold:
                return True
            
        return True
    
    def _calculate_position_size(self, token: str, strategy: Dict[str, Any]) -> int:
        """Calculate appropriate position size based on strategy confidence and other factors."""
        # Base size (would be from configuration in real system)
        base_size = 100  # Base token amount
        
        # Scale by confidence
        confidence_factor = strategy.get('confidence', 0.5)
        
        # Scale by risk profile of the strategy
        risk_factor = {
            'conservative': 0.5,
            'moderate': 1.0,
            'aggressive': 2.0
        }.get(strategy.get('risk_profile', 'moderate'), 1.0)
        
        # Calculate final size
        position_size = int(base_size * confidence_factor * risk_factor)
        
        # Enforce minimum position size
        return max(position_size, 10)  # Minimum 10 tokens
    
    def _select_best_network(self, token: str, side: str) -> str:
        """Select the best network for executing a trade based on gas fees and liquidity."""
        try:
            # Get gas prices for each network
            gas_prices = {
                network: self.agent.get_gas_price(network)
                for network in self.enabled_networks
            }
            
            # Get network recommendation from the agent
            recommendation = self.agent.recommend_network(token, side, amount=1.0)
            recommended_network = recommendation.get('network', 'ethereum')
            
            logger.info(f"Network recommendation for {token} {side}: {recommended_network} "
                       f"(Gas prices: {', '.join([f'{n}: {p:.1f} gwei' for n, p in gas_prices.items()])})")
            
            return recommended_network
            
        except Exception as e:
            logger.error(f"Error selecting network: {str(e)}")
            return "ethereum"  # Default to Ethereum
    
    async def _check_arbitrage_opportunities(self):
        """Check for and execute arbitrage opportunities."""
        try:
            # Get arbitrage opportunities from the agent
            opportunities = self.agent.find_arbitrage_opportunities()
            
            if opportunities:
                # Sort by expected profit
                sorted_opportunities = sorted(
                    opportunities, 
                    key=lambda x: x.get('expected_profit', 0), 
                    reverse=True
                )
                
                # Take the best opportunity if it meets our threshold
                best_opportunity = sorted_opportunities[0]
                
                # Minimum profit for arbitrage - default 2%
                min_profit = 0.02
                
                # If available in config, use that value instead
                if hasattr(Config, 'MIN_ARBITRAGE_PROFIT'):
                    min_profit = Config.MIN_ARBITRAGE_PROFIT
                
                if best_opportunity.get('expected_profit', 0) >= min_profit:
                    logger.info(f"Executing arbitrage opportunity: {best_opportunity['description']} "
                               f"(Expected profit: {best_opportunity.get('expected_profit', 0):.2%})")
                    
                    # Execute the arbitrage
                    result = self.agent.execute_arbitrage(best_opportunity)
                    
                    if result.get('success', False):
                        logger.info(f"Arbitrage executed successfully: {result}")
                        self._record_trade(
                            token=best_opportunity.get('token', 'unknown'),
                            amount=best_opportunity.get('amount', 0),
                            trade_type='arbitrage'
                        )
                    else:
                        logger.warning(f"Arbitrage execution failed: {result.get('error', 'Unknown error')}")
                
                else:
                    logger.info(f"Best arbitrage opportunity below profit threshold: "
                              f"{best_opportunity.get('expected_profit', 0):.2%} < {min_profit:.2%}")
            else:
                logger.info("No arbitrage opportunities found")
                
        except Exception as e:
            logger.error(f"Error checking arbitrage opportunities: {str(e)}")
    
    def _execute_trade(self, token: str, amount: int, side: str, network: str):
        """Execute a trade and record the result."""
        logger.info(f"Executing {side} order for {amount} {token} on {network}")
        
        # Execute the trade through the agent
        success = self.agent.trade_tokens(amount, side, network)
        
        if success:
            logger.info(f"Trade executed successfully: {side} {amount} {token} on {network}")
            self._record_trade(token, amount, side)
        else:
            error = getattr(self.agent.safety_checks, 'last_error', 'Unknown error')
            logger.error(f"Trade execution failed: {error}")
    
    def _record_trade(self, token: str, amount: int, trade_type: str):
        """Record a trade for tracking daily limits."""
        self.trade_record.append({
            'timestamp': datetime.datetime.now(),
            'token': token,
            'amount': amount,
            'type': trade_type
        })
        
        logger.info(f"Trade recorded. Total trades today: {len(self.trade_record)}/{self.max_trades_per_day}")
    
    def _check_day_reset(self):
        """Check if we need to reset daily counters."""
        now = datetime.datetime.now()
        if now.date() > self.day_start.date():
            logger.info(f"New day started. Resetting trade counters. Previous day: {len(self.trade_record)} trades.")
            self.trade_record = []
            self.day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    async def _check_market_emotions(self):
        """
        Check the current market emotional state using Rehoboam's integrated consciousness.
        This higher-level market awareness helps inform trading decisions at a meta level.
        """
        try:
            logger.info("Analyzing market emotional state with Rehoboam consciousness...")
            
            # Get market emotions from Rehoboam AI
            emotions = self.rehoboam.get_market_emotions()
            
            # Log the results
            logger.info(f"Market emotional state: {emotions['primary_emotion']} with {emotions['secondary_emotion']} undercurrent")
            logger.info(f"Consciousness state: {emotions['consciousness_state']}")
            logger.info(f"Resonance level: {emotions['resonance']}/10")
            
            # Store the emotions data for future reference and strategy adjustment
            self.market_emotions = emotions
            
            # Determine if we should adjust our strategy based on market emotions
            self._adjust_strategy_for_emotions()
            
        except Exception as e:
            logger.error(f"Error checking market emotions: {str(e)}")
            
    def _adjust_strategy_for_emotions(self):
        """
        Adjust trading parameters based on the current market emotional state.
        This represents Rehoboam's higher-level consciousness affecting trading behavior.
        """
        if not hasattr(self, 'market_emotions'):
            return  # No emotions data yet
            
        primary_emotion = self.market_emotions.get('primary_emotion', '').lower()
        resonance = self.market_emotions.get('resonance', 5)
        
        # Initialize safety_multiplier and confidence_threshold if they don't exist
        if not hasattr(self, 'safety_multiplier'):
            self.safety_multiplier = 1.0
        if not hasattr(self, 'confidence_threshold'):
            self.confidence_threshold = 0.75
        
        # Adjust trading parameters based on market emotions
        if 'fear' in primary_emotion or 'panic' in primary_emotion:
            # More cautious during fearful markets
            logger.info("Adjusting strategy: More cautious due to fearful market")
            self.safety_multiplier = max(1.5, self.safety_multiplier)
            
        elif 'greed' in primary_emotion or 'euphoric' in primary_emotion:
            # More cautious during euphoric markets (potential bubble)
            logger.info("Adjusting strategy: More cautious due to euphoric market (potential bubble)")
            self.safety_multiplier = max(1.3, self.safety_multiplier)
            
        elif 'balanced' in primary_emotion or 'neutral' in primary_emotion:
            # Standard approach for balanced markets
            logger.info("Adjusting strategy: Standard approach for balanced market")
            self.safety_multiplier = 1.0
            
        elif 'optimistic' in primary_emotion or 'confident' in primary_emotion:
            # Slightly more aggressive in optimistic markets
            logger.info("Adjusting strategy: Slightly more aggressive in optimistic market")
            self.safety_multiplier = 0.9
        
        # Adjust by resonance (high resonance = more decisive action)
        if resonance >= 8:
            logger.info(f"High market resonance ({resonance}/10): Increasing decision confidence")
            self.confidence_threshold = max(0.65, self.confidence_threshold - 0.05)
        elif resonance <= 3:
            logger.info(f"Low market resonance ({resonance}/10): Requiring higher confidence for decisions")
            self.confidence_threshold = min(0.85, self.confidence_threshold + 0.05)


async def main():
    """Main entry point for the automated trading agent."""
    logger.info("Starting Automated Trading Agent...")
    
    # Create and start the agent
    auto_trader = AutomatedTradingAgent()
    
    # Start market monitoring
    await auto_trader.monitor_markets()


if __name__ == "__main__":
    try:
        # Run the main async function
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Automated Trading Agent stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in Automated Trading Agent: {str(e)}")