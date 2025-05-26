"""Trading Platform Flask Application with WebSocket support."""
import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

# Import global state
from .state import (
    trading_agents,
    market_data,
    user_sessions,
    websocket_connections
)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'rehoboam-trading-platform-secret')
    
    # Enable CORS for all origins
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    return app

# Create Flask app and SocketIO instance
app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Import routes after app creation to avoid circular imports
from . import routes
from . import websocket_handlers

__all__ = ['app', 'socketio']
