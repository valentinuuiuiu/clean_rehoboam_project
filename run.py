"""Main entry point for the trading platform."""
from trading_platform import app, socketio

if __name__ == '__main__':
    # Start Flask app with SocketIO support
    socketio.run(app, 
                host='0.0.0.0',
                port=5000,
                debug=True,
                use_reloader=True,
                allow_unsafe_werkzeug=True)  # Only for development