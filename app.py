"""Main application entry point."""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from trading_platform.state import State
from utils.websocket_server import EnhancedWebSocketServer

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def init_platform():
    """Initialize the trading platform."""
    ws_server = EnhancedWebSocketServer()
    state = State(ws_server)
    await state.initialize()
    return state

@app.on_event("startup")
async def startup_event():
    """Initialize application state on startup."""
    app.state.platform = await init_platform()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    if hasattr(app.state, "platform"):
        await app.state.platform.cleanup()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )