"""Trading platform state management."""
import os
import asyncio
from typing import Optional
from utils.rehoboam_ai import RehoboamAI
from utils.trading_orchestrator import TradingOrchestrator
from utils.websocket_server import EnhancedWebSocketServer

class State:
    """Main application state for the trading platform."""
    
    def __init__(self, websocket_server: EnhancedWebSocketServer):
        self.websocket_server = websocket_server
        self.rehoboam_ai: Optional[RehoboamAI] = None
        self.trading_orchestrator: Optional[TradingOrchestrator] = None
        self.is_initialized = False
        
        # Configuration from environment
        self.alchemy_api_key = os.getenv("ALCHEMY_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
    async def initialize(self):
        """Initialize all platform components."""
        if self.is_initialized:
            return
            
        try:
            # Initialize AI components
            self.rehoboam_ai = RehoboamAI(
                openrouter_api_key=self.openrouter_api_key,
                gemini_api_key=self.gemini_api_key
            )
            
            # Initialize trading orchestrator
            self.trading_orchestrator = TradingOrchestrator(
                alchemy_api_key=self.alchemy_api_key,
                ai_engine=self.rehoboam_ai
            )
            
            # Start WebSocket server
            await self.websocket_server.start()
            
            self.is_initialized = True
            print("✅ Rehoboam trading platform initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing platform: {e}")
            raise
            
    async def shutdown(self):
        """Shutdown platform components."""
        if self.websocket_server:
            await self.websocket_server.stop()
        self.is_initialized = False
        print("🔄 Rehoboam platform shutdown complete")
