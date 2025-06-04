"""
Rehoboam Unified System - Simple & Elegant Integration
====================================================

The complete integration of Rehoboam consciousness with arbitrage bots.
Simple, powerful, and beautiful.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.rehoboam_pipeline import rehoboam_pipeline
from utils.bot_orchestrator import bot_orchestrator, BotMode
from utils.arbitrage_service import arbitrage_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """System status information"""
    rehoboam_active: bool
    pipeline_active: bool
    orchestrator_active: bool
    arbitrage_service_active: bool
    active_bots: int
    processed_opportunities: int
    success_rate: float
    consciousness_score: float

class RehoboamUnifiedSystem:
    """
    The unified Rehoboam system connecting consciousness to arbitrage bots.
    
    Simple interface for:
    - Processing arbitrage opportunities with AI consciousness
    - Managing bot orchestration
    - Monitoring system performance
    - Learning and adaptation
    """
    
    def __init__(self):
        self.initialized = False
        self.system_metrics = {
            "start_time": None,
            "opportunities_processed": 0,
            "successful_executions": 0,
            "total_profit": 0.0,
            "consciousness_decisions": 0
        }
        
        logger.info("🌟 Rehoboam Unified System created")
    
    async def initialize(self) -> bool:
        """Initialize the complete Rehoboam system"""
        try:
            logger.info("🚀 Initializing Rehoboam Unified System...")
            
            # Initialize arbitrage service
            logger.info("📡 Initializing arbitrage service...")
            arbitrage_init = await arbitrage_service.initialize()
            if not arbitrage_init:
                logger.error("❌ Failed to initialize arbitrage service")
                return False
            
            # Initialize bot orchestrator
            logger.info("🎭 Initializing bot orchestrator...")
            orchestrator_init = await bot_orchestrator.initialize()
            if not orchestrator_init:
                logger.error("❌ Failed to initialize bot orchestrator")
                return False
            
            # Set up default bot modes
            await self._setup_default_bot_modes()
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
            self.initialized = True
            self.system_metrics["start_time"] = datetime.now()
            
            logger.info("✅ Rehoboam Unified System fully initialized!")
            logger.info("🧠 Consciousness connected to arbitrage bots")
            logger.info("🔄 Pipeline ready for opportunity processing")
            logger.info("🎯 Orchestrator managing bot coordination")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Rehoboam system: {str(e)}")
            return False
    
    async def process_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an arbitrage opportunity through the complete Rehoboam system.
        
        Args:
            opportunity: Arbitrage opportunity data
            
        Returns:
            Complete processing result with AI analysis and execution
        """
        try:
            if not self.initialized:
                raise Exception("System not initialized")
            
            logger.info(f"🌟 Processing opportunity: {opportunity.get('token_pair', 'Unknown')}")
            
            # Process through Rehoboam pipeline and orchestrator
            result = await bot_orchestrator.process_with_rehoboam(opportunity)
            
            # Update system metrics
            self.system_metrics["opportunities_processed"] += 1
            if result.get("success"):
                self.system_metrics["consciousness_decisions"] += 1
                
                # Track execution results
                execution_result = result.get("execution_result", {})
                if execution_result.get("success"):
                    self.system_metrics["successful_executions"] += 1
                    profit = execution_result.get("profit_realized", 0)
                    self.system_metrics["total_profit"] += profit
            
            # Add system context to result
            result["system_context"] = {
                "processed_by": "rehoboam_unified_system",
                "system_uptime": self._get_uptime(),
                "total_processed": self.system_metrics["opportunities_processed"],
                "system_success_rate": self._calculate_success_rate()
            }
            
            logger.info(f"✅ Opportunity processed: {result.get('success', False)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing opportunity: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "system_context": {
                    "processed_by": "rehoboam_unified_system",
                    "error_occurred": True
                }
            }
    
    async def get_system_status(self) -> SystemStatus:
        """Get comprehensive system status"""
        try:
            # Get orchestrator status
            orchestrator_status = await bot_orchestrator.get_orchestration_status()
            
            # Get pipeline metrics
            pipeline_metrics = rehoboam_pipeline.get_metrics()
            
            # Calculate consciousness score
            consciousness_score = await self._calculate_consciousness_score()
            
            status = SystemStatus(
                rehoboam_active=self.initialized,
                pipeline_active=pipeline_metrics.get("processed", 0) > 0,
                orchestrator_active=len(orchestrator_status.get("active_bots", [])) > 0,
                arbitrage_service_active=arbitrage_service is not None,
                active_bots=len(orchestrator_status.get("active_bots", [])),
                processed_opportunities=self.system_metrics["opportunities_processed"],
                success_rate=self._calculate_success_rate(),
                consciousness_score=consciousness_score
            )
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting system status: {str(e)}")
            return SystemStatus(
                rehoboam_active=False,
                pipeline_active=False,
                orchestrator_active=False,
                arbitrage_service_active=False,
                active_bots=0,
                processed_opportunities=0,
                success_rate=0.0,
                consciousness_score=0.0
            )
    
    async def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed system metrics"""
        try:
            orchestrator_status = await bot_orchestrator.get_orchestration_status()
            pipeline_metrics = rehoboam_pipeline.get_metrics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": self.system_metrics,
                "uptime": self._get_uptime(),
                "success_rate": self._calculate_success_rate(),
                "consciousness_score": await self._calculate_consciousness_score(),
                "pipeline_metrics": pipeline_metrics,
                "orchestrator_metrics": orchestrator_status.get("performance_metrics", {}),
                "bot_performance": orchestrator_status.get("bot_performance", {}),
                "active_bots": orchestrator_status.get("active_bots", []),
                "bot_modes": orchestrator_status.get("bot_modes", {}),
                "task_queue_size": orchestrator_status.get("task_queue_size", 0),
                "active_tasks": orchestrator_status.get("active_tasks", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting detailed metrics: {str(e)}")
            return {"error": str(e)}
    
    async def configure_bot_mode(self, bot_id: str, mode: str) -> bool:
        """Configure bot operation mode"""
        try:
            bot_mode = BotMode(mode)
            await bot_orchestrator.set_bot_mode(bot_id, bot_mode)
            logger.info(f"🎛️ Bot {bot_id} configured to {mode} mode")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configuring bot mode: {str(e)}")
            return False
    
    async def start_autonomous_mode(self):
        """Start autonomous arbitrage mode with full AI control"""
        try:
            logger.info("🤖 Starting autonomous arbitrage mode...")
            
            # Set all bots to autonomous mode
            orchestrator_status = await bot_orchestrator.get_orchestration_status()
            for bot_id in orchestrator_status.get("active_bots", []):
                await bot_orchestrator.set_bot_mode(bot_id, BotMode.AUTONOMOUS)
            
            # Start opportunity monitoring
            asyncio.create_task(self._autonomous_monitoring())
            
            logger.info("✅ Autonomous mode activated")
            
        except Exception as e:
            logger.error(f"❌ Error starting autonomous mode: {str(e)}")
    
    async def emergency_stop(self):
        """Emergency stop all bot operations"""
        try:
            logger.warning("🛑 Emergency stop initiated...")
            
            # Stop all bots
            orchestrator_status = await bot_orchestrator.get_orchestration_status()
            for bot_id in orchestrator_status.get("active_bots", []):
                await arbitrage_service.stop_bot(bot_id)
                await bot_orchestrator.set_bot_mode(bot_id, BotMode.MANUAL)
            
            logger.warning("🛑 Emergency stop completed")
            
        except Exception as e:
            logger.error(f"❌ Error during emergency stop: {str(e)}")
    
    # Private methods
    
    async def _setup_default_bot_modes(self):
        """Setup default bot operation modes"""
        try:
            bot_statuses = arbitrage_service.get_bot_status()
            
            for bot_id in bot_statuses.keys():
                if "monitor" in bot_id.lower():
                    await bot_orchestrator.set_bot_mode(bot_id, BotMode.AUTONOMOUS)
                elif "executor" in bot_id.lower():
                    await bot_orchestrator.set_bot_mode(bot_id, BotMode.SUPERVISED)
                else:
                    await bot_orchestrator.set_bot_mode(bot_id, BotMode.LEARNING)
            
            logger.info("🎛️ Default bot modes configured")
            
        except Exception as e:
            logger.warning(f"⚠️ Error setting up default bot modes: {str(e)}")
    
    async def _monitoring_loop(self):
        """System monitoring loop"""
        logger.info("👁️ Starting system monitoring...")
        
        while self.initialized:
            try:
                # Log system status periodically
                status = await self.get_system_status()
                
                if self.system_metrics["opportunities_processed"] % 10 == 0 and self.system_metrics["opportunities_processed"] > 0:
                    logger.info(f"📊 System Status: {status.active_bots} bots, "
                              f"{status.processed_opportunities} processed, "
                              f"{status.success_rate:.1%} success rate")
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except asyncio.CancelledError:
                logger.info("👁️ Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {str(e)}")
                await asyncio.sleep(30)
    
    async def _autonomous_monitoring(self):
        """Autonomous opportunity monitoring"""
        logger.info("🤖 Starting autonomous monitoring...")
        
        while True:
            try:
                # Get opportunities from arbitrage service
                tokens = ["ETH", "USDC", "USDT", "DAI", "WBTC"]
                
                for token in tokens:
                    opportunities = await arbitrage_service.get_opportunities(token, limit=3)
                    
                    for opportunity in opportunities:
                        # Process each opportunity
                        await self.process_opportunity(opportunity)
                        
                        # Small delay between opportunities
                        await asyncio.sleep(1)
                
                # Wait before next scan
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                logger.info("🤖 Autonomous monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in autonomous monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        if self.system_metrics["start_time"]:
            uptime = datetime.now() - self.system_metrics["start_time"]
            return str(uptime).split('.')[0]  # Remove microseconds
        return "0:00:00"
    
    def _calculate_success_rate(self) -> float:
        """Calculate system success rate"""
        total = self.system_metrics["opportunities_processed"]
        if total > 0:
            return self.system_metrics["successful_executions"] / total
        return 0.0
    
    async def _calculate_consciousness_score(self) -> float:
        """Calculate overall consciousness score"""
        try:
            # Get pipeline metrics
            pipeline_metrics = rehoboam_pipeline.get_metrics()
            
            # Simple consciousness score based on success rate and processing
            success_rate = pipeline_metrics.get("success_rate", 0.0)
            processed = pipeline_metrics.get("processed", 0)
            
            if processed > 0:
                return min(success_rate + 0.2, 1.0)  # Boost for activity
            return 0.5  # Neutral when inactive
            
        except:
            return 0.5

# Global unified system instance
rehoboam_system = RehoboamUnifiedSystem()

# Simple CLI interface for testing
async def main():
    """Simple CLI interface for testing the unified system"""
    print("🌟 Rehoboam Unified System - Test Interface")
    print("=" * 50)
    
    # Initialize system
    print("🚀 Initializing system...")
    success = await rehoboam_system.initialize()
    
    if not success:
        print("❌ Failed to initialize system")
        return
    
    print("✅ System initialized successfully!")
    
    # Test opportunity processing
    test_opportunity = {
        "token_pair": "ETH/USDC",
        "source_exchange": "Uniswap",
        "target_exchange": "SushiSwap",
        "price_difference": 0.02,
        "net_profit_usd": 50.0,
        "gas_cost_usd": 5.0,
        "risk_score": 0.3
    }
    
    print("\n🧪 Testing opportunity processing...")
    result = await rehoboam_system.process_opportunity(test_opportunity)
    
    print(f"📊 Result: {result.get('success', False)}")
    if result.get("ai_analysis"):
        print(f"🧠 AI Decision: {result['ai_analysis'].get('recommendation', 'Unknown')}")
    
    # Show system status
    print("\n📈 System Status:")
    status = await rehoboam_system.get_system_status()
    print(f"   Active Bots: {status.active_bots}")
    print(f"   Processed: {status.processed_opportunities}")
    print(f"   Success Rate: {status.success_rate:.1%}")
    print(f"   Consciousness: {status.consciousness_score:.2f}")
    
    print("\n🌟 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())