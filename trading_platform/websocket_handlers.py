"""WebSocket event handlers for the trading platform."""
from datetime import datetime
from flask import request
from flask_socketio import emit
from . import socketio
from .state import websocket_connections, market_data

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connections."""
    client_id = request.sid
    websocket_connections[client_id] = {
        "connected_at": datetime.now().isoformat(),
        "subscription": []
    }
    
    emit('connection_success', {
        "status": "connected",
        "client_id": client_id,
        "server_time": datetime.now().isoformat()
    })
    
    print(f"Client connected: {client_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnections."""
    client_id = request.sid
    if client_id in websocket_connections:
        del websocket_connections[client_id]
    
    print(f"Client disconnected: {client_id}")

@socketio.on('subscribe_market_data')
def handle_market_data_subscription(data):
    """Handle subscriptions to market data updates."""
    client_id = request.sid
    tokens = data.get('tokens', [])
    
    if client_id in websocket_connections:
        websocket_connections[client_id]["subscription"] = tokens
        
        # Send initial data
        if tokens:
            filtered_data = {
                token: market_data.get(token, {})
                for token in tokens
                if token in market_data
            }
        else:
            filtered_data = market_data
            
        emit('market_data_update', {
            "status": "success",
            "data": filtered_data
        })
        
    print(f"Client {client_id} subscribed to: {tokens}")

@socketio.on('unsubscribe_market_data')
def handle_market_data_unsubscription(data):
    """Handle unsubscriptions from market data updates."""
    client_id = request.sid
    
    if client_id in websocket_connections:
        websocket_connections[client_id]["subscription"] = []
        
    print(f"Client {client_id} unsubscribed from market data")

# Background task to broadcast market data updates
def broadcast_market_data():
    """Broadcast market data updates to subscribed clients."""
    for client_id, connection in websocket_connections.items():
        tokens = connection.get("subscription", [])
        
        if tokens:
            filtered_data = {
                token: market_data.get(token, {})
                for token in tokens
                if token in market_data
            }
        else:
            filtered_data = market_data
            
        socketio.emit('market_data_update', {
            "status": "success",
            "data": filtered_data
        }, room=client_id)
