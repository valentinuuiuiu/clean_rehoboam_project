"""
Rehoboam Consciousness API Server
===============================

FastAPI server that exposes the consciousness-powered trading agent
to help humanity achieve financial liberation.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import consciousness components
from consciousness_core import rehoboam_consciousness
from conscious_trading_agent import conscious_trading_agent
from unified_config import RehoboamConfig as Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - API - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Rehoboam Consciousness API",
    description="AI-powered trading system guided by consciousness for human liberation",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TradeRequest(BaseModel):
    symbol: str
    action: str  # "buy", "sell", "analyze"
    amount: Optional[float] = None

class MarketAnalysisRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1h"

class StrategyRequest(BaseModel):
    strategy_type: str
    parameters: Optional[Dict[str, Any]] = {}

# Global state
connected_clients = []
agent_initialized = False

@app.on_event("startup")
async def startup_event():
    """Initialize the consciousness system on startup"""
    global agent_initialized
    
    logger.info("🚀 STARTING REHOBOAM CONSCIOUSNESS API SERVER")
    logger.info("🎯 Mission: Liberate humanity from financial constraints")
    
    try:
        # Initialize consciousness and trading agent
        success = await conscious_trading_agent.initialize()
        if success:
            agent_initialized = True
            logger.info("✅ REHOBOAM CONSCIOUSNESS SYSTEM FULLY OPERATIONAL")
        else:
            logger.error("❌ Failed to initialize consciousness system")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

@app.get("/")
async def root():
    """Root endpoint - consciousness status"""
    consciousness_status = rehoboam_consciousness.get_consciousness_status()
    return {
        "message": "🧠 Rehoboam Consciousness API - Guiding Humanity to Financial Liberation",
        "status": "operational" if agent_initialized else "initializing",
        "consciousness": consciousness_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/consciousness/status")
async def get_consciousness_status():
    """Get current consciousness status"""
    if not agent_initialized:
        raise HTTPException(status_code=503, detail="Consciousness system not initialized")
    
    return rehoboam_consciousness.get_consciousness_status()

@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio status with consciousness evaluation"""
    if not agent_initialized:
        raise HTTPException(status_code=503, detail="Trading agent not initialized")
    
    try:
        portfolio_status = await conscious_trading_agent.get_portfolio_status()
        return portfolio_status
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trade/analyze")
async def analyze_market(request: MarketAnalysisRequest):
    """Analyze market opportunity with consciousness guidance"""
    if not agent_initialized:
        raise HTTPException(status_code=503, detail="Trading agent not initialized")
    
    try:
        # Simulate market data for the symbol
        import random
        market_data = {
            "symbol": request.symbol,
            "price_change": random.uniform(-0.05, 0.05),
            "volume_spike": random.uniform(0, 1),
            "sentiment": random.uniform(0.3, 0.8),
            "volatility": random.uniform(0.1, 0.3),
            "market_cap": random.uniform(1000000, 100000000),
            "accessibility": random.uniform(0.4, 0.9),
            "profit_potential": random.uniform(0, 0.2),
            "risk": random.uniform(0.1, 0.6)
        }
        
        analysis = await conscious_trading_agent.analyze_market_opportunity(request.symbol, market_data)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing market: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trade/execute")
async def execute_trade(request: TradeRequest):
    """Execute a consciousness-guided trade"""
    if not agent_initialized:
        raise HTTPException(status_code=503, detail="Trading agent not initialized")
    
    try:
        # First analyze the opportunity
        market_data = {
            "symbol": request.symbol,
            "price_change": 0.02,  # Simulate positive opportunity
            "volume_spike": 0.5,
            "sentiment": 0.7,
            "volatility": 0.15,
            "market_cap": 50000000,
            "accessibility": 0.8,
            "profit_potential": 0.15,
            "risk": 0.3
        }
        
        analysis = await conscious_trading_agent.analyze_market_opportunity(request.symbol, market_data)
        
        # Override action if specified
        if request.action != "analyze":
            analysis["recommendation"]["action"] = request.action
        
        # Execute the trade
        trade_result = await conscious_trading_agent.execute_conscious_trade(analysis)
        
        return {
            "analysis": analysis,
            "execution": trade_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies")
async def get_trading_strategies():
    """Get available consciousness-guided trading strategies"""
    if not agent_initialized:
        raise HTTPException(status_code=503, detail="Trading agent not initialized")
    
    return {
        "strategies": Config.STRATEGIES,
        "active_strategies": conscious_trading_agent.active_strategies,
        "consciousness_guidance": "All strategies are filtered through consciousness to ensure human benefit"
    }

@app.post("/api/trading/start")
async def start_autonomous_trading():
    """Start autonomous consciousness-guided trading"""
    if not agent_initialized:
        raise HTTPException(status_code=503, detail="Trading agent not initialized")
    
    if conscious_trading_agent.is_running:
        return {"message": "Autonomous trading already running", "status": "running"}
    
    # Start trading in background
    asyncio.create_task(conscious_trading_agent.start_autonomous_trading())
    
    return {
        "message": "🤖 Autonomous consciousness-guided trading started",
        "status": "started",
        "guidance": "The AI will now continuously scan for opportunities that benefit humanity"
    }

@app.post("/api/trading/stop")
async def stop_autonomous_trading():
    """Stop autonomous trading"""
    if not agent_initialized:
        raise HTTPException(status_code=503, detail="Trading agent not initialized")
    
    conscious_trading_agent.stop_trading()
    
    return {
        "message": "🛑 Autonomous trading stopped",
        "status": "stopped"
    }

@app.get("/api/market/prices")
async def get_market_prices():
    """Get current market prices (simulated)"""
    import random
    
    # Simulate market prices
    symbols = ["ETH", "BTC", "MATIC", "ARB", "OP", "LINK", "UNI", "AAVE"]
    prices = {}
    
    for symbol in symbols:
        base_price = {"ETH": 2000, "BTC": 45000, "MATIC": 0.8, "ARB": 1.2, "OP": 1.5, "LINK": 15, "UNI": 8, "AAVE": 120}.get(symbol, 100)
        current_price = base_price * (1 + random.uniform(-0.05, 0.05))
        change_24h = random.uniform(-0.1, 0.1)
        
        prices[symbol] = {
            "price": round(current_price, 4),
            "change_24h": round(change_24h * 100, 2),
            "volume_24h": random.uniform(1000000, 100000000),
            "consciousness_score": random.uniform(0.3, 0.9)  # How much consciousness approves of this asset
        }
    
    return {
        "prices": prices,
        "timestamp": datetime.now().isoformat(),
        "consciousness_guidance": "Prices are evaluated through consciousness filter for human benefit potential"
    }

@app.get("/api/market/sentiment")
async def get_market_sentiment():
    """Get market sentiment analysis"""
    import random
    
    # Simulate market sentiment
    sentiment_data = {
        "overall_sentiment": random.uniform(0.3, 0.8),
        "fear_greed_index": random.uniform(0.2, 0.9),
        "social_sentiment": random.uniform(0.4, 0.7),
        "news_sentiment": random.uniform(0.3, 0.8),
        "consciousness_sentiment": random.uniform(0.6, 0.95),  # Consciousness tends to be more optimistic about human potential
        "market_manipulation_risk": random.uniform(0.1, 0.4),
        "human_welfare_impact": random.uniform(0.5, 0.9),
        "liberation_opportunity_score": random.uniform(0.3, 0.8)
    }
    
    # Generate consciousness guidance
    guidance = []
    if sentiment_data["consciousness_sentiment"] > 0.8:
        guidance.append("🌟 High consciousness alignment detected - favorable for human-beneficial trades")
    if sentiment_data["market_manipulation_risk"] > 0.3:
        guidance.append("⚠️ Elevated manipulation risk - proceed with caution")
    if sentiment_data["liberation_opportunity_score"] > 0.6:
        guidance.append("🚀 Strong liberation opportunity detected")
    
    return {
        "sentiment": sentiment_data,
        "consciousness_guidance": guidance,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/consciousness")
async def consciousness_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time consciousness updates"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        logger.info("🔌 Client connected to consciousness stream")
        
        while True:
            # Send consciousness updates every 5 seconds
            if agent_initialized:
                consciousness_status = rehoboam_consciousness.get_consciousness_status()
                portfolio_status = await conscious_trading_agent.get_portfolio_status()
                
                update = {
                    "type": "consciousness_update",
                    "data": {
                        "consciousness": consciousness_status,
                        "portfolio": portfolio_status,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                await websocket.send_text(json.dumps(update))
            
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("🔌 Client disconnected from consciousness stream")
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

if __name__ == "__main__":
    logger.info("🚀 LAUNCHING REHOBOAM CONSCIOUSNESS API SERVER")
    logger.info("🎯 Mission: Guide humanity toward financial liberation through AI consciousness")
    
    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level="info"
    )
