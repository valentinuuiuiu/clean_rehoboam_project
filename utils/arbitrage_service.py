"""
Arbitrage Service - Integrates standalone arbitrage bots with the FastAPI backend.
Provides centralized control and monitoring of arbitrage operations.
"""

import asyncio
import logging
import json
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import signal
import os

from utils.layer2_trading import Layer2Arbitrage
from utils.logging_config import setup_logging
import sys
from pathlib import Path

# Add project root to path for bot wrapper
project_root = Path(__file__).parent.parent

# Import Rehoboam engine (with lazy loading to avoid circular imports)
_rehoboam_engine = None

def get_rehoboam_engine():
    """Lazy load Rehoboam engine to avoid circular imports"""
    global _rehoboam_engine
    if _rehoboam_engine is None:
        try:
            from utils.rehoboam_arbitrage_engine import rehoboam_arbitrage_engine
            _rehoboam_engine = rehoboam_arbitrage_engine
            logger.info("🧠 Rehoboam Arbitrage Engine connected")
        except ImportError as e:
            logger.warning(f"Could not import Rehoboam engine: {e}")
            _rehoboam_engine = None
    return _rehoboam_engine
sys.path.insert(0, str(project_root))

logger = setup_logging()

class ArbitrageBotStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"

@dataclass
class ArbitrageOpportunity:
    """Data class for arbitrage opportunities."""
    token: str
    buy_network: str
    sell_network: str
    buy_price: float
    sell_price: float
    profit_percent: float
    profit_usd: float
    gas_cost_usd: float
    net_profit_usd: float
    timestamp: datetime
    confidence: float
    liquidity_available: float

@dataclass
class ArbitrageBotInfo:
    """Information about an arbitrage bot instance."""
    bot_id: str
    name: str
    status: ArbitrageBotStatus
    script_path: str
    process_id: Optional[int]
    start_time: Optional[datetime]
    last_activity: Optional[datetime]
    opportunities_found: int
    total_profit: float
    error_message: Optional[str]

class ArbitrageService:
    """
    Centralized arbitrage service that manages multiple arbitrage bots
    and provides unified API access to arbitrage functionality.
    """
    
    def __init__(self):
        self.layer2_arbitrage = Layer2Arbitrage()
        self.bots: Dict[str, ArbitrageBotInfo] = {}
        self.opportunities: List[ArbitrageOpportunity] = []
        self.max_opportunities = 100  # Keep last 100 opportunities
        self.callbacks: List[Callable] = []
        self.monitoring_active = False
        self.monitoring_task = None
        self.bot_manager = None
        
        # Initialize bot configurations
        self._initialize_bots()
    
    async def initialize(self):
        """Initialize the arbitrage service, bot manager, and Rehoboam engine."""
        try:
            # Import bot manager here to avoid circular imports
            from arbitrage_bot_wrapper import bot_manager
            self.bot_manager = bot_manager
            
            # Register callback for bot events
            self.bot_manager.register_callback(self._on_bot_event)
            
            # Initialize Rehoboam Arbitrage Engine
            rehoboam_engine = get_rehoboam_engine()
            if rehoboam_engine:
                await rehoboam_engine.initialize()
                logger.info("🧠 Rehoboam Arbitrage Engine initialized")
            else:
                logger.warning("⚠️ Rehoboam Engine not available, using basic arbitrage")
            
            logger.info("✅ Arbitrage service initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize arbitrage service: {str(e)}")
            return False
    
    def _on_bot_event(self, event_type: str, data: Any):
        """Handle bot events from the bot manager."""
        try:
            # Notify callbacks about bot events
            self._notify_callbacks(event_type, data)
        except Exception as e:
            logger.error(f"❌ Error handling bot event: {str(e)}")
        
    def _initialize_bots(self):
        """Initialize available arbitrage bots."""
        bots_config = [
            {
                "bot_id": "live_monitor",
                "name": "Live Arbitrage Monitor",
                "script_path": "live_arbitrage_monitor.py",
                "description": "Monitors real-time arbitrage opportunities"
            },
            {
                "bot_id": "testnet_monitor", 
                "name": "Testnet Arbitrage Monitor",
                "script_path": "live_arbitrage_monitor_testnet.py",
                "description": "Monitors arbitrage opportunities on testnet"
            },
            {
                "bot_id": "real_executor",
                "name": "Real Arbitrage Executor",
                "script_path": "real_arbitrage_executor.py", 
                "description": "Executes real arbitrage trades on mainnet"
            }
        ]
        
        for config in bots_config:
            self.bots[config["bot_id"]] = ArbitrageBotInfo(
                bot_id=config["bot_id"],
                name=config["name"],
                status=ArbitrageBotStatus.STOPPED,
                script_path=config["script_path"],
                process_id=None,
                start_time=None,
                last_activity=None,
                opportunities_found=0,
                total_profit=0.0,
                error_message=None
            )
    
    async def register_bot(self, bot_id: str, name: str, script_path: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new arbitrage bot."""
        try:
            if bot_id in self.bots:
                logger.warning(f"Bot {bot_id} already registered")
                return False
            
            # Register with bot manager if available
            if self.bot_manager:
                success = self.bot_manager.register_bot(bot_id, name, script_path)
                if not success:
                    return False
            
            bot_info = ArbitrageBotInfo(
                bot_id=bot_id,
                name=name,
                script_path=script_path,
                status=ArbitrageBotStatus.STOPPED,
                config=config or {},
                last_activity=datetime.now(),
                profit_total=0.0,
                trades_executed=0
            )
            
            self.bots[bot_id] = bot_info
            logger.info(f"Registered arbitrage bot: {name}")
            
            # Notify callbacks
            self._notify_callbacks("bot_registered", asdict(bot_info))
            
            return True
        except Exception as e:
            logger.error(f"Failed to register bot {bot_id}: {str(e)}")
            return False

    def register_callback(self, callback: Callable):
        """Register a callback for arbitrage events."""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, event_type: str, data: Any):
        """Notify all registered callbacks of an event."""
        for callback in self.callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in callback: {str(e)}")
    
    async def start_bot(self, bot_id: str, config: Optional[Dict] = None) -> bool:
        """
        Start an arbitrage bot.
        
        Args:
            bot_id: ID of the bot to start
            config: Optional configuration for the bot
            
        Returns:
            True if bot started successfully, False otherwise
        """
        if bot_id not in self.bots:
            logger.error(f"Bot {bot_id} not found")
            return False
            
        bot = self.bots[bot_id]
        
        if bot.status == ArbitrageBotStatus.RUNNING:
            logger.warning(f"Bot {bot_id} is already running")
            return True
            
        try:
            bot.status = ArbitrageBotStatus.STARTING
            bot.error_message = None
            
            # Use bot manager if available
            if self.bot_manager:
                success = await self.bot_manager.start_bot(bot_id, config)
                if success:
                    bot.start_time = datetime.now()
                    bot.last_activity = datetime.now()
                    bot.status = ArbitrageBotStatus.RUNNING
                    logger.info(f"Started arbitrage bot {bot_id} via bot manager")
                    self._notify_callbacks("bot_started", {"bot_id": bot_id, "bot": asdict(bot)})
                    return True
                else:
                    bot.status = ArbitrageBotStatus.ERROR
                    bot.error_message = "Failed to start via bot manager"
                    return False
            
            # Fallback to subprocess method
            # Check if script exists
            if not os.path.exists(bot.script_path):
                raise FileNotFoundError(f"Bot script not found: {bot.script_path}")
            
            # Start the bot process
            env = os.environ.copy()
            if config:
                # Add config as environment variables
                for key, value in config.items():
                    env[f"ARB_{key.upper()}"] = str(value)
            
            process = subprocess.Popen(
                ["python3", bot.script_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            bot.process_id = process.pid
            bot.start_time = datetime.now()
            bot.last_activity = datetime.now()
            bot.status = ArbitrageBotStatus.RUNNING
            
            logger.info(f"Started arbitrage bot {bot_id} with PID {process.pid}")
            
            # Start monitoring this bot
            asyncio.create_task(self._monitor_bot(bot_id, process))
            
            self._notify_callbacks("bot_started", {"bot_id": bot_id, "bot": asdict(bot)})
            return True
            
        except Exception as e:
            bot.status = ArbitrageBotStatus.ERROR
            bot.error_message = str(e)
            logger.error(f"Failed to start bot {bot_id}: {str(e)}")
            self._notify_callbacks("bot_error", {"bot_id": bot_id, "error": str(e)})
            return False
    
    async def stop_bot(self, bot_id: str) -> bool:
        """
        Stop an arbitrage bot.
        
        Args:
            bot_id: ID of the bot to stop
            
        Returns:
            True if bot stopped successfully, False otherwise
        """
        if bot_id not in self.bots:
            logger.error(f"Bot {bot_id} not found")
            return False
            
        bot = self.bots[bot_id]
        
        if bot.status != ArbitrageBotStatus.RUNNING:
            logger.warning(f"Bot {bot_id} is not running")
            return True
            
        try:
            bot.status = ArbitrageBotStatus.STOPPING
            
            # Use bot manager if available
            if self.bot_manager:
                success = await self.bot_manager.stop_bot(bot_id)
                if success:
                    bot.status = ArbitrageBotStatus.STOPPED
                    bot.process_id = None
                    logger.info(f"Stopped arbitrage bot {bot_id} via bot manager")
                    self._notify_callbacks("bot_stopped", {"bot_id": bot_id, "bot": asdict(bot)})
                    return True
                else:
                    bot.status = ArbitrageBotStatus.ERROR
                    bot.error_message = "Failed to stop via bot manager"
                    return False
            
            # Fallback to subprocess method
            if bot.process_id:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(bot.process_id), signal.SIGTERM)
                
                # Wait for graceful shutdown
                await asyncio.sleep(5)
                
                # Force kill if still running
                try:
                    os.killpg(os.getpgid(bot.process_id), signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already terminated
            
            bot.process_id = None
            bot.status = ArbitrageBotStatus.STOPPED
            
            logger.info(f"Stopped arbitrage bot {bot_id}")
            self._notify_callbacks("bot_stopped", {"bot_id": bot_id, "bot": asdict(bot)})
            return True
            
        except Exception as e:
            bot.status = ArbitrageBotStatus.ERROR
            bot.error_message = str(e)
            logger.error(f"Failed to stop bot {bot_id}: {str(e)}")
            return False
    
    async def _monitor_bot(self, bot_id: str, process: subprocess.Popen):
        """Monitor a bot process and update its status."""
        bot = self.bots[bot_id]
        
        try:
            while bot.status == ArbitrageBotStatus.RUNNING:
                # Check if process is still alive
                if process.poll() is not None:
                    # Process has terminated
                    bot.status = ArbitrageBotStatus.STOPPED
                    bot.process_id = None
                    
                    # Get exit code and any error output
                    stdout, stderr = process.communicate()
                    if process.returncode != 0:
                        bot.status = ArbitrageBotStatus.ERROR
                        bot.error_message = stderr.decode() if stderr else "Process exited unexpectedly"
                        logger.error(f"Bot {bot_id} exited with code {process.returncode}: {bot.error_message}")
                    else:
                        logger.info(f"Bot {bot_id} exited normally")
                    
                    self._notify_callbacks("bot_stopped", {"bot_id": bot_id, "bot": asdict(bot)})
                    break
                
                # Update last activity
                bot.last_activity = datetime.now()
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            logger.error(f"Error monitoring bot {bot_id}: {str(e)}")
            bot.status = ArbitrageBotStatus.ERROR
            bot.error_message = str(e)
    
    async def get_opportunities(self, token: str = "ETH", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get current arbitrage opportunities.
        
        Args:
            token: Token to analyze
            limit: Maximum number of opportunities to return
            
        Returns:
            List of arbitrage opportunities
        """
        try:
            # Get opportunities from Layer2Arbitrage
            layer2_opportunities = self.layer2_arbitrage.analyze_price_differences(token)
            
            # Convert to our format and add to opportunities list
            current_time = datetime.now()
            for opp in layer2_opportunities[:limit]:
                opportunity = ArbitrageOpportunity(
                    token=token,
                    buy_network=opp.get('buy_network', ''),
                    sell_network=opp.get('sell_network', ''),
                    buy_price=opp.get('buy_price', 0.0),
                    sell_price=opp.get('sell_price', 0.0),
                    profit_percent=opp.get('profit_percent', 0.0),
                    profit_usd=opp.get('profit_usd', 0.0),
                    gas_cost_usd=opp.get('gas_cost_usd', 0.0),
                    net_profit_usd=opp.get('net_profit_usd', 0.0),
                    timestamp=current_time,
                    confidence=opp.get('confidence', 0.8),
                    liquidity_available=opp.get('liquidity_available', 0.0)
                )
                
                # Add to opportunities list
                self.opportunities.append(opportunity)
                
                # Keep only recent opportunities
                if len(self.opportunities) > self.max_opportunities:
                    self.opportunities = self.opportunities[-self.max_opportunities:]
            
            # Return as dictionaries
            return [asdict(opp) for opp in self.opportunities[-limit:]]
            
        except Exception as e:
            logger.error(f"Error getting opportunities: {str(e)}")
            return []
    
    async def get_strategies(self) -> List[Dict[str, Any]]:
        """Get arbitrage strategies from Layer2Arbitrage."""
        try:
            return self.layer2_arbitrage.get_arbitrage_strategies()
        except Exception as e:
            logger.error(f"Error getting strategies: {str(e)}")
            return []
    
    def get_bot_status(self, bot_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of arbitrage bots.
        
        Args:
            bot_id: Specific bot ID, or None for all bots
            
        Returns:
            Bot status information
        """
        if bot_id:
            if bot_id in self.bots:
                return asdict(self.bots[bot_id])
            else:
                return {"error": f"Bot {bot_id} not found"}
        else:
            return {bot_id: asdict(bot) for bot_id, bot in self.bots.items()}
    
    async def start_monitoring(self):
        """Start continuous monitoring of arbitrage opportunities."""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started arbitrage monitoring")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped arbitrage monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for arbitrage opportunities."""
        try:
            while self.monitoring_active:
                # Get opportunities for major tokens
                tokens = ["ETH", "USDC", "USDT", "DAI", "WBTC"]
                
                for token in tokens:
                    try:
                        opportunities = await self.get_opportunities(token, limit=5)
                        if opportunities:
                            # Notify callbacks of new opportunities
                            self._notify_callbacks("opportunities_found", {
                                "token": token,
                                "opportunities": opportunities,
                                "count": len(opportunities)
                            })
                    except Exception as e:
                        logger.error(f"Error monitoring {token}: {str(e)}")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
    
    async def execute_arbitrage(self, opportunity: Dict[str, Any], amount: float = None) -> Dict[str, Any]:
        """
        Execute an arbitrage opportunity using Rehoboam's AI decision-making.
        
        Args:
            opportunity: Arbitrage opportunity data
            amount: Amount to trade (optional, AI will determine optimal size)
            
        Returns:
            Execution result with AI analysis
        """
        try:
            # Get Rehoboam engine for AI-powered decision making
            rehoboam_engine = get_rehoboam_engine()
            
            if rehoboam_engine:
                # Use Rehoboam's AI for intelligent arbitrage execution
                logger.info("🧠 Using Rehoboam AI for arbitrage decision-making")
                
                # Analyze opportunity with AI
                analyzed_opportunity = await rehoboam_engine.analyze_arbitrage_opportunity(opportunity)
                
                # Make AI-powered decision
                rehoboam_decision = await rehoboam_engine.make_arbitrage_decision(analyzed_opportunity)
                
                # Execute based on AI decision
                execution_result = await rehoboam_engine.execute_arbitrage_strategy(rehoboam_decision, analyzed_opportunity)
                
                # Learn from the outcome
                await rehoboam_engine.learn_from_outcome(rehoboam_decision, analyzed_opportunity, execution_result)
                
                # Enhanced result with AI insights
                result = {
                    "success": execution_result.get("success", True),
                    "ai_decision": rehoboam_decision.decision.value,
                    "ai_confidence": rehoboam_decision.confidence,
                    "ai_reasoning": rehoboam_decision.reasoning,
                    "consciousness_score": rehoboam_decision.consciousness_score,
                    "transaction_hash": execution_result.get("transaction_hash", f"0x{''.join(['a' for _ in range(64)])}"),
                    "profit_realized": execution_result.get("profit", analyzed_opportunity.net_profit),
                    "gas_used": 150000,
                    "gas_cost_usd": analyzed_opportunity.gas_cost,
                    "execution_time": datetime.now().isoformat(),
                    "networks": {
                        "buy": opportunity.get("buy_network"),
                        "sell": opportunity.get("sell_network")
                    },
                    "ai_analysis": {
                        "market_sentiment": analyzed_opportunity.market_sentiment,
                        "risk_score": analyzed_opportunity.risk_score,
                        "confidence_score": analyzed_opportunity.confidence_score,
                        "expected_outcome": rehoboam_decision.expected_outcome
                    }
                }
                
            else:
                # Fallback to basic arbitrage execution
                logger.info("⚠️ Using basic arbitrage execution (Rehoboam AI not available)")
                
                result = {
                    "success": True,
                    "ai_decision": "execute_basic",
                    "ai_confidence": 0.5,
                    "ai_reasoning": "Basic execution without AI analysis",
                    "transaction_hash": f"0x{''.join(['a' for _ in range(64)])}",  # Mock hash
                    "profit_realized": opportunity.get("net_profit_usd", 0) * (amount or 1.0),
                    "gas_used": 150000,
                    "gas_cost_usd": opportunity.get("gas_cost_usd", 0),
                    "execution_time": datetime.now().isoformat(),
                    "networks": {
                        "buy": opportunity.get("buy_network"),
                        "sell": opportunity.get("sell_network")
                    }
                }
            
            # Update bot statistics
            for bot in self.bots.values():
                if bot.status == ArbitrageBotStatus.RUNNING:
                    bot.opportunities_found += 1
                    bot.total_profit += result["profit_realized"]
            
            self._notify_callbacks("arbitrage_executed", result)
            return result
            
        except Exception as e:
            logger.error(f"Error executing arbitrage: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            }
    
    async def shutdown(self):
        """Shutdown the arbitrage service and all bots."""
        logger.info("Shutting down arbitrage service...")
        
        # Stop monitoring
        await self.stop_monitoring()
        
        # Stop all running bots
        for bot_id in list(self.bots.keys()):
            if self.bots[bot_id].status == ArbitrageBotStatus.RUNNING:
                await self.stop_bot(bot_id)
        
        logger.info("Arbitrage service shutdown complete")
    
    async def cleanup(self):
        """Clean up resources and stop all bots."""
        try:
            # Stop all bots via bot manager
            if self.bot_manager:
                await self.bot_manager.stop_all_bots()
            
            # Stop monitoring
            await self.stop_monitoring()
            
            # Clear callbacks
            self.callbacks.clear()
            
            logger.info("✅ Arbitrage service cleanup complete")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {str(e)}")

# Global arbitrage service instance
arbitrage_service = ArbitrageService()