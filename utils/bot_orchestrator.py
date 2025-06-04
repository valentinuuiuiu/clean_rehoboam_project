"""
Bot Orchestrator - Simple & Elegant Bot Management
================================================

Connects Rehoboam's consciousness with arbitrage bots through clean pipelines.
Simple, powerful, and beautiful coordination.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from utils.rehoboam_pipeline import rehoboam_pipeline, PipelineData
from utils.arbitrage_service import arbitrage_service, ArbitrageBotStatus

logger = logging.getLogger(__name__)

class BotMode(Enum):
    """Bot operation modes"""
    AUTONOMOUS = "autonomous"  # Full AI control
    SUPERVISED = "supervised"  # AI with human oversight
    MANUAL = "manual"         # Human control
    LEARNING = "learning"     # Learning mode

@dataclass
class BotTask:
    """Task for arbitrage bots"""
    task_id: str
    bot_id: str
    opportunity: Dict[str, Any]
    priority: int
    created_at: datetime
    deadline: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None

class BotOrchestrator:
    """
    Simple orchestrator connecting Rehoboam consciousness to arbitrage bots.
    
    Features:
    - Intelligent task distribution
    - Real-time bot coordination
    - Performance optimization
    - Learning and adaptation
    """
    
    def __init__(self):
        self.active_bots: Set[str] = set()
        self.bot_modes: Dict[str, BotMode] = {}
        self.task_queue: List[BotTask] = []
        self.active_tasks: Dict[str, BotTask] = {}
        self.completed_tasks: List[BotTask] = []
        
        # Performance tracking
        self.bot_performance: Dict[str, Dict[str, Any]] = {}
        self.orchestration_metrics = {
            "tasks_processed": 0,
            "successful_tasks": 0,
            "avg_task_time": 0.0,
            "bot_utilization": 0.0
        }
        
        # Configuration
        self.max_concurrent_tasks = 5
        self.task_timeout = timedelta(minutes=10)
        self.rebalance_interval = 30  # seconds
        
        logger.info("🎭 Bot Orchestrator initialized")
    
    async def initialize(self):
        """Initialize the orchestrator"""
        try:
            # Initialize arbitrage service
            await arbitrage_service.initialize()
            
            # Discover available bots
            await self._discover_bots()
            
            # Start orchestration loop
            asyncio.create_task(self._orchestration_loop())
            
            logger.info("✅ Bot Orchestrator ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {str(e)}")
            return False
    
    async def submit_opportunity(self, opportunity: Dict[str, Any], priority: int = 5) -> str:
        """
        Submit an arbitrage opportunity for processing.
        
        Args:
            opportunity: Arbitrage opportunity data
            priority: Task priority (1-10, higher = more urgent)
            
        Returns:
            Task ID
        """
        try:
            # Create task
            task = BotTask(
                task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.task_queue)}",
                bot_id="",  # Will be assigned by orchestrator
                opportunity=opportunity,
                priority=priority,
                created_at=datetime.now(),
                deadline=datetime.now() + self.task_timeout
            )
            
            # Add to queue (sorted by priority)
            self.task_queue.append(task)
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)
            
            logger.info(f"📝 Task submitted: {task.task_id} (priority: {priority})")
            return task.task_id
            
        except Exception as e:
            logger.error(f"❌ Error submitting opportunity: {str(e)}")
            raise
    
    async def process_with_rehoboam(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process opportunity through Rehoboam pipeline and execute with bots.
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Complete processing result
        """
        try:
            logger.info(f"🧠 Processing with Rehoboam: {opportunity.get('token_pair', 'Unknown')}")
            
            # Process through Rehoboam pipeline
            pipeline_result = await rehoboam_pipeline.process(opportunity)
            
            if pipeline_result.get("success"):
                # Submit for bot execution if decision is to execute
                decision = pipeline_result.get("decision", {})
                if decision.get("type") == "execute":
                    task_id = await self.submit_opportunity(opportunity, priority=8)
                    pipeline_result["task_id"] = task_id
                    pipeline_result["orchestration_status"] = "submitted_for_execution"
                else:
                    pipeline_result["orchestration_status"] = f"action_{decision.get('type')}"
            
            return pipeline_result
            
        except Exception as e:
            logger.error(f"❌ Error processing with Rehoboam: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def set_bot_mode(self, bot_id: str, mode: BotMode):
        """Set operation mode for a bot"""
        try:
            self.bot_modes[bot_id] = mode
            logger.info(f"🎛️ Bot {bot_id} mode set to: {mode.value}")
            
            # Update bot performance tracking
            if bot_id not in self.bot_performance:
                self.bot_performance[bot_id] = {
                    "tasks_completed": 0,
                    "success_rate": 0.0,
                    "avg_execution_time": 0.0,
                    "mode_changes": 0
                }
            
            self.bot_performance[bot_id]["mode_changes"] += 1
            
        except Exception as e:
            logger.error(f"❌ Error setting bot mode: {str(e)}")
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        try:
            bot_statuses = arbitrage_service.get_bot_status()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "active_bots": list(self.active_bots),
                "bot_modes": {bot_id: mode.value for bot_id, mode in self.bot_modes.items()},
                "task_queue_size": len(self.task_queue),
                "active_tasks": len(self.active_tasks),
                "completed_tasks": len(self.completed_tasks),
                "bot_statuses": bot_statuses,
                "performance_metrics": self.orchestration_metrics,
                "bot_performance": self.bot_performance,
                "pipeline_metrics": rehoboam_pipeline.get_metrics()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting orchestration status: {str(e)}")
            return {"error": str(e)}
    
    async def _discover_bots(self):
        """Discover available arbitrage bots"""
        try:
            bot_statuses = arbitrage_service.get_bot_status()
            
            for bot_id, bot_info in bot_statuses.items():
                self.active_bots.add(bot_id)
                
                # Set default mode based on bot type
                if "monitor" in bot_id.lower():
                    self.bot_modes[bot_id] = BotMode.AUTONOMOUS
                elif "executor" in bot_id.lower():
                    self.bot_modes[bot_id] = BotMode.SUPERVISED
                else:
                    self.bot_modes[bot_id] = BotMode.LEARNING
                
                # Initialize performance tracking
                self.bot_performance[bot_id] = {
                    "tasks_completed": 0,
                    "success_rate": 0.0,
                    "avg_execution_time": 0.0,
                    "mode_changes": 0
                }
            
            logger.info(f"🔍 Discovered {len(self.active_bots)} bots: {list(self.active_bots)}")
            
        except Exception as e:
            logger.warning(f"⚠️ Error discovering bots: {str(e)}")
    
    async def _orchestration_loop(self):
        """Main orchestration loop"""
        logger.info("🔄 Starting orchestration loop")
        
        while True:
            try:
                # Process pending tasks
                await self._process_task_queue()
                
                # Check active tasks
                await self._check_active_tasks()
                
                # Cleanup completed tasks
                await self._cleanup_tasks()
                
                # Update metrics
                await self._update_metrics()
                
                # Rebalance if needed
                await self._rebalance_bots()
                
                # Wait before next iteration
                await asyncio.sleep(self.rebalance_interval)
                
            except asyncio.CancelledError:
                logger.info("🛑 Orchestration loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in orchestration loop: {str(e)}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _process_task_queue(self):
        """Process pending tasks from the queue"""
        try:
            while (self.task_queue and 
                   len(self.active_tasks) < self.max_concurrent_tasks):
                
                task = self.task_queue.pop(0)
                
                # Assign best bot for the task
                best_bot = await self._select_best_bot(task)
                if best_bot:
                    task.bot_id = best_bot
                    task.status = "assigned"
                    
                    # Start task execution
                    asyncio.create_task(self._execute_task(task))
                    self.active_tasks[task.task_id] = task
                    
                    logger.info(f"🎯 Task {task.task_id} assigned to bot {best_bot}")
                else:
                    # No available bot, put task back
                    self.task_queue.insert(0, task)
                    break
                    
        except Exception as e:
            logger.error(f"❌ Error processing task queue: {str(e)}")
    
    async def _select_best_bot(self, task: BotTask) -> Optional[str]:
        """Select the best bot for a task"""
        try:
            available_bots = []
            
            for bot_id in self.active_bots:
                # Check if bot is available
                bot_status = arbitrage_service.get_bot_status().get(bot_id, {})
                if bot_status.get("status") == ArbitrageBotStatus.RUNNING.value:
                    
                    # Check bot mode compatibility
                    bot_mode = self.bot_modes.get(bot_id, BotMode.LEARNING)
                    if bot_mode in [BotMode.AUTONOMOUS, BotMode.SUPERVISED]:
                        
                        # Calculate bot score
                        performance = self.bot_performance.get(bot_id, {})
                        score = performance.get("success_rate", 0.5)
                        
                        available_bots.append((bot_id, score))
            
            if available_bots:
                # Select bot with highest score
                available_bots.sort(key=lambda x: x[1], reverse=True)
                return available_bots[0][0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error selecting best bot: {str(e)}")
            return None
    
    async def _execute_task(self, task: BotTask):
        """Execute a task with the assigned bot"""
        start_time = datetime.now()
        
        try:
            task.status = "executing"
            logger.info(f"🚀 Executing task {task.task_id} with bot {task.bot_id}")
            
            # Execute through arbitrage service
            result = await arbitrage_service.execute_arbitrage(
                task.opportunity,
                amount=task.opportunity.get("suggested_amount", 100)
            )
            
            # Update task
            task.result = result
            task.status = "completed" if result.get("success") else "failed"
            
            # Update bot performance
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._update_bot_performance(task.bot_id, result.get("success", False), execution_time)
            
            logger.info(f"✅ Task {task.task_id} completed: {task.status}")
            
        except Exception as e:
            task.status = "error"
            task.result = {"success": False, "error": str(e)}
            logger.error(f"❌ Task {task.task_id} failed: {str(e)}")
        
        finally:
            # Move to completed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks.append(task)
    
    async def _check_active_tasks(self):
        """Check for timed out active tasks"""
        try:
            current_time = datetime.now()
            timed_out_tasks = []
            
            for task_id, task in self.active_tasks.items():
                if task.deadline and current_time > task.deadline:
                    timed_out_tasks.append(task_id)
            
            for task_id in timed_out_tasks:
                task = self.active_tasks[task_id]
                task.status = "timeout"
                task.result = {"success": False, "error": "Task timeout"}
                
                del self.active_tasks[task_id]
                self.completed_tasks.append(task)
                
                logger.warning(f"⏰ Task {task_id} timed out")
                
        except Exception as e:
            logger.error(f"❌ Error checking active tasks: {str(e)}")
    
    async def _cleanup_tasks(self):
        """Cleanup old completed tasks"""
        try:
            # Keep only last 100 completed tasks
            if len(self.completed_tasks) > 100:
                self.completed_tasks = self.completed_tasks[-100:]
                
        except Exception as e:
            logger.error(f"❌ Error cleaning up tasks: {str(e)}")
    
    async def _update_metrics(self):
        """Update orchestration metrics"""
        try:
            total_tasks = len(self.completed_tasks)
            if total_tasks > 0:
                successful_tasks = sum(1 for task in self.completed_tasks if task.status == "completed")
                
                self.orchestration_metrics.update({
                    "tasks_processed": total_tasks,
                    "successful_tasks": successful_tasks,
                    "success_rate": successful_tasks / total_tasks,
                    "bot_utilization": len(self.active_tasks) / max(len(self.active_bots), 1)
                })
                
        except Exception as e:
            logger.error(f"❌ Error updating metrics: {str(e)}")
    
    async def _update_bot_performance(self, bot_id: str, success: bool, execution_time: float):
        """Update bot performance metrics"""
        try:
            if bot_id not in self.bot_performance:
                self.bot_performance[bot_id] = {
                    "tasks_completed": 0,
                    "success_rate": 0.0,
                    "avg_execution_time": 0.0,
                    "mode_changes": 0
                }
            
            perf = self.bot_performance[bot_id]
            perf["tasks_completed"] += 1
            
            # Update success rate
            total_tasks = perf["tasks_completed"]
            current_successes = perf["success_rate"] * (total_tasks - 1)
            if success:
                current_successes += 1
            perf["success_rate"] = current_successes / total_tasks
            
            # Update average execution time
            total_time = perf["avg_execution_time"] * (total_tasks - 1)
            perf["avg_execution_time"] = (total_time + execution_time) / total_tasks
            
        except Exception as e:
            logger.error(f"❌ Error updating bot performance: {str(e)}")
    
    async def _rebalance_bots(self):
        """Rebalance bot assignments based on performance"""
        try:
            # Simple rebalancing: adjust bot modes based on performance
            for bot_id, performance in self.bot_performance.items():
                if performance["tasks_completed"] >= 5:  # Enough data
                    success_rate = performance["success_rate"]
                    
                    current_mode = self.bot_modes.get(bot_id, BotMode.LEARNING)
                    
                    if success_rate > 0.8 and current_mode == BotMode.SUPERVISED:
                        # Promote to autonomous
                        await self.set_bot_mode(bot_id, BotMode.AUTONOMOUS)
                        logger.info(f"📈 Promoted bot {bot_id} to autonomous mode")
                        
                    elif success_rate < 0.5 and current_mode == BotMode.AUTONOMOUS:
                        # Demote to supervised
                        await self.set_bot_mode(bot_id, BotMode.SUPERVISED)
                        logger.info(f"📉 Demoted bot {bot_id} to supervised mode")
                        
        except Exception as e:
            logger.error(f"❌ Error rebalancing bots: {str(e)}")

# Global orchestrator instance
bot_orchestrator = BotOrchestrator()