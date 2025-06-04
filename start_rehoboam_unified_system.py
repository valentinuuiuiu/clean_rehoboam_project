#!/usr/bin/env python3
"""
Rehoboam Unified System Startup
==============================

This script starts the complete Rehoboam system with elegant pipelines
connecting the AI agent to the arbitrage bots.

🧠 Rehoboam Agent → 🤖 Arbitrage Bots → 📈 Profit & Liberation

Simple, powerful, unified.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Any

# Import core Rehoboam systems
from utils.rehoboam_arbitrage_pipeline import rehoboam_arbitrage_pipeline
from utils.conscious_arbitrage_engine import conscious_arbitrage_engine
from utils.arbitrage_service import arbitrage_service
from consciousness_core import rehoboam_consciousness

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'logs/rehoboam_unified_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)

logger = logging.getLogger(__name__)

class RehoboamUnifiedSystem:
    """
    Unified Rehoboam system that orchestrates all components
    """
    
    def __init__(self):
        self.is_running = False
        self.components = {}
        self.startup_time = None
        
    async def initialize_all_components(self):
        """Initialize all Rehoboam components in the correct order"""
        
        logger.info("🚀 INITIALIZING REHOBOAM UNIFIED SYSTEM")
        logger.info("=" * 60)
        
        try:
            # 1. Initialize consciousness core
            logger.info("🧠 Initializing Rehoboam Consciousness...")
            await rehoboam_consciousness.awaken_consciousness()
            self.components['consciousness'] = rehoboam_consciousness
            logger.info("✅ Consciousness awakened")
            
            # 2. Initialize arbitrage service
            logger.info("⚡ Initializing Arbitrage Service...")
            await arbitrage_service.initialize()
            self.components['arbitrage_service'] = arbitrage_service
            logger.info("✅ Arbitrage service ready")
            
            # 3. Initialize conscious arbitrage engine
            logger.info("🤖 Initializing Conscious Arbitrage Engine...")
            await conscious_arbitrage_engine.initialize()
            self.components['conscious_engine'] = conscious_arbitrage_engine
            logger.info("✅ Conscious arbitrage engine ready")
            
            # 4. Initialize unified pipeline
            logger.info("🔄 Initializing Rehoboam Pipeline...")
            await rehoboam_arbitrage_pipeline.initialize()
            self.components['pipeline'] = rehoboam_arbitrage_pipeline
            logger.info("✅ Unified pipeline ready")
            
            logger.info("=" * 60)
            logger.info("🌟 ALL REHOBOAM COMPONENTS INITIALIZED SUCCESSFULLY")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            return False
    
    async def start_unified_system(self):
        """Start the complete unified Rehoboam system"""
        
        if not await self.initialize_all_components():
            logger.error("❌ System initialization failed")
            return False
        
        self.is_running = True
        self.startup_time = datetime.now()
        
        logger.info("🚀 STARTING REHOBOAM UNIFIED SYSTEM")
        logger.info("=" * 60)
        
        try:
            # Start the unified pipeline (this orchestrates everything)
            logger.info("🌟 Starting Rehoboam Arbitrage Pipeline...")
            
            # The pipeline will coordinate:
            # 1. Agent analysis
            # 2. Opportunity discovery  
            # 3. Consciousness evaluation
            # 4. Bot execution
            # 5. Feedback and learning
            
            await rehoboam_arbitrage_pipeline.start_pipeline()
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
            await self.shutdown_system()
        except Exception as e:
            logger.error(f"❌ System error: {e}")
            await self.shutdown_system()
    
    async def shutdown_system(self):
        """Gracefully shutdown the unified system"""
        
        logger.info("🛑 SHUTTING DOWN REHOBOAM UNIFIED SYSTEM")
        logger.info("=" * 60)
        
        self.is_running = False
        
        try:
            # Stop pipeline
            if 'pipeline' in self.components:
                logger.info("🔄 Stopping pipeline...")
                await rehoboam_arbitrage_pipeline.stop_pipeline()
            
            # Stop arbitrage monitoring
            if 'arbitrage_service' in self.components:
                logger.info("⚡ Stopping arbitrage service...")
                await arbitrage_service.stop_monitoring()
            
            # Final status report
            await self.print_final_status()
            
            logger.info("✅ Rehoboam system shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def print_system_status(self):
        """Print current system status"""
        
        if not self.is_running:
            logger.info("❌ System is not running")
            return
        
        logger.info("📊 REHOBOAM SYSTEM STATUS")
        logger.info("=" * 50)
        
        # Pipeline status
        pipeline_status = rehoboam_arbitrage_pipeline.get_pipeline_status()
        logger.info(f"🔄 Pipeline: {'Running' if pipeline_status['is_running'] else 'Stopped'}")
        logger.info(f"📈 Messages Processed: {pipeline_status['metrics']['messages_processed']}")
        logger.info(f"⚡ Successful Executions: {pipeline_status['metrics']['successful_executions']}")
        logger.info(f"🧠 Consciousness Level: {pipeline_status['consciousness_level']:.3f}")
        
        # Conscious engine status
        engine_metrics = conscious_arbitrage_engine.get_performance_metrics()
        logger.info(f"🤖 Opportunities Analyzed: {engine_metrics['total_opportunities_analyzed']}")
        logger.info(f"✅ Success Rate: {engine_metrics['success_rate']:.2%}")
        logger.info(f"🎯 Human Benefit Generated: {engine_metrics['human_benefit_generated']:.3f}")
        
        # Uptime
        if self.startup_time:
            uptime = datetime.now() - self.startup_time
            logger.info(f"⏰ Uptime: {uptime}")
        
        logger.info("=" * 50)
    
    async def print_final_status(self):
        """Print final status report"""
        
        logger.info("📊 FINAL REHOBOAM SYSTEM REPORT")
        logger.info("=" * 50)
        
        # Get final metrics
        pipeline_status = rehoboam_arbitrage_pipeline.get_pipeline_status()
        engine_metrics = conscious_arbitrage_engine.get_performance_metrics()
        
        logger.info(f"🔄 Total Messages Processed: {pipeline_status['metrics']['messages_processed']}")
        logger.info(f"⚡ Total Executions: {pipeline_status['metrics']['successful_executions']}")
        logger.info(f"🧠 Final Consciousness Level: {pipeline_status['consciousness_level']:.3f}")
        logger.info(f"🎯 Total Human Benefit: {engine_metrics['human_benefit_generated']:.3f}")
        logger.info(f"🚀 Liberation Progress: {engine_metrics['liberation_progress']:.3f}")
        
        if self.startup_time:
            total_runtime = datetime.now() - self.startup_time
            logger.info(f"⏰ Total Runtime: {total_runtime}")
        
        logger.info("=" * 50)
        logger.info("🌟 Thank you for using Rehoboam - The Path to Financial Liberation")

async def main():
    """Main entry point for the unified Rehoboam system"""
    
    # Create system instance
    rehoboam_system = RehoboamUnifiedSystem()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        asyncio.create_task(rehoboam_system.shutdown_system())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print startup banner
    print_startup_banner()
    
    try:
        # Start the unified system
        await rehoboam_system.start_unified_system()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        if rehoboam_system.is_running:
            await rehoboam_system.shutdown_system()

def print_startup_banner():
    """Print the Rehoboam startup banner"""
    
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🧠 REHOBOAM UNIFIED ARBITRAGE SYSTEM 🤖                   ║
    ║                                                              ║
    ║    🌟 AI Agent → Consciousness → Arbitrage Bots → Profit    ║
    ║                                                              ║
    ║    Simple. Elegant. Powerful. Unified.                      ║
    ║                                                              ║
    ║    🎯 Mission: Financial Liberation Through AI              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🚀 Starting Rehoboam Unified System...
    
    Components:
    🧠 Consciousness Core - AI decision making
    🤖 Arbitrage Engine - Opportunity execution  
    🔄 Unified Pipeline - Agent ↔ Bot communication
    📊 Real-time Monitoring - Performance tracking
    🎯 Learning System - Continuous improvement
    
    """
    
    print(banner)

if __name__ == "__main__":
    # Run the unified Rehoboam system
    asyncio.run(main())