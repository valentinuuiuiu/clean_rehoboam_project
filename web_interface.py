import os
import sys
import time
import logging
import traceback
from typing import Dict, Optional
from datetime import datetime
import numpy as np
import pandas as pd
from utils.price_feed_service import PriceFeedService
from utils.logging_config import setup_logging

logger = setup_logging()

def format_market_data(data: dict) -> dict:
    """Format market data for frontend consumption"""
    try:
        return {
            'timestamp': datetime.fromtimestamp(data['time']/1000).isoformat(),
            'price': float(data['close']),
            'volume': float(data['volume']),
            'high': float(data['high']),
            'low': float(data['low']),
            'open': float(data['open'])
        }
    except Exception as e:
        logger.error(f"Error formatting market data: {str(e)}")
        return {}

def calculate_indicators(prices: list) -> Dict[str, float]:
    """Calculate technical indicators from price data"""
    try:
        if not prices:
            return {}

        prices = np.array(prices)
        return {
            'sma': float(np.mean(prices[-20:])),
            'ema': float(np.average(prices[-20:], weights=np.exp(np.linspace(-1., 0., 20)))),
            'std': float(np.std(prices[-20:]))
        }
    except Exception as e:
        logger.error(f"Error calculating indicators: {str(e)}")
        return {}


class TradingDashboard:
    def __init__(self):
        """Initialize the trading dashboard with enhanced price feeds"""
        try:
            self.logger = logging.getLogger(__name__)
            # Removed Flask and Dash initialization

            # Initialize price feed service
            self.price_service = PriceFeedService()

            # Get initial prices (this part remains largely unchanged)
            try:
                initial_prices = self.price_service.get_all_prices()
                self.logger.info(f"Initial prices loaded: {initial_prices}")
            except Exception as e:
                self.logger.error(f"Failed to get initial prices: {str(e)}")
                initial_prices = {}

            # Supported cryptocurrencies mapping (unchanged)
            self.supported_coins = {
                'ETH-USD': {
                    'name': 'Ethereum',
                    'symbol': 'ETH',
                    'default_price': 3000.00,
                    'min_price': 500,
                    'max_price': 10000,
                    'decimals': 2
                },
                'BTC-USD': {
                    'name': 'Bitcoin',
                    'symbol': 'BTC',
                    'default_price': 42000.00,
                    'min_price': 10000,
                    'max_price': 150000,
                    'decimals': 2
                },
                'LINK-USD': {
                    'name': 'Chainlink',
                    'symbol': 'LINK',
                    'default_price': 15.00,
                    'min_price': 5,
                    'max_price': 100,
                    'decimals': 2
                },
                'DOT-USD': {
                    'name': 'Polkadot',
                    'symbol': 'DOT',
                    'default_price': 9.00,
                    'min_price': 3,
                    'max_price': 100,
                    'decimals': 2
                },
                'SOL-USD': {
                    'name': 'Solana',
                    'symbol': 'SOL',
                    'default_price': 220.00,
                    'min_price': 20,
                    'max_price': 500,
                    'decimals': 2
                },
                'AVAX-USD': {
                    'name': 'Avalanche',
                    'symbol': 'AVAX',
                    'default_price': 35.00,
                    'min_price': 10,
                    'max_price': 200,
                    'decimals': 2
                },
                'SHIB-USD': {
                    'name': 'Shiba Inu',
                    'symbol': 'SHIB',
                    'default_price': 0.00001,
                    'min_price': 0.000000001,
                    'max_price': 0.001,
                    'decimals': 8
                },
                'UMA-USD': {
                    'name': 'UMA',
                    'symbol': 'UMA',
                    'default_price': 2.50,
                    'min_price': 0.5,
                    'max_price': 50,
                    'decimals': 2
                }
            }

            # Initialize market data structures (unchanged)
            self.market_cache = {pair: None for pair in self.supported_coins}
            self.market_cache_time = {pair: 0 for pair in self.supported_coins}
            self.base_prices = {}
            self.volatility = {pair: 0.0 for pair in self.supported_coins}
            self.trend = {pair: 'neutral' for pair in self.supported_coins}

            # Initialize prices with live or default values (unchanged)
            for pair, data in self.supported_coins.items():
                symbol = data['symbol']
                try:
                    if symbol in initial_prices and initial_prices[symbol] is not None:
                        price = initial_prices[symbol]
                        if self._validate_price(data, price):
                            self.base_prices[pair] = price
                            self.logger.info(f"Using live price for {pair}: ${price}")
                        else:
                            self.base_prices[pair] = data['default_price']
                            self.logger.warning(f"Invalid price for {pair}, using default: ${data['default_price']}")
                    else:
                        self.base_prices[pair] = data['default_price']
                        self.logger.warning(f"No live price for {pair}, using default: ${data['default_price']}")
                except Exception as e:
                    self.logger.error(f"Error setting price for {pair}: {str(e)}")
                    self.base_prices[pair] = data['default_price']

            # Removed layout and callback setup

        except Exception as e:
            self.logger.error(f"Error initializing dashboard: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _validate_price(self, token_data: dict, price: float) -> bool:
        """Validate price based on token-specific rules"""
        try:
            if price <= 0:
                return False

            # Special handling for SHIB and other small-value tokens
            if token_data['symbol'] == 'SHIB':
                return 0 < price < token_data['max_price']

            # Standard validation for other tokens
            return token_data['min_price'] <= price <= token_data['max_price']

        except Exception as e:
            self.logger.error(f"Error validating price: {str(e)}")
            return False

    def format_price(self, price: float, decimals: int) -> str:
        """Format price with appropriate decimal places and handling for very small values"""
        if price < 0.00001:  # For very small values like SHIB
            return f"${price:.8f}"
        elif price < 0.01:   # For small values
            return f"${price:.6f}"
        elif price < 1:      # For values less than 1
            return f"${price:.4f}"
        else:               # For normal values
            return f"${price:.{min(decimals, 2)}f}"

    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Run the dashboard server -  Placeholder,  No server to run."""
        try:
            self.logger.info(f"Dashboard functionality is now handled outside this script.")
            #Removed server run code
        except Exception as e:
            self.logger.error(f"Failed to start server: {str(e)}")
            raise


if __name__ == '__main__':
    try:
        dashboard = TradingDashboard()
        port = int(os.getenv('PORT', 5000))
        #Removed server start command.
        print("Data processing functions initialized. Frontend application ready to serve.")

    except Exception as e:
        logging.error(f"Application startup failed: {str(e)}")
        sys.exit(1)