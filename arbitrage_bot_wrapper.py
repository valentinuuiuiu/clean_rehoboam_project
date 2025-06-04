#!/usr/bin/env python3
"""
Wrapper to connect standalone arbitrage scripts to the centralized arbitrage service.
This allows existing bots to work with the new service architecture.
"""

import asyncio
import logging
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import importlib.util

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.arbitrage_service import arbitrage_service

logger = logging.getLogger(__name__)

class ArbitrageBotWrapper:
    """Wrapper class that connects standalone arbitrage bots to the service."""
    
    def __init__(self, bot_id: str, bot_name: str, script_path: str):
        self.bot_id = bot_id
        self.bot_name = bot_name
        self.script_path = script_path
        self.bot_module = None
        self.bot_instance = None
        self.running = False
        self.task = None
        
    async def load_bot_module(self):
        """Dynamically load the bot module."""
        try:
            spec = importlib.util.spec_from_file_location(
                f"bot_{self.bot_id}", 
                self.script_path
            )
            if spec and spec.loader:
                self.bot_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.bot_module)
                logger.info(f"✅ Loaded bot module: {self.bot_name}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to load bot {self.bot_name}: {str(e)}")
            return False
    
    async def initialize_bot(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the bot instance."""
        try:
            if not self.bot_module:
                await self.load_bot_module()
            
            # Try to find the main bot class
            bot_classes = [
                "ArbitrageMonitor", "ArbitrageExecutor", "Layer2Arbitrage",
                "LiveArbitrageMonitor", "RealArbitrageExecutor"
            ]
            
            for class_name in bot_classes:
                if hasattr(self.bot_module, class_name):
                    bot_class = getattr(self.bot_module, class_name)
                    if config:
                        self.bot_instance = bot_class(**config)
                    else:
                        self.bot_instance = bot_class()
                    logger.info(f"✅ Initialized bot instance: {class_name}")
                    return True
            
            logger.warning(f"⚠️ No recognized bot class found in {self.script_path}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot {self.bot_name}: {str(e)}")
            return False
    
    async def start_bot(self, config: Optional[Dict[str, Any]] = None):
        """Start the bot."""
        if self.running:
            logger.warning(f"⚠️ Bot {self.bot_name} is already running")
            return False
        
        try:
            if not self.bot_instance:
                if not await self.initialize_bot(config):
                    return False
            
            # Start the bot's main loop
            self.running = True
            self.task = asyncio.create_task(self._run_bot_loop())
            
            logger.info(f"🚀 Started bot: {self.bot_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot {self.bot_name}: {str(e)}")
            self.running = False
            return False
    
    async def stop_bot(self):
        """Stop the bot."""
        if not self.running:
            return True
        
        try:
            self.running = False
            
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            
            # Call bot's cleanup method if it exists
            if self.bot_instance and hasattr(self.bot_instance, 'cleanup'):
                await self.bot_instance.cleanup()
            
            logger.info(f"🛑 Stopped bot: {self.bot_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop bot {self.bot_name}: {str(e)}")
            return False
    
    async def _run_bot_loop(self):
        """Main bot execution loop."""
        try:
            while self.running:
                # Check if bot has a run method
                if hasattr(self.bot_instance, 'run'):
                    await self.bot_instance.run()
                elif hasattr(self.bot_instance, 'monitor'):
                    await self.bot_instance.monitor()
                elif hasattr(self.bot_instance, 'execute'):
                    await self.bot_instance.execute()
                else:
                    # Fallback: try to call the main function from the module
                    if hasattr(self.bot_module, 'main'):
                        await self.bot_module.main()
                    else:
                        logger.warning(f"⚠️ No run method found for bot {self.bot_name}")
                        await asyncio.sleep(10)
                
                # Small delay to prevent tight loops
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info(f"📡 Bot {self.bot_name} cancelled")
        except Exception as e:
            logger.error(f"❌ Error in bot {self.bot_name}: {str(e)}")
            self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status."""
        return {
            "bot_id": self.bot_id,
            "name": self.bot_name,
            "script_path": self.script_path,
            "status": "running" if self.running else "stopped",
            "has_instance": self.bot_instance is not None,
            "has_module": self.bot_module is not None
        }

class ArbitrageBotManager:
    """Manager for all arbitrage bot wrappers."""
    
    def __init__(self):
        self.bots: Dict[str, ArbitrageBotWrapper] = {}
        self.callbacks: list[Callable] = []
    
    def register_bot(self, bot_id: str, bot_name: str, script_path: str) -> bool:
        """Register a new bot."""
        try:
            if not os.path.exists(script_path):
                logger.error(f"❌ Bot script not found: {script_path}")
                return False
            
            wrapper = ArbitrageBotWrapper(bot_id, bot_name, script_path)
            self.bots[bot_id] = wrapper
            
            logger.info(f"📝 Registered bot: {bot_name} ({bot_id})")
            self._notify_callbacks("bot_registered", {"bot_id": bot_id, "name": bot_name})
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register bot {bot_name}: {str(e)}")
            return False
    
    async def start_bot(self, bot_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Start a specific bot."""
        if bot_id not in self.bots:
            logger.error(f"❌ Bot not found: {bot_id}")
            return False
        
        success = await self.bots[bot_id].start_bot(config)
        if success:
            self._notify_callbacks("bot_started", {"bot_id": bot_id})
        return success
    
    async def stop_bot(self, bot_id: str) -> bool:
        """Stop a specific bot."""
        if bot_id not in self.bots:
            logger.error(f"❌ Bot not found: {bot_id}")
            return False
        
        success = await self.bots[bot_id].stop_bot()
        if success:
            self._notify_callbacks("bot_stopped", {"bot_id": bot_id})
        return success
    
    async def stop_all_bots(self):
        """Stop all running bots."""
        for bot_id in self.bots:
            if self.bots[bot_id].running:
                await self.stop_bot(bot_id)
    
    def get_bot_status(self, bot_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of one or all bots."""
        if bot_id:
            if bot_id in self.bots:
                return self.bots[bot_id].get_status()
            else:
                return {"error": f"Bot {bot_id} not found"}
        else:
            return {bot_id: bot.get_status() for bot_id, bot in self.bots.items()}
    
    def register_callback(self, callback: Callable):
        """Register a callback for bot events."""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, event_type: str, data: Any):
        """Notify all registered callbacks."""
        for callback in self.callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"❌ Callback error: {str(e)}")

# Global bot manager instance
bot_manager = ArbitrageBotManager()

async def main():
    """Test the bot wrapper system."""
    print("🤖 Arbitrage Bot Wrapper Test")
    print("=" * 40)
    
    # Register test bots
    bots_to_register = [
        ("live_monitor", "Live Arbitrage Monitor", "live_arbitrage_monitor.py"),
        ("real_executor", "Real Arbitrage Executor", "real_arbitrage_executor.py"),
    ]
    
    for bot_id, name, script in bots_to_register:
        if os.path.exists(script):
            bot_manager.register_bot(bot_id, name, script)
        else:
            print(f"⚠️ Script not found: {script}")
    
    # Show status
    status = bot_manager.get_bot_status()
    print(f"\n📊 Registered bots: {len(status)}")
    for bot_id, bot_status in status.items():
        print(f"  - {bot_status['name']}: {bot_status['status']}")
    
    print("\n✅ Bot wrapper system ready")

if __name__ == "__main__":
    asyncio.run(main())