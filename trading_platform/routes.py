"""Flask routes for the trading platform."""
from flask import request, jsonify, render_template_string
from . import app
from .state import trading_agents, market_data
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main index page."""
    return jsonify({
        "message": "Rehoboam Trading Platform API",
        "status": "active",
        "endpoints": {
            "/health": "Health check",
            "/market/status": "Market status",
            "/trading/agents": "Trading agents status"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "active_agents": len(trading_agents),
        "market_data_available": bool(market_data)
    })

@app.route('/market/status')
def market_status():
    """Get current market status."""
    return jsonify({
        "status": "active",
        "data": market_data,
        "timestamp": market_data.get('timestamp') if market_data else None
    })

@app.route('/trading/agents')
def trading_agents_status():
    """Get status of all trading agents."""
    agents_info = []
    for agent_id, agent in trading_agents.items():
        agents_info.append({
            "id": agent_id,
            "status": getattr(agent, 'status', 'unknown'),
            "last_activity": getattr(agent, 'last_activity', None)
        })
    
    return jsonify({
        "agents": agents_info,
        "total_count": len(trading_agents)
    })

@app.route('/api/test')
def api_test():
    """Test endpoint for API connectivity."""
    return jsonify({
        "message": "API is working correctly",
        "timestamp": market_data.get('timestamp') if market_data else "No market data"
    })
