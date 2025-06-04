#!/usr/bin/env python3
"""
Startup script for the Rehoboam arbitrage trading system.
This script properly initializes and starts the arbitrage service with the API server.
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.arbitrage_service import arbitrage_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ArbitrageSystemManager:
    def __init__(self):
        self.running = False
        self.api_server_process = None
        
    async def start_arbitrage_service(self):
        """Initialize and start the arbitrage service."""
        logger.info("🚀 Starting Arbitrage Service...")
        
        try:
            # Initialize the arbitrage service
            await arbitrage_service.initialize()
            logger.info("✅ Arbitrage service initialized successfully")
            
            # Start monitoring
            await arbitrage_service.start_monitoring()
            logger.info("✅ Arbitrage monitoring started")
            
            # Register available bots
            bots_registered = 0
            
            # Register live monitor bot
            if await arbitrage_service.register_bot(
                "live_monitor",
                "Live Arbitrage Monitor",
                "live_arbitrage_monitor.py"
            ):
                bots_registered += 1
                logger.info("✅ Live monitor bot registered")
            
            # Register real executor bot
            if await arbitrage_service.register_bot(
                "real_executor", 
                "Real Arbitrage Executor",
                "real_arbitrage_executor.py"
            ):
                bots_registered += 1
                logger.info("✅ Real executor bot registered")
            
            # Register layer2 arbitrage bot
            if await arbitrage_service.register_bot(
                "layer2_arbitrage",
                "Layer2 Arbitrage Bot", 
                "utils/layer2_trading.py"
            ):
                bots_registered += 1
                logger.info("✅ Layer2 arbitrage bot registered")
            
            logger.info(f"📊 Total bots registered: {bots_registered}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start arbitrage service: {str(e)}")
            return False
    
    async def start_api_server(self):
        """Start the FastAPI server."""
        logger.info("🌐 Starting API Server...")
        
        try:
            # Import and run the API server
            import uvicorn
            from api_server import app
            
            # Configure uvicorn
            config = uvicorn.Config(
                app=app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                access_log=True,
                reload=False  # Disable reload in production
            )
            
            server = uvicorn.Server(config)
            
            # Start the server
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {str(e)}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown the system."""
        logger.info("🛑 Shutting down arbitrage system...")
        
        try:
            # Stop arbitrage monitoring
            await arbitrage_service.stop_monitoring()
            logger.info("✅ Arbitrage monitoring stopped")
            
            # Stop all bots
            bots_status = arbitrage_service.get_bot_status()
            for bot_id in bots_status:
                if bots_status[bot_id].get("status") == "running":
                    await arbitrage_service.stop_bot(bot_id)
                    logger.info(f"✅ Bot {bot_id} stopped")
            
            # Cleanup arbitrage service
            await arbitrage_service.cleanup()
            logger.info("✅ Arbitrage service cleaned up")
            
            self.running = False
            logger.info("🏁 System shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main run loop."""
        logger.info("🎯 Rehoboam Arbitrage Trading System")
        logger.info("=" * 50)
        
        self.setup_signal_handlers()
        self.running = True
        
        try:
            # Start arbitrage service first
            if not await self.start_arbitrage_service():
                logger.error("❌ Failed to start arbitrage service, exiting")
                return
            
            logger.info("✅ Arbitrage system ready")
            logger.info("🌐 Starting API server...")
            
            # Start API server (this will block)
            await self.start_api_server()
            
        except KeyboardInterrupt:
            logger.info("📡 Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
        finally:
            await self.shutdown()

async def main():
    """Main entry point."""
    # Check environment
    if not os.path.exists(".env"):
        logger.warning("⚠️ .env file not found, using default configuration")
    
    # Create and run the system manager
    manager = ArbitrageSystemManager()
    await manager.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
        sys.exit(1)