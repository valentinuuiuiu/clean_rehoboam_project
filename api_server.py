"""FastAPI server with integrated WebSocket support and Layer 2 rollup capabilities."""
import asyncio
import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import jwt
from pydantic import BaseModel, Field

# Import our custom modules
from utils.websocket_server import EnhancedWebSocketServer as WebSocketServer
from utils.rehoboam_ai import RehoboamAI
from utils.network_config import network_config
from utils.layer2_trading import (
    Layer2GasEstimator, 
    Layer2Arbitrage,
    Layer2Liquidation,
    Layer2TradingOptimizer,
    Layer2TradingException
)
from utils.web_data import WebDataFetcher

# Import our API routers
from api_companions import router as companions_router
from api_mcp import router as mcp_router, register_mcp_function, record_mcp_function_execution
from utils.web3_service import web3_service

import logging
logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET = "your-secret-key"  # Change this to a secure secret key
JWT_ALGORITHM = "HS256"

async def get_user_id_from_token(token: str) -> str:
    """Verify JWT token and return user_id."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except jwt.InvalidTokenError:
        return None

app = FastAPI(
    title="Web3 Trading Agent API with Layer 2 Support", 
    version="1.0.0",
    redirect_slashes=False
)
# Include our API routers
app.include_router(companions_router)
app.include_router(mcp_router)

# Initialize WebSocketServer with proper configuration
ws_server = WebSocketServer()
# Initialize connection_manager in the websocket server
from utils.connection_manager import ConnectionManager
ws_server.connection_manager = ConnectionManager()

# Initialize our Layer 2 components
web_data = WebDataFetcher()
gas_estimator = Layer2GasEstimator()
arbitrage = Layer2Arbitrage()
liquidation = Layer2Liquidation()
trading_optimizer = Layer2TradingOptimizer()

# Initialize RehoboamAI consciousness layers and intelligence modules
try:
    # Import and initialize all consciousness layers and AI modules
    from utils.rehoboam_ai import RehoboamAI
    from utils.advanced_reasoning import MultimodalOrchestrator
    from utils.ai_market_analyzer import DeepSeekMarketAnalyzer
    from utils.ai_companion_creator import AICompanionCreator
    from utils.enhanced_mcp_specialist import EnhancedMCPSpecialist
    from utils.portfolio_optimizer import PortfolioOptimizer
    
    # Initialize core Rehoboam consciousness
    if os.getenv('DEEPSEEK_API_KEY'):
        logger.info("Initializing Rehoboam consciousness layers with DeepSeek integration")
        rehoboam = RehoboamAI(provider="deepseek", model="deepseek-chat")
    else:
        logger.warning("DEEPSEEK_API_KEY not found, initializing with limited AI capabilities")
        rehoboam = RehoboamAI()
    
    # Initialize advanced reasoning orchestrator with multi-model capabilities
    reasoning_orchestrator = MultimodalOrchestrator()
    logger.info("Advanced reasoning orchestrator initialized")
    
    # Initialize market analyzer with cross-chain intelligence
    market_analyzer = DeepSeekMarketAnalyzer()
    logger.info("AI market analyzer initialized with Layer 2 awareness")
    
    # Initialize AI companion creator
    companion_creator = AICompanionCreator(rehoboam)
    logger.info("AI companion creator initialized")
    
    # Initialize enhanced MCP specialist
    mcp_specialist = EnhancedMCPSpecialist(rehoboam)
    logger.info("Enhanced MCP specialist initialized")
    
    # Initialize portfolio optimizer
    portfolio_optimizer = PortfolioOptimizer()
    logger.info("Portfolio optimizer initialized")
    
    logger.info("🧠 Rehoboam consciousness matrix fully activated")
    
except Exception as e:
    logger.error(f"Failed to initialize Rehoboam consciousness layers: {str(e)}")
    rehoboam = None
    reasoning_orchestrator = None
    market_analyzer = None
    companion_creator = None
    mcp_specialist = None
    portfolio_optimizer = None

from utils.user_preferences import preferences_manager

# Initialize companion API with consciousness layers
from api_companions import initialize_companion_system
initialize_companion_system(rehoboam, companion_creator)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
async def get_ws_server():
    return ws_server

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize WebSocket server
    await ws_server.initialize()
    await ws_server.start()
    
    # Initialize default Web3 providers
    default_providers = {
        1: os.getenv('ETHEREUM_RPC_URL', "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"),
        137: os.getenv('POLYGON_RPC_URL', "https://polygon-rpc.com"),
        42161: os.getenv('ARBITRUM_RPC_URL', "https://arb1.arbitrum.io/rpc"),
        10: os.getenv('OPTIMISM_RPC_URL', "https://mainnet.optimism.io")
    }
    
    for chain_id, rpc_url in default_providers.items():
        if "YOUR_INFURA_KEY" in rpc_url:
            logger.warning(f"Skipping chain {chain_id} - RPC URL not configured")
            continue
            
        try:
            web3_service.add_provider(chain_id, rpc_url)
            logger.info(f"Initialized Web3 provider for chain {chain_id}")
        except Exception as e:
            logger.error(f"Failed to initialize provider for chain {chain_id}: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup WebSocket connections on shutdown."""
    await ws_server.stop()

# Authentication Models
class UserCredentials(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str

# Web3 Provider Endpoints
@app.post("/api/web3/providers")
async def add_web3_provider(
    chain_id: int = Body(..., embed=True),
    rpc_url: str = Body(..., embed=True),
    user_id: str = Depends(get_current_user)
):
    """Add a Web3 provider."""
    web3_service.add_provider(chain_id, rpc_url)
    return {"status": "success", "chain_id": chain_id}

# Wallet Endpoints
@app.post("/api/web3/wallets", response_model=Dict[str, str])
async def create_wallet(user_id: str = Depends(get_current_user)):
    """Create a new wallet."""
    return web3_service.create_wallet()

@app.get("/api/web3/balance")
async def get_wallet_balance(
    address: str = Query(...),
    chain_id: int = Query(...),
    user_id: str = Depends(get_current_user)
):
    """Get wallet balance."""
    balance = web3_service.get_balance(address, chain_id)
    return {"address": address, "balance": balance}

# Transaction Endpoints
@app.post("/api/web3/transactions")
async def send_transaction(
    chain_id: int = Body(...),
    from_address: str = Body(...),
    to_address: str = Body(...),
    value: float = Body(...),
    private_key: str = Body(...),
    gas_limit: int = Body(21000),
    max_priority_fee: Optional[float] = Body(None),
    max_fee: Optional[float] = Body(None),
    user_id: str = Depends(get_current_user)
):
    """Send a transaction."""
    tx_hash = web3_service.send_transaction(
        chain_id,
        from_address,
        to_address,
        value,
        private_key,
        gas_limit,
        max_priority_fee,
        max_fee
    )
    return {"status": "success", "tx_hash": tx_hash}

# Authentication Endpoints
@app.post("/api/auth/login", response_model=TokenResponse)
async def login_for_access_token(form_data: UserCredentials = Depends()):
    """
    Authenticate user and return access token.
    Placeholder implementation.
    """
    # In a real application, you would verify username and password
    # and then create a JWT token.
    user_id = f"user_{form_data.username}" # Dummy user ID
    
    # Create a dummy token
    token_data = {"sub": form_data.username, "user_id": user_id}
    access_token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id
    }

@app.post("/api/auth/register")
async def register_user(form_data: UserCredentials = Depends()):
    """
    Register a new user.
    Placeholder implementation.
    """
    # In a real application, you would save the user to a database.
    logger.info(f"User registration attempt for: {form_data.username}")
    return {
        "message": "User registration successful (placeholder)",
        "username": form_data.username
    }

@app.get("/api/binance/ticker")
async def get_binance_ticker(symbol: str = Query(..., title="Trading Symbol")):
    """Proxy endpoint to fetch ticker price from Binance."""
    binance_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(binance_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Binance API: {str(e)}")

@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    """WebSocket endpoint for market data."""
    client_id = str(id(websocket))
    if await ws_server.connect(websocket, client_id):
        try:
            while True:
                message = await websocket.receive_json()
                await ws_server.handle_message(client_id, message)
        except WebSocketDisconnect:
            await ws_server.disconnect(client_id)

@app.websocket("/ws/trades")
async def trades_websocket(websocket: WebSocket):
    """WebSocket endpoint for trade updates."""
    client_id = str(id(websocket))
    if await ws_server.connect(websocket, client_id):
        try:
            while True:
                message = await websocket.receive_json()
                await ws_server.handle_message(client_id, message)
        except WebSocketDisconnect:
            await ws_server.disconnect(client_id)

@app.websocket("/ws/portfolio")
async def portfolio_websocket(websocket: WebSocket):
    """WebSocket endpoint for portfolio updates."""
    client_id = str(id(websocket))
    if await ws_server.connect(websocket, client_id):
        try:
            while True:
                message = await websocket.receive_json()
                await ws_server.handle_message(client_id, message)
        except WebSocketDisconnect:
            await ws_server.disconnect(client_id)

@app.websocket("/ws/strategies")
async def strategies_websocket(websocket: WebSocket):
    """WebSocket endpoint for trading strategies."""
    client_id = str(id(websocket))
    if await ws_server.connect(websocket, client_id):
        try:
            # Subscribe client to strategies channel
            await ws_server.connection_manager.subscribe(client_id, 'strategies')
            # Send initial strategies message (can be empty initially)
            await websocket.send_json({
                'type': 'strategies',
                'data': {
                    'strategies': [],
                    'timestamp': datetime.now().isoformat()
                }
            })
            
            # Handle incoming messages
            while True:
                message = await websocket.receive_json()
                if message.get('action') == 'get_strategies':
                    # Generate trading strategies based on token and risk profile
                    from trading_agent import TradingAgent
                    
                    token = message.get('token', 'ETH')
                    risk_profile = message.get('risk_profile', 'moderate')
                    
                    # Create agent instance and get strategies
                    agent = TradingAgent()
                    strategies = agent.generate_trading_strategies(token, risk_profile)
                    
                    # Send strategies back to client
                    await websocket.send_json({
                        'type': 'strategies_update',
                        'data': {
                            'token': token,
                            'strategies': strategies,
                            'timestamp': datetime.now().isoformat()
                        }
                    })
                else:
                    await ws_server.handle_message(client_id, message)
        except WebSocketDisconnect:
            await ws_server.disconnect(client_id)
        except Exception as e:
            logger.error(f"Error in strategies websocket: {str(e)}")
            await ws_server.disconnect(client_id)

# Add preferences websocket endpoint
@app.websocket("/ws/preferences")
async def preferences_websocket(websocket: WebSocket):
    """WebSocket endpoint for user preferences."""
    await websocket.accept()
    try:
        # Get user ID from token
        token = websocket.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = await get_user_id_from_token(token)
        
        if not user_id:
            await websocket.close(code=4001, reason="Unauthorized")
            return

        # Get user preferences
        user_prefs = preferences_manager.get_user_preferences(user_id)

        # Send initial preferences
        await websocket.send_json({
            'type': 'preferences_update',
            'data': user_prefs.get_all_preferences()
        })

        # Handle preference updates
        while True:
            try:
                message = await websocket.receive_json()
                action = message.get('action')

                if action == 'update_preference':
                    category = message.get('category')
                    key = message.get('key')
                    value = message.get('value')
                    user_prefs.set_preference(category, key, value)
                    
                elif action == 'update_preferences':
                    updates = message.get('updates')
                    user_prefs.update_preferences(updates)
                    
                elif action == 'reset_category':
                    category = message.get('category')
                    user_prefs.reset_category(category)
                    
                elif action == 'reset_all':
                    user_prefs.reset_all()
                    
                elif action == 'export_preferences':
                    export_path = user_prefs.export_preferences()
                    await websocket.send_json({
                        'type': 'export_complete',
                        'data': {'path': export_path}
                    })
                    continue
                    
                elif action == 'import_preferences':
                    data = message.get('data')
                    success = user_prefs.import_preferences(data)
                    if not success:
                        await websocket.send_json({
                            'type': 'error',
                            'message': 'Failed to import preferences'
                        })
                        continue

                # Send updated preferences
                await websocket.send_json({
                    'type': 'preferences_update',
                    'data': user_prefs.get_all_preferences()
                })

            except json.JSONDecodeError:
                await websocket.send_json({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                })
            except Exception as e:
                logger.error(f"Error handling preference update: {str(e)}")
                await websocket.send_json({
                    'type': 'error',
                    'message': str(e)
                })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from preferences websocket: {user_id}")
    except Exception as e:
        logger.error(f"Error in preferences websocket: {str(e)}")

async def get_current_user(authorization: str = Header(None)):
    """Get current user from authorization header."""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.replace('Bearer ', '')
    user_id = await get_user_id_from_token(token)  # Implement this based on your auth system
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

# Add preferences REST endpoints for non-WebSocket clients
@app.get("/api/preferences")
async def get_preferences(user_id: str = Depends(get_current_user)):
    """Get user preferences."""
    user_prefs = preferences_manager.get_user_preferences(user_id)
    return user_prefs.get_all_preferences()

@app.post("/api/preferences/update")
async def update_preferences(
    updates: Dict[str, Dict[str, Any]],
    user_id: str = Depends(get_current_user)
):
    """Update user preferences."""
    user_prefs = preferences_manager.get_user_preferences(user_id)
    user_prefs.update_preferences(updates)
    return user_prefs.get_all_preferences()

@app.post("/api/preferences/reset")
async def reset_preferences(
    category: Optional[str] = None,
    user_id: str = Depends(get_current_user)
):
    """Reset user preferences."""
    user_prefs = preferences_manager.get_user_preferences(user_id)
    if category:
        user_prefs.reset_category(category)
    else:
        user_prefs.reset_all()
    return user_prefs.get_all_preferences()

# Market Data Endpoints
@app.get("/api/market/prices")
async def get_market_prices():
    """Get latest cryptocurrency prices."""
    try:
        from trading_agent import TradingAgent
        from utils.web_data import get_crypto_prices
        
        # Create agent instance for price data
        agent = TradingAgent()
        
        # Try to get all prices for common tokens across networks
        prices = {}
        common_symbols = ['BTC', 'ETH', 'LINK', 'UMA', 'AAVE', 'XMR', 'USDC', 'USDT', 'DAI', 'MATIC', 'SHIB']
        
        # First try using actual market data
        try:
            market_prices = await get_crypto_prices(common_symbols)
            if market_prices:
                prices = market_prices
                logger.info(f"Fetched {len(prices)} real cryptocurrency prices")
            else:
                # If API request fails, use simulated data from agent
                for symbol in common_symbols:
                    prices[symbol] = agent.get_latest_price(symbol)
                logger.info("Using simulated prices")
        except Exception as e:
            logger.error(f"Error fetching market prices, using simulation: {e}")
            # Fallback to simulated data if API request fails
            for symbol in common_symbols:
                prices[symbol] = agent.get_latest_price(symbol)
        
        # Format prices to 2 decimal places for UI display
        formatted_prices = {symbol: float(f"{price:.2f}") for symbol, price in prices.items()}
        
        # Broadcast update through WebSocket for real-time updates
        await ws_server.broadcast_market_update({
            'type': 'prices',
            'data': {
                'prices': formatted_prices,
                'timestamp': datetime.now().isoformat()
            }
        })
        
        return {"prices": formatted_prices, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error in get_market_prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Analysis Endpoints
@app.get("/api/market/analysis")
async def get_market_analysis(token: str, timeframe: str):
    """Get market analysis with real-time updates."""
    try:
        from trading_agent import TradingAgent
        
        # Create agent instance for analysis
        agent = TradingAgent()
        
        # Get analysis from Rehoboam
        analysis = agent.analyze_market_with_rehoboam(token)
        
        # Create response with additional data
        response = {
            'token': token,
            'timeframe': timeframe,
            'sentiment': analysis.get('sentiment', 'neutral'),
            'trend': analysis.get('trend', 'sideways'),
            'support': analysis.get('support', 0),
            'resistance': analysis.get('resistance', 0),
            'recommendation': analysis.get('recommendation', 'hold'),
            'confidence': analysis.get('confidence', 0.5),
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast update through WebSocket
        await ws_server.broadcast_market_update({
            'token': token,
            'analysis': response
        })
        
        return response
    except Exception as e:
        logger.error(f"Error in market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trading/execute")
async def execute_trade(trade_data: dict):
    """Execute trade with real-time updates."""
    try:
        # Execute trade
        result = await rehoboam.execute_trade(trade_data)
        
        # Broadcast trade update
        await ws_server.broadcast_trade_update({
            'trade': result
        })
        
        return result
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trading/positions")
async def get_trading_positions(user_id: str = Depends(get_current_user)):
    """Get current open trading positions. Placeholder."""
    # In a real app, fetch positions for user_id from a database or trading service
    logger.info(f"Fetching trading positions for user: {user_id} (placeholder)")
    return {
        "success": True,
        "data": [
            {"id": "pos_1", "token": "ETH", "amount": 2.5, "entry_price": 3000, "current_price": 3450, "pnl": 1125, "network": "arbitrum"},
            {"id": "pos_2", "token": "BTC", "amount": 0.1, "entry_price": 58000, "current_price": 59423, "pnl": 142.3, "network": "ethereum"}
        ],
        "metadata": {"timestamp": datetime.now().isoformat(), "count": 2}
    }

@app.get("/api/trading/history")
async def get_trading_history(
    user_id: str = Depends(get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, gt=0, le=1000)
):
    """Get trading history. Placeholder."""
    # In a real app, fetch history for user_id, filtered by dates and limit
    logger.info(f"Fetching trading history for user: {user_id}, start: {start_date}, end: {end_date}, limit: {limit} (placeholder)")
    return {
        "success": True,
        "data": [
            {"id": "trade_1", "token": "ETH", "amount": 1.0, "price": 3050, "side": "buy", "timestamp": "2024-05-20T10:00:00Z", "network": "arbitrum"},
            {"id": "trade_2", "token": "ETH", "amount": 0.5, "price": 3200, "side": "sell", "timestamp": "2024-05-21T14:30:00Z", "network": "arbitrum"}
        ],
        "metadata": {"timestamp": datetime.now().isoformat(), "count": 2, "start_date": start_date, "end_date": end_date}
    }

@app.get("/api/portfolio/summary")
async def get_portfolio_summary():
    """Get portfolio summary with real-time updates."""
    try:
        # Get portfolio data
        summary = await rehoboam.get_portfolio_summary()
        
        # Broadcast update
        await ws_server.broadcast_portfolio_update(summary)
        
        return summary
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/performance")
async def get_portfolio_performance(
    user_id: str = Depends(get_current_user),
    timeframe: str = Query("1w", description="Timeframe e.g., 1d, 1w, 1m, 1y")
):
    """Get historical portfolio performance. Placeholder."""
    logger.info(f"Fetching portfolio performance for user: {user_id}, timeframe: {timeframe} (placeholder)")
    # Dummy data structure
    performance_data = {
        "1d": [{"timestamp": "2024-05-25T00:00:00Z", "value": 10000}, {"timestamp": "2024-05-26T00:00:00Z", "value": 10150}],
        "1w": [{"timestamp": "2024-05-19T00:00:00Z", "value": 9800}, {"timestamp": "2024-05-26T00:00:00Z", "value": 10150}],
        "1m": [{"timestamp": "2024-04-26T00:00:00Z", "value": 9500}, {"timestamp": "2024-05-26T00:00:00Z", "value": 10150}],
        "1y": [{"timestamp": "2023-05-26T00:00:00Z", "value": 8000}, {"timestamp": "2024-05-26T00:00:00Z", "value": 10150}],
    }
    return {
        "success": True,
        "data": performance_data.get(timeframe, []),
        "metadata": {"timestamp": datetime.now().isoformat(), "timeframe": timeframe}
    }

@app.get("/api/risk/metrics")
async def get_risk_metrics(user_id: str = Depends(get_current_user)):
    """Get current risk analysis and recommendations. Placeholder."""
    logger.info(f"Fetching risk metrics for user: {user_id} (placeholder)")
    return {
        "success": True,
        "data": {
            "overall_risk_score": 0.45, # Example: 0 (low) to 1 (high)
            "volatility_index": 0.6,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.15, # 15%
            "recommendations": [
                "Consider diversifying BTC holdings.",
                "Reduce exposure to high-volatility assets if risk appetite is low."
            ]
        },
        "metadata": {"timestamp": datetime.now().isoformat()}
    }

@app.get("/api/market/chart/{token}")
async def get_market_chart_data(
    token: str,
    timeframe: str = Query("1d", description="e.g., 1h, 4h, 1d, 1w, 1m"),
    interval: str = Query("15m", description="e.g., 1m, 5m, 15m, 1h, 4h, 1d")
):
    """Get OHLCV data for charting. Placeholder."""
    logger.info(f"Fetching chart data for {token}, timeframe: {timeframe}, interval: {interval} (placeholder)")
    # Dummy OHLCV data
    ohlcv_data = [
        {"timestamp": "2024-05-26T10:00:00Z", "open": 3400, "high": 3420, "low": 3390, "close": 3410, "volume": 1000},
        {"timestamp": "2024-05-26T10:15:00Z", "open": 3410, "high": 3430, "low": 3405, "close": 3425, "volume": 1200},
    ]
    return {
        "success": True,
        "data": ohlcv_data,
        "metadata": {"token": token, "timeframe": timeframe, "interval": interval, "timestamp": datetime.now().isoformat()}
    }

@app.get("/api/market/orderbook/{token}")
async def get_market_orderbook(token: str, depth: int = Query(20, gt=0, le=100)):
    """Get current orderbook depth. Placeholder."""
    logger.info(f"Fetching order book for {token}, depth: {depth} (placeholder)")
    # Dummy order book data
    orderbook_data = {
        "bids": [["3400.50", "2.5"], ["3400.00", "5.0"]], # [price, quantity]
        "asks": [["3401.00", "3.0"], ["3401.50", "1.5"]],
        "timestamp": datetime.now().isoformat()
    }
    return {
        "success": True,
        "data": orderbook_data,
        "metadata": {"token": token, "depth": depth}
    }

@app.get("/api/ai/emotions")
async def get_market_emotions():
    """Get market emotional state from Rehoboam."""
    try:
        emotions = await rehoboam.get_market_emotions()
        
        # Broadcast emotion update
        await ws_server.broadcast_emotion_update(emotions)
        
        return emotions
    except Exception as e:
        logger.error(f"Error getting market emotions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check basic connectivity and module availability
    core_modules_active = all([
        rehoboam,
        reasoning_orchestrator,
        market_analyzer,
        ws_server
    ])
    return {
        "status": "healthy" if core_modules_active else "degraded",
        "timestamp": datetime.now().isoformat(),
        "active_modules": {
            "rehoboam_core": rehoboam is not None,
            "reasoning_orchestrator": reasoning_orchestrator is not None,
            "market_analyzer": market_analyzer is not None,
            "websocket_server": ws_server is not None,
            "companion_creator": companion_creator is not None,
            "mcp_specialist": mcp_specialist is not None,
            "portfolio_optimizer": portfolio_optimizer is not None,
            "gas_estimator": gas_estimator is not None,
            "arbitrage_module": arbitrage is not None,
            "liquidation_module": liquidation is not None,
            "trading_optimizer_module": trading_optimizer is not None
        },
        "message": "API is operational" if core_modules_active else "One or more core modules are not available"
    }

@app.get("/")
async def root():
    """Root path for health check and API info"""
    return {
        "name": "Advanced Trading Platform API",
        "version": "1.0.0",
        "status": "online",
        "description": "AI-Powered Layer 2 Blockchain Trading API",
        "endpoints": {
            "networks": "/api/networks",
            "market_prices": "/api/market/prices",
            "trading_strategies": "/api/trading/strategies",
            "arbitrage": "/api/arbitrage/strategies",
            "websockets": {
                "market": "/ws/market",
                "strategies": "/ws/strategies",
                "trades": "/ws/trades",
                "portfolio": "/ws/portfolio"
            }
        }
    }

@app.get("/api/trading/strategies")
async def get_trading_strategies(token: str = Query("ETH", title="Token Symbol"), 
                               risk_profile: str = Query("moderate", title="Risk Profile")):
    """Get AI-generated trading strategies using Rehoboam's consciousness layers."""
    try:
        # Use real consciousness layers for strategy generation
        strategies = []
        
        if market_analyzer:
            # Get comprehensive market analysis using DeepSeek AI
            logger.info(f"Analyzing {token} with Rehoboam's market intelligence")
            analysis = await market_analyzer.analyze_token(token)
            
            if reasoning_orchestrator:
                # Use advanced reasoning to enhance the strategy
                reasoning_prompt = f"""
                As Rehoboam, analyze this market data for {token} and generate advanced trading strategies.
                
                Market Analysis: {json.dumps(analysis, indent=2)}
                Risk Profile: {risk_profile}
                
                Generate sophisticated trading strategies that leverage Layer 2 networks and consider:
                1. Cross-chain arbitrage opportunities
                2. Gas optimization across networks
                3. Market sentiment and technical indicators
                4. Portfolio risk management
                5. Multi-dimensional consciousness layers
                
                Format as JSON with strategy objects containing: id, name, description, confidence, 
                risk_level, expected_return, timeframe, networks, reasoning, action_steps
                """
                
                try:
                    reasoning_response = await reasoning_orchestrator.process_request(reasoning_prompt)
                    if reasoning_response and reasoning_response.success:
                        # Parse the AI-generated strategies
                        import re
                        json_match = re.search(r'\{.*\}', reasoning_response.content, re.DOTALL)
                        if json_match:
                            ai_strategies = json.loads(json_match.group())
                            if isinstance(ai_strategies, dict) and 'strategies' in ai_strategies:
                                strategies.extend(ai_strategies['strategies'])
                            elif isinstance(ai_strategies, list):
                                strategies.extend(ai_strategies)
                except Exception as e:
                    logger.warning(f"Error processing AI reasoning: {e}")
            
            # Add MCP-generated strategy if available
            if mcp_specialist:
                try:
                    mcp_strategy = await mcp_specialist.generate_trading_strategy(token, analysis, risk_profile)
                    if mcp_strategy:
                        strategies.append(mcp_strategy)
                except Exception as e:
                    logger.warning(f"Error generating MCP strategy: {e}")
                    
            # Generate portfolio optimization strategy if available
            if portfolio_optimizer:
                try:
                    optimization_strategy = portfolio_optimizer.generate_rebalancing_strategy(
                        current_token=token,
                        risk_profile=risk_profile,
                        market_conditions=analysis
                    )
                    if optimization_strategy:
                        strategies.append(optimization_strategy)
                except Exception as e:
                    logger.warning(f"Error generating portfolio optimization strategy: {e}")
        
        # Fallback to basic strategy if no consciousness layers available
        if not strategies:
            logger.warning("Using fallback strategy generation")
            from trading_agent import TradingAgent
            agent = TradingAgent()
            
            if hasattr(agent, 'generate_trading_strategies'):
                strategies = agent.generate_trading_strategies(token, risk_profile)
            else:
                analysis = agent.analyze_market_with_rehoboam(token)
                
                strategy = {
                    'id': f"{token.lower()}-fallback-strategy-1",
                    'name': f"{token} Basic Strategy",
                    'description': f"Basic strategy for {token} (consciousness layers unavailable)",
                    'token': token,
                    'recommendation': analysis.get('recommendation', 'hold'),
                    'confidence': analysis.get('confidence', 0.5),
                    'risk_level': risk_profile,
                    'expected_return': 0.05 if analysis.get('recommendation') == 'buy' else 0.02,
                    'timeframe': '24h',
                    'reasoning': 'Basic analysis - advanced consciousness layers offline',
                    'networks': ['ethereum', 'arbitrum'],
                    'timestamp': datetime.now().isoformat()
                }
                strategies = [strategy]
        
        # Add metadata about consciousness state
        response = {
            'strategies': strategies,
            'consciousness_state': {
                'rehoboam_active': rehoboam is not None,
                'reasoning_active': reasoning_orchestrator is not None,
                'market_analyzer_active': market_analyzer is not None,
                'mcp_specialist_active': mcp_specialist is not None,
                'portfolio_optimizer_active': portfolio_optimizer is not None
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'token': token,
            'risk_profile': risk_profile
        }
        
        # Broadcast strategy update via WebSocket
        await ws_server.broadcast_strategy_update(response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating trading strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Layer 2 specific endpoints
@app.get("/api/networks")
async def get_networks():
    """Get all supported networks with their details."""
    try:
        networks = []
        for network_id, network in network_config.networks.items():
            networks.append({
                "id": network_id,
                "name": network.get("name", ""),
                "chain_id": network.get("chain_id", 0),
                "type": network.get("type", ""),
                "layer": network.get("layer", 1),
                "currency": network.get("currency", ""),
                "rollup_type": network.get("rollup_type", None)
            })
            
        return {
            "networks": networks,
            "count": len(networks),
            "layer1_count": len([n for n in networks if n["layer"] == 1]),
            "layer2_count": len([n for n in networks if n["layer"] == 2])
        }
    except Exception as e:
        logger.error(f"Error getting networks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/networks/compare")
async def compare_networks(token: str = Query("ETH", title="Token Symbol")):
    """Compare metrics across networks for a token."""
    try:
        network_comparison = network_config.compare_networks(token)
        return {
            "token": token,
            "networks": network_comparison,
            "count": len(network_comparison),
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error comparing networks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gas/prices")
async def get_gas_prices():
    """Get gas prices across all networks."""
    try:
        gas_prices = gas_estimator.compare_gas_prices()
        return {
            "gas_prices": gas_prices,
            "count": len(gas_prices),
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error getting gas prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gas/network/{network_id}")
async def get_network_gas_price(network_id: str):
    """Get gas price for a specific network."""
    try:
        gas_data = gas_estimator.get_gas_price(network_id)
        network_info = network_config.get_network(network_id)
        
        if not network_info:
            raise HTTPException(status_code=404, detail=f"Network {network_id} not found")
            
        return {
            "network": network_id,
            "name": network_info.get("name", ""),
            "gas_data": gas_data,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error getting gas price for {network_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bridging/estimate")
async def estimate_bridging_costs(
    from_network: str = Query(..., title="Source Network"),
    to_network: str = Query(..., title="Target Network"),
    amount: float = Query(1.0, title="Token Amount")
):
    """Estimate costs for bridging tokens between networks."""
    try:
        costs = network_config.estimate_bridging_costs(from_network, to_network, amount)
        return costs
    except Exception as e:
        logger.error(f"Error estimating bridging costs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/arbitrage/opportunities")
async def get_arbitrage_opportunities(token: str = Query("ETH", title="Token Symbol")):
    """Get arbitrage opportunities for a specific token."""
    try:
        opportunities = arbitrage.analyze_price_differences(token)
        return {
            "token": token,
            "opportunities": opportunities,
            "count": len(opportunities),
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error getting arbitrage opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/arbitrage/strategies")
async def get_arbitrage_strategies():
    """Get arbitrage strategies across multiple tokens."""
    try:
        strategies = arbitrage.get_arbitrage_strategies()
        return {
            "strategies": strategies,
            "count": len(strategies),
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error getting arbitrage strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class LiquidationRequest(BaseModel):
    collateral_token: str = Field(..., description="Token used as collateral")
    collateral_amount: float = Field(..., description="Amount of collateral token")
    debt_token: str = Field(..., description="Borrowed token")
    debt_amount: float = Field(..., description="Amount of borrowed token")

@app.post("/api/liquidation/price")
async def calculate_liquidation_price(request: LiquidationRequest):
    """Calculate liquidation price for a position."""
    try:
        liquidation_data = liquidation.calculate_liquidation_price(
            request.collateral_token,
            request.collateral_amount,
            request.debt_token,
            request.debt_amount
        )
        return liquidation_data
    except Layer2TradingException as e:
        logger.error(f"Layer2 trading error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating liquidation price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class BorrowableRequest(BaseModel):
    collateral_token: str = Field(..., description="Token used as collateral")
    collateral_amount: float = Field(..., description="Amount of collateral token")
    borrow_token: str = Field(..., description="Token to borrow")
    buffer_percent: float = Field(20.0, description="Safety buffer percentage")

@app.post("/api/liquidation/borrowable")
async def calculate_max_borrowable(request: BorrowableRequest):
    """Calculate maximum borrowable amount."""
    try:
        borrowable_data = liquidation.calculate_max_borrowable(
            request.collateral_token,
            request.collateral_amount,
            request.borrow_token,
            request.buffer_percent
        )
        return borrowable_data
    except Layer2TradingException as e:
        logger.error(f"Layer2 trading error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating max borrowable: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimizer/network")
async def recommend_network(
    token: str = Query(..., title="Token Symbol"),
    transaction_type: str = Query(..., title="Transaction Type"),
    amount: float = Query(1.0, title="Transaction Amount")
):
    """Recommend the best network for a specific transaction."""
    try:
        recommendation = trading_optimizer.recommend_network(token, transaction_type, amount)
        return recommendation
    except Exception as e:
        logger.error(f"Error recommending network: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimizer/path")
async def find_best_path(
    from_token: str = Query(..., title="From Token"),
    to_token: str = Query(..., title="To Token"),
    amount: float = Query(1.0, title="Amount")
):
    """Find best path for cross-network token exchange."""
    try:
        path = trading_optimizer.find_best_cross_network_path(from_token, to_token, amount)
        return path
    except Exception as e:
        logger.error(f"Error finding best path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/trading")
async def trading_websocket(websocket: WebSocket):
    """WebSocket endpoint for trading activities."""
    client_id = str(id(websocket))
    if await ws_server.connect(websocket, client_id):
        try:
            # Subscribe client to trading channel
            await ws_server.connection_manager.subscribe(client_id, 'trading')
            
            # Send initial trading data
            await websocket.send_json({
                'type': 'trading_update',
                'data': {
                    'status': 'ready',
                    'timestamp': asyncio.get_event_loop().time()
                }
            })
            
            # Listen for client messages
            while True:
                message = await websocket.receive_json()
                await ws_server.handle_message(client_id, message)
        except WebSocketDisconnect:
            await ws_server.disconnect(client_id)
        except Exception as e:
            logger.error(f"Error in trading websocket: {str(e)}")
            await ws_server.disconnect(client_id)

@app.websocket("/ws/arbitrage")
async def arbitrage_websocket(websocket: WebSocket):
    """WebSocket endpoint for arbitrage opportunities."""
    client_id = str(id(websocket))
    if await ws_server.connect(websocket, client_id):
        try:
            # Send initial arbitrage data
            strategies = arbitrage.get_arbitrage_strategies()
            await websocket.send_json({
                "type": "arbitrage_update",
                "data": {
                    "strategies": strategies,
                    "timestamp": asyncio.get_event_loop().time()
                }
            })
            
            # Listen for client messages
            while True:
                message = await websocket.receive_json()
                
                # Handle client requests for specific tokens
                if message.get("type") == "get_arbitrage":
                    token = message.get("token", "ETH")
                    try:
                        opportunities = arbitrage.analyze_price_differences(token)
                        await websocket.send_json({
                            "type": "arbitrage_update",
                            "data": {
                                "token": token,
                                "opportunities": opportunities,
                                "timestamp": asyncio.get_event_loop().time()
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error getting arbitrage for {token}: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "error": str(e)
                        })
                
                await asyncio.sleep(0.1)  # Prevent tight loop
                
        except WebSocketDisconnect:
            await ws_server.disconnect(client_id)
        except Exception as e:
            logger.error(f"Error in arbitrage websocket: {str(e)}")
            await ws_server.disconnect(client_id)

# Enhanced AI Consciousness Endpoints
@app.get("/api/ai/consciousness-state")
async def get_consciousness_state():
    """Get the current state of Rehoboam's consciousness layers."""
    try:
        consciousness_matrix = None
        if rehoboam and hasattr(rehoboam, 'consciousness'):
            consciousness_matrix = rehoboam.consciousness.tolist() if hasattr(rehoboam.consciousness, 'tolist') else rehoboam.consciousness
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "consciousness_matrix": consciousness_matrix,
            "active_modules": {
                "rehoboam_core": rehoboam is not None,
                "advanced_reasoning": reasoning_orchestrator is not None,
                "market_analyzer": market_analyzer is not None,
                "companion_creator": companion_creator is not None,
                "mcp_specialist": mcp_specialist is not None,
                "portfolio_optimizer": portfolio_optimizer is not None
            },
            "cognitive_capabilities": {
                "sentiment_analysis": rehoboam is not None,
                "strategy_generation": mcp_specialist is not None,
                "multi_model_reasoning": reasoning_orchestrator is not None,
                "companion_creation": companion_creator is not None,
                "portfolio_optimization": portfolio_optimizer is not None,
                "cross_chain_analysis": market_analyzer is not None
            },
            "consciousness_dimensions": [
                "analysis", "adaptation", "learning", "risk_assessment", "optimality"
            ] if consciousness_matrix else []
        }
        
        return state
        
    except Exception as e:
        logger.error(f"Error getting consciousness state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/reason")
async def advanced_reasoning(prompt: str, task_type: str = "general", complexity: int = 5):
    """Use Rehoboam's advanced multi-model reasoning capabilities."""
    try:
        if not reasoning_orchestrator:
            raise HTTPException(status_code=503, detail="Advanced reasoning module not available")
        
        # Create a model request
        from utils.advanced_reasoning import ModelRequest
        request = ModelRequest(
            prompt=prompt,
            task_type=task_type,
            complexity=complexity
        )
        
        # Process the request through the orchestrator
        response = await reasoning_orchestrator.process_request(request)
        
        return {
            "request_id": request.id,
            "response": response.to_dict() if response else None,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "complexity": complexity
        }
        
    except Exception as e:
        logger.error(f"Error in advanced reasoning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/market-intelligence/{token}")
async def get_market_intelligence(token: str):
    """Get comprehensive market intelligence using Rehoboam's consciousness."""
    try:
        if not market_analyzer:
            raise HTTPException(status_code=503, detail="Market analyzer module not available")
        
        # Use the real market analyzer
        intelligence = await market_analyzer.analyze_token(token)
        
        # Add consciousness layer analysis if available
        if rehoboam:
            consciousness_analysis = await rehoboam.analyze_sentiment(token, intelligence)
            intelligence["consciousness_sentiment"] = consciousness_analysis
        
        return intelligence
        
    except Exception as e:
        logger.error(f"Error getting market intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/mcp-function")
async def execute_mcp_function(function_name: str, parameters: Dict[str, Any]):
    """Execute an MCP function using the enhanced specialist."""
    try:
        if not mcp_specialist:
            raise HTTPException(status_code=503, detail="MCP specialist module not available")
        
        # Execute the MCP function
        result = await mcp_specialist.execute_function(function_name, parameters)
        
        return {
            "function_name": function_name,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error executing MCP function: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Etherscan Blockchain Analysis Endpoints

@app.post("/api/blockchain/analyze-wallet")
async def analyze_wallet_behavior(address: str, transaction_limit: int = 200):
    """
    Analyze wallet behavior using Etherscan data.
    
    Provides comprehensive insights into wallet patterns, trading behavior,
    and potential risks or opportunities.
    """
    try:
        if not trading_agent:
            raise HTTPException(status_code=503, detail="Trading agent not available")
        
        logger.info(f"Analyzing wallet behavior for {address}")
        
        # Validate Ethereum address format (basic check)
        if not address.startswith('0x') or len(address) != 42:
            raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
        
        result = trading_agent.analyze_wallet_behavior(address, transaction_limit)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "success": True,
            "address": address,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing wallet behavior: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/blockchain/detect-mev")
async def detect_mev_opportunities(address: str):
    """
    Detect MEV (Maximal Extractable Value) opportunities and patterns.
    
    Identifies potential MEV extraction opportunities and protection strategies.
    """
    try:
        if not trading_agent:
            raise HTTPException(status_code=503, detail="Trading agent not available")
        
        logger.info(f"Detecting MEV opportunities for {address}")
        
        # Validate Ethereum address format
        if not address.startswith('0x') or len(address) != 42:
            raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
        
        result = trading_agent.detect_mev_opportunities(address)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "success": True,
            "address": address,
            "mev_analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting MEV opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blockchain/intelligence/{address}")
async def get_blockchain_intelligence(address: str):
    """
    Get comprehensive blockchain intelligence for an address.
    
    Combines balance, transaction history, behavior analysis, and MEV detection
    into a single intelligence report.
    """
    try:
        if not trading_agent:
            raise HTTPException(status_code=503, detail="Trading agent not available")
        
        logger.info(f"Generating blockchain intelligence for {address}")
        
        # Validate Ethereum address format
        if not address.startswith('0x') or len(address) != 42:
            raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
        
        result = trading_agent.get_blockchain_intelligence(address)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "success": True,
            "address": address,
            "intelligence": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating blockchain intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blockchain/whale-activity")
async def monitor_whale_activity(min_value_eth: float = 1000.0):
    """
    Monitor whale activity for large transactions and market impact.
    
    Helps anticipate market movements based on large player activity.
    """
    try:
        if not trading_agent:
            raise HTTPException(status_code=503, detail="Trading agent not available")
        
        logger.info(f"Monitoring whale activity (min value: {min_value_eth} ETH)")
        
        result = trading_agent.monitor_whale_activity(min_value_eth)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "success": True,
            "whale_analysis": result,
            "min_value_eth": min_value_eth,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error monitoring whale activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/blockchain/analyze-contract")
async def analyze_contract_security(contract_address: str):
    """
    Analyze smart contract security and potential risks.
    
    Provides insights into contract safety before interactions.
    """
    try:
        if not trading_agent:
            raise HTTPException(status_code=503, detail="Trading agent not available")
        
        logger.info(f"Analyzing contract security for {contract_address}")
        
        # Validate Ethereum address format
        if not contract_address.startswith('0x') or len(contract_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid contract address format")
        
        result = trading_agent.analyze_contract_security(contract_address)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "success": True,
            "contract_address": contract_address,
            "security_analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing contract security: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handling
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "success": False,
        "error": {
            "message": "Internal server error",
            "detail": str(exc)
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting API server on http://0.0.0.0:5002")
    # Using port 5002 to avoid conflict with Simple Server on port 5000
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=5002, 
        reload=False,  # Disable reload to avoid multiple instances
        log_level="info"
    )