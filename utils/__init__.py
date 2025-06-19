# Empty init file to make the utils directory a Python package
from .websocket_server import EnhancedWebSocketServer as WebSocketServer # Alias to match expected import
from .rehoboam_ai import RehoboamAI
from .network_config import network_config # Import the instance directly
from .web_data import WebDataFetcher
from .arbitrage_service import arbitrage_service # Assuming this is an initialized instance
# Add other important classes/functions you want to expose from the 'utils' package directly
# For example, if Layer2GasEstimator, etc., are classes:
# from .layer2_trading import Layer2GasEstimator, Layer2Liquidation, Layer2TradingOptimizer
# If they are instances, they should be initialized somewhere and then imported if needed globally.
# For now, only adding what api_server.py directly tries to import from 'utils'.

# To avoid circular dependencies if modules within utils import from __init__ itself,
# be careful or use more specific imports in those modules.
# For now, this should resolve the direct import in api_server.py.

# It seems api_server.py also does:
# from utils import web3_service
# This implies web3_service should also be importable from here.
# Let's assume web3_service.py defines a global instance named web3_service.
try:
    from .web3_service import web3_service
except ImportError as e:
    # This allows api_server to still import it if web3_service.py doesn't exist or has issues,
    # falling back to the mock defined in api_server if this path fails.
    # However, the original error was about WebSocketServer.
    print(f"INFO: Could not import web3_service from utils.web3_service: {e}") # Make it visible
    pass

# The error was "cannot import name 'WebSocketServer' from 'utils'",
# so the line for WebSocketServer is the primary fix.
# The other imports are based on the usage in api_server.py:
# from utils import (...)
#   WebSocketServer, RehoboamAI, network_config, WebDataFetcher, arbitrage_service
# from utils import web3_service
#
# This suggests these names should be available directly from the 'utils' package.
# RehoboamAI is in rehoboam_ai.py
# network_config is in network_config.py (and api_server seems to expect an instance)
# WebDataFetcher is in web_data.py
# arbitrage_service is in arbitrage_service.py (likely an instance)
# web3_service is in web3_service.py (likely an instance)

# Let's also add the other ones that api_server.py imports directly from 'utils'
# Note: If these files also have dependencies that are not installed,
# this might lead to further ModuleNotFoundErrors.
# Removing try-except to see the actual import error from layer2_trading
from .layer2_trading import Layer2GasEstimator, Layer2Liquidation, Layer2TradingOptimizer
# If api_server.py expects instances like:
# gas_estimator = Layer2GasEstimator()
# then just exposing the classes is fine.
# The current api_server.py does:
# gas_estimator = Layer2GasEstimator()
# So, exposing the class itself is correct.
# except ImportError as e:
#     print(f"CRITICAL: Failed to import L2 trading components from utils.layer2_trading: {e}")
#     pass # Keep it robust if layer2_trading isn't there yet
