import os
import time
import requests
import logging
import traceback
from typing import Dict, Optional, Union
from .rate_limiter import rate_limiter as etherscan_limiter
from datetime import datetime
from typing import List, Set, Tuple
import json
import re
import asyncio
import websockets
from typing import Callable
from .monitoring_config import MonitoringConfig
from .system_monitor import SystemMonitor

logger = logging.getLogger(__name__)

class PriceFeedService:
    def __init__(self):
        self.api_key = os.getenv('ETHERSCAN_API_KEY')
        if not self.api_key:
            raise ValueError("ETHERSCAN_API_KEY environment variable is required")

        # Enhanced cache with token-specific timestamps and exponential backoff
        self.price_cache: Dict[str, Dict] = {}
        self.request_timestamps: Dict[str, float] = {}
        self.retry_counts: Dict[str, int] = {}
        self.backoff_times: Dict[str, float] = {}
        self.min_request_interval = 2.0  # 2 seconds between requests
        self.batch_interval = 0.5  # 500ms between batch requests
        self.max_retries = 5
        self.batch_size = 2  # Reduced batch size for better rate limit handling

        # Initialize request tracking with exponential backoff
        self.last_request_time = 0
        self.base_backoff = 1.0
        self.max_backoff = 16.0

        # Token configuration remains the same...
        self.default_tokens = {
            'ETH': {
                'address': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
                'decimals': 8,
                'min_price': 500,
                'max_price': 10000,
                'coingecko_id': 'ethereum',
                'networks': ['ethereum', 'arbitrum', 'polygon', 'avalanche']
            },
            'BTC': {
                'address': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
                'decimals': 8,
                'min_price': 10000,
                'max_price': 150000,
                'coingecko_id': 'bitcoin',
                'networks': ['ethereum', 'arbitrum', 'polygon', 'avalanche']
            },
            'MANA': {
                'address': '0x56a4857acbcfe3a66965c251628B1c9f1c408C19',
                'decimals': 8,
                'min_price': 0.1,
                'max_price': 10,
                'coingecko_id': 'decentraland',
                'networks': ['ethereum', 'polygon']
            },
            'XRP': {
                'address': '0xc26B0c2341b105551B3C4f410EEa2dB7cAb01f01',
                'decimals': 8,
                'min_price': 0.2,
                'max_price': 5,
                'coingecko_id': 'ripple',
                'networks': ['ethereum']
            },
            'XMR': {
                'address': None,  # Monero doesn't have a Chainlink feed
                'decimals': 8,
                'min_price': 50,
                'max_price': 1000,
                'coingecko_id': 'monero',
                'networks': ['ethereum']  # Will use CoinGecko fallback
            },
            'EAI': {
                'address': None,  # Using CoinGecko as primary source
                'decimals': 18,
                'min_price': 0.01,
                'max_price': 100,
                'coingecko_id': 'eternal-ai',
                'networks': ['ethereum']
            },
            'LINK': {
                'address': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',
                'decimals': 8,
                'min_price': 5,
                'max_price': 100,
                'coingecko_id': 'chainlink',
                'networks': ['ethereum', 'arbitrum', 'polygon', 'avalanche']
            },
            'DOT': {
                'address': '0x1C07AFb8E2B827c5A4739C6d59Ae3A5035f28734',
                'decimals': 8,
                'min_price': 3,
                'max_price': 100,
                'coingecko_id': 'polkadot',
                'networks': ['ethereum']  # DOT mainly on Ethereum via wrapped token
            },
            'MATIC': {
                'address': '0x7bAC85A8a13A4BcD8abb3eB7d6b4d632c5a57676',
                'decimals': 8,
                'min_price': 0.1,
                'max_price': 5,
                'coingecko_id': 'matic-network',
                'networks': ['ethereum', 'polygon']
            },
            'ARB': {
                'address': '0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6',
                'decimals': 8,
                'min_price': 0.1,
                'max_price': 50,
                'coingecko_id': 'arbitrum',
                'networks': ['ethereum', 'arbitrum']
            },
            'AVAX': {
                'address': '0xFF3EEb22B5E3dE6e705b44749C2559d704923FD7',
                'decimals': 8,
                'min_price': 5,
                'max_price': 500,
                'coingecko_id': 'avalanche-2',
                'networks': ['ethereum', 'avalanche']
            },
            'DOT': {
                'address': '0x1C07AFb8E2B827c5A4739C6d59Ae3A5035f28734',  # Chainlink DOT/USD feed
                'decimals': 8,
                'min_price': 3,
                'max_price': 100,
                'coingecko_id': 'polkadot'
            },
            'SOL': {
                'address': '0x4ffC43a60e009B551865A93d232E33Fce9f01507',  # Chainlink SOL/USD feed
                'decimals': 8,
                'min_price': 20,
                'max_price': 500,
                'coingecko_id': 'solana'
            },
            'AVAX': {
                'address': '0xFF3EEb22B5E3dE6e705b44749C2559d704923FD7',  # Chainlink AVAX/USD feed
                'decimals': 8,
                'min_price': 5,
                'max_price': 500,
                'coingecko_id': 'avalanche-2'
            },
            'SHIB': {
                'address': '0x8dD1CD88F43aF196ae478e91b9F5E4Ac69A97C61',  # Chainlink SHIB/USD feed
                'decimals': 18,  # Chainlink feed uses 8 decimals for small values
                'min_price': 0.000000001,  # Adjusted for realistic SHIB prices
                'max_price': 0.001,
                'coingecko_id': 'shiba-inu'
            },
            'UMA': {
                'address': '0xf7d57c676ac2bc4997ca5d4d34adc0d72213d29',  # Chainlink UMA/USD feed
                'decimals': 8,
                'min_price': 0.1,
                'max_price': 100,
                'coingecko_id': 'uma'
            },
            'AMP': {
                'address': '0x8797ABc4641dE76342b8acE9C63e3301DC35e3d8',  # Chainlink AMP/USD feed
                'decimals': 8,
                'min_price': 0.001,  # Setting conservative price bounds
                'max_price': 1.0,
                'coingecko_id': 'amp-token',
                'networks': ['ethereum']  # AMP primarily on Ethereum
            },
        }

        # Load custom token configuration if exists
        self.custom_tokens = {}
        self.load_custom_tokens()

        # Initialize cache with longer validity
        self.cache_validity = 30  # Cache valid for 30 seconds

        self.ws_connections = {}
        self.price_subscribers: Set[Callable] = set()
        self.monitor = SystemMonitor()
        self.config = MonitoringConfig()
        
        # Price caching
        self.price_cache: Dict[str, Dict] = {}
        self.cache_validity = 60  # seconds
        self.retry_counts: Dict[str, int] = {}
        self.max_retries = 3
        
        # WebSocket endpoints
        self.ws_endpoints = {
            'binance': 'wss://stream.binance.com:9443/ws',
            'coinbase': 'wss://ws-feed.pro.coinbase.com',
        }
        
        # Initialize connections
        asyncio.create_task(self._init_websocket_connections())

    async def _init_websocket_connections(self):
        """Initialize WebSocket connections to multiple providers."""
        for provider, url in self.ws_endpoints.items():
            try:
                websocket = await websockets.connect(url)
                self.ws_connections[provider] = websocket
                asyncio.create_task(self._handle_websocket_messages(provider, websocket))
                logger.info(f"Connected to {provider} WebSocket feed")
            except Exception as e:
                logger.error(f"Failed to connect to {provider} WebSocket: {e}")

    async def _handle_websocket_messages(self, provider: str, websocket):
        """Handle incoming WebSocket messages."""
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                await self._process_price_update(provider, data)
        except Exception as e:
            logger.error(f"WebSocket error for {provider}: {e}")
            # Attempt to reconnect
            asyncio.create_task(self._reconnect_websocket(provider))

    async def _reconnect_websocket(self, provider: str):
        """Attempt to reconnect to WebSocket endpoint."""
        while True:
            try:
                url = self.ws_endpoints[provider]
                websocket = await websockets.connect(url)
                self.ws_connections[provider] = websocket
                asyncio.create_task(self._handle_websocket_messages(provider, websocket))
                logger.info(f"Reconnected to {provider} WebSocket feed")
                break
            except Exception as e:
                logger.error(f"Failed to reconnect to {provider}: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _process_price_update(self, provider: str, data: Dict):
        """Process incoming price update and notify subscribers."""
        try:
            # Extract price data based on provider format
            price_data = self._extract_price_data(provider, data)
            if not price_data:
                return

            # Update cache
            symbol = price_data['symbol']
            self.price_cache[symbol] = {
                'price': price_data['price'],
                'timestamp': time.time(),
                'provider': provider
            }

            # Monitor for significant price changes
            alert = self.monitor.monitor_price_change(symbol, price_data['price'])
            if alert:
                logger.warning(f"Price alert: {alert.message}")

            # Notify subscribers
            for callback in self.price_subscribers:
                try:
                    callback(symbol, price_data)
                except Exception as e:
                    logger.error(f"Error in price subscriber callback: {e}")

        except Exception as e:
            logger.error(f"Error processing price update from {provider}: {e}")

    def _extract_price_data(self, provider: str, data: Dict) -> Optional[Dict]:
        """Extract standardized price data from provider-specific format."""
        try:
            if provider == 'binance':
                if 'e' in data and data['e'] == 'trade':
                    return {
                        'symbol': data['s'],
                        'price': float(data['p']),
                        'volume': float(data['q']),
                        'timestamp': data['T'] / 1000
                    }
            elif provider == 'coinbase':
                if data['type'] == 'match':
                    return {
                        'symbol': data['product_id'].replace('-', ''),
                        'price': float(data['price']),
                        'volume': float(data['size']),
                        'timestamp': time.time()
                    }
            return None
        except Exception as e:
            logger.error(f"Error extracting price data: {e}")
            return None

    def subscribe_to_prices(self, callback: Callable[[str, Dict], None]):
        """Subscribe to real-time price updates."""
        self.price_subscribers.add(callback)
        return lambda: self.price_subscribers.remove(callback)

    def get_price(self, symbol: str) -> Optional[float]:
        """Get latest price with fallback mechanisms."""
        try:
            # Check cache first
            cached_data = self._get_cached_price(symbol)
            if cached_data:
                return cached_data['price']

            # If no cached price, try API endpoints
            price = self._get_rest_api_price(symbol)
            if price:
                self._cache_price(symbol, price)
                return price

            logger.warning(f"Failed to get price for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None

    def _get_cached_price(self, symbol: str) -> Optional[Dict]:
        """Get cached price if still valid."""
        if symbol in self.price_cache:
            cache_data = self.price_cache[symbol]
            if time.time() - cache_data['timestamp'] < self.cache_validity:
                return cache_data
        return None

    def _get_rest_api_price(self, symbol: str) -> Optional[float]:
        """Get price from REST API endpoints as fallback."""
        # Implementation of REST API calls to multiple providers
        # This serves as a fallback when WebSocket feeds fail
        pass

    def get_supported_symbols(self) -> List[str]:
        """Get list of supported trading symbols."""
        return list(self.price_cache.keys())

    async def close(self):
        """Close all WebSocket connections."""
        for provider, ws in self.ws_connections.items():
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"Error closing {provider} WebSocket: {e}")

    def _get_backoff_time(self, symbol: str) -> float:
        """Calculate exponential backoff time with jitter"""
        if symbol not in self.retry_counts:
            self.retry_counts[symbol] = 0
            self.backoff_times[symbol] = self.base_backoff

        retry_count = self.retry_counts[symbol]
        backoff = min(self.base_backoff * (2 ** retry_count), self.max_backoff)
        # Add random jitter (±20%)
        jitter = backoff * 0.2 * (2 * time.time() % 1 - 0.5)
        return backoff + jitter

    def _update_rate_limit_state(self, symbol: str, success: bool):
        """Update rate limiting state based on request success"""
        if success:
            self.retry_counts[symbol] = 0
            self.backoff_times[symbol] = self.base_backoff
        else:
            self.retry_counts[symbol] = self.retry_counts.get(symbol, 0) + 1
            self.backoff_times[symbol] = self._get_backoff_time(symbol)

    def _get_cached_price(self, symbol: str) -> Optional[Dict]:
        """Get cached price data if still valid, with enhanced validation"""
        if symbol in self.price_cache:
            cache_data = self.price_cache[symbol]
            cache_age = time.time() - cache_data['timestamp']

            # Use shorter cache time if we've had recent failures
            valid_time = self.cache_validity * (0.5 if self.retry_counts.get(symbol, 0) > 0 else 1.0)

            if cache_age < valid_time:
                logger.info(f"Using cached price for {symbol}, age: {cache_age:.1f}s")
                return cache_data
        return None

    def get_price(self, symbol: str) -> Optional[float]:
        """Get latest price with enhanced error handling and retries"""
        try:
            # Check cache first
            cached_data = self._get_cached_price(symbol)
            if cached_data:
                return cached_data['price']

            # Try Chainlink first if available
            if symbol in self.default_tokens and self.default_tokens[symbol].get('address'):
                price = self._get_chainlink_price(symbol)
                if price:
                    self._cache_price(symbol, price)
                    return price

            # Fallback to CoinGecko with retries
            for attempt in range(self.max_retries):
                try:
                    price = self._get_coingecko_price(symbol)
                    if price:
                        self._cache_price(symbol, price)
                        return price

                    backoff_time = self._get_backoff_time(symbol)
                    logger.info(f"Retrying {symbol} after {backoff_time:.1f}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(backoff_time)

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                    if attempt < self.max_retries - 1:
                        backoff_time = self._get_backoff_time(symbol)
                        time.sleep(backoff_time)

            logger.error(f"Failed to get price for {symbol} after {self.max_retries} attempts")
            return None

        except Exception as e:
            logger.error(f"Unexpected error getting price for {symbol}: {str(e)}")
            return None

    def _cache_price(self, symbol: str, price: float):
        """Cache price data with timestamp"""
        self.price_cache[symbol] = {
            'price': price,
            'timestamp': time.time()
        }

    def _get_chainlink_price(self, symbol: str) -> Optional[float]:
        """Get price from Chainlink feed with enhanced error handling"""
        if symbol not in self.default_tokens or not self.default_tokens[symbol].get('address'):
            return None

        address = self.default_tokens[symbol]['address']
        try:
            if not etherscan_limiter.wait_if_needed():
                logger.warning(f"Etherscan daily limit reached for {symbol}")
                return None

            url = "https://api.etherscan.io/api"
            params = {
                "module": "proxy",
                "action": "eth_call",
                "to": address,
                "data": "0x50d25bcd",  # latestAnswer() function signature
                "tag": "latest",
                "apikey": self.api_key
            }

            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 429:
                logger.warning(f"Rate limit reached for {symbol}")
                return None

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "0" and "Max rate limit reached" in str(data.get("result", "")):
                    logger.warning(f"Etherscan rate limit reached for {symbol}")
                    return None

                if "result" in data and data["result"] and data["result"] != "0x":
                    raw_price = int(data["result"], 16)
                    decimals = self.default_tokens[symbol].get('decimals', 8)
                    price = raw_price / (10 ** decimals)
                    if self._validate_price(symbol, price):
                        logger.info(f"Got Chainlink price for {symbol}: ${price:.8f}")
                        return float(price)
                    logger.warning(f"Invalid price from Chainlink for {symbol}")

            return None

        except Exception as e:
            logger.error(f"Chainlink price fetch failed for {symbol}: {str(e)}")
            return None

    def _get_coingecko_price(self, symbol: str) -> Optional[float]:
        """Get price from CoinGecko with enhanced error handling and rate limiting"""
        coingecko_id = self._get_coingecko_id(symbol)
        if not coingecko_id:
            return None

        try:
            current_time = time.time()
            if hasattr(self, '_last_coingecko_request'):
                time_since_last = current_time - self._last_coingecko_request
                if time_since_last < 2.0:  # Minimum 2 seconds between requests
                    time.sleep(2.0 - time_since_last)
            self._last_coingecko_request = current_time

            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coingecko_id,
                "vs_currencies": "usd",
                "precision": "full"
            }

            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Trading Bot/1.0'
            }

            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 429:
                logger.warning(f"CoinGecko rate limit reached for {symbol}, waiting and retrying")
                time.sleep(2)
                response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if coingecko_id in data and "usd" in data[coingecko_id]:
                    price = float(data[coingecko_id]["usd"])
                    if self._validate_price(symbol, price):
                        logger.info(f"Got CoinGecko price for {symbol}: ${price:.8f}")
                        return float(price)
                    logger.warning(f"Invalid price from CoinGecko for {symbol}")

            logger.error(f"Failed to get valid price from CoinGecko for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error fetching CoinGecko price for {symbol}: {str(e)}")
            return None

    def _get_coingecko_id(self, symbol: str) -> Optional[str]:
        """Map token symbols to CoinGecko IDs"""
        coingecko_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'LINK': 'chainlink',
            'DOT': 'polkadot',
            'SOL': 'solana',
            'AVAX': 'avalanche-2',
            'SHIB': 'shiba-inu',
            'ZKSYNC': 'zksync-2',
            'BASE': 'base',
            'MANA': 'decentraland',
            'XRP': 'ripple',
            'XMR': 'monero',
            'EAI': 'eternal-ai',
            'AMP': 'amp-token'
        }
        return coingecko_ids.get(symbol) or self.default_tokens.get(symbol, {}).get('coingecko_id')

    def _validate_price(self, symbol: str, price: float) -> bool:
        """Validate price with flexible ranges and special cases"""
        try:
            if not isinstance(price, (int, float)) or price <= 0:
                return False

            # Special handling for tokens with very small values
            if symbol == 'SHIB':
                return price > 0 and price < 0.001

            if symbol == 'AMP':
                return price > 0 and price < 1.0

            if symbol in ['MANA', 'XRP', 'EAI']:
                return price > 0 and price < 10.0

            if symbol == 'XMR':
                return price > 0 and price < 1000.0

            token_data = self.default_tokens.get(symbol)
            if not token_data:
                return price > 0

            # More flexible validation with 50% buffer on both sides
            min_price = token_data.get('min_price', 0) * 0.5
            max_price = token_data.get('max_price', float('inf')) * 1.5
            return min_price <= price <= max_price

        except Exception as e:
            logger.error(f"Error validating price for {symbol}: {str(e)}")
            return False

    def format_price(self, price: float, decimals: int = 8) -> float:
        """Format price with appropriate precision"""
        try:
            if not isinstance(price, (int, float)):
                return None
            # Return as float, not string
            if price < 0.000001:  # For extremely small values like SHIB
                return float(f"{price:.10f}")
            elif price < 0.0001:   # For very small values
                return float(f"{price:.8f}")
            elif price < 0.01:     # For small values
                return float(f"{price:.6f}")
            elif price < 1:        # For values less than 1
                return float(f"{price:.4f}")
            else:                 # For normal values
                return float(f"{price:.{min(decimals, 2)}f}")
        except Exception as e:
            logger.error(f"Error formatting price: {str(e)}")
            return None

    def load_custom_tokens(self):
        """Load custom token configurations from a file or database."""
        try:
            with open('custom_tokens.json', 'r') as f:
                self.custom_tokens = json.load(f)
        except FileNotFoundError:
            self.custom_tokens = {}
        except Exception as e:
            logger.error(f"Error loading custom tokens: {str(e)}")
            self.custom_tokens = {}

    def save_custom_tokens(self):
        """Save custom token configurations to file"""
        try:
            with open('custom_tokens.json', 'w') as f:
                json.dump(self.custom_tokens, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving custom tokens: {str(e)}")

    def add_custom_token(self, symbol: str, config: dict) -> bool:
        """Add or update a custom token configuration"""
        try:
            required_fields = ['name', 'decimals']
            if not all(field in config for field in required_fields):
                logger.error(f"Missing required fields for token {symbol}")
                return False

            # Validate configuration
            if 'address' in config and not re.match(r'^0x[a-fA-F0-9]{40}$', config['address']):
                logger.error(f"Invalid address format for token {symbol}")
                return False

            self.custom_tokens[symbol] = config
            self.save_custom_tokens()
            logger.info(f"Added custom token {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error adding custom token {symbol}: {str(e)}")
            return False

    def remove_custom_token(self, symbol: str) -> bool:
        """Remove a custom token configuration"""
        try:
            if symbol in self.custom_tokens:
                del self.custom_tokens[symbol]
                self.save_custom_tokens()
                logger.info(f"Removed custom token {symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing custom token {symbol}: {str(e)}")
            return False

    def get_supported_tokens(self) -> list:
        """Get list of all supported tokens"""
        return list(set(list(self.default_tokens.keys()) + list(self.custom_tokens.keys())))

    def get_all_prices(self) -> Dict[str, float]:
        """Get prices for all supported tokens"""
        prices = {}
        for symbol in self.default_tokens.keys():
            price = self.get_price(symbol)
            if price:
                prices[f"{symbol}-USD"] = price
        return prices

    def is_token_supported(self, symbol: str) -> bool:
        """Check if a token is supported"""
        return symbol in self.default_tokens or symbol in self.custom_tokens

    def _get_price_limits(self, symbol: str) -> Tuple[float, float]:
        """Get price limits for a given symbol."""
        token_data = self.default_tokens.get(symbol) or self.custom_tokens.get(symbol)
        if token_data:
            return token_data.get('min_price', 0), token_data.get('max_price', float('inf'))
        return 0, float('inf')

    def format_price(self, price: float, decimals: int = 8) -> float:
        """Format price as float with appropriate precision"""
        try:
            if not isinstance(price, (int, float)):
                return None
            # Return as float, not string
            if price < 0.000001:  # For extremely small values like SHIB
                return float(f"{price:.10f}")
            elif price < 0.0001:   # For very small values
                return float(f"{price:.8f}")
            elif price < 0.01:     # For small values
                return float(f"{price:.6f}")
            elif price < 1:        # For values less than 1
                return float(f"{price:.4f}")
            else:                 # For normal values
                return float(f"{price:.{min(decimals, 2)}f}")
        except Exception as e:
            logger.error(f"Error formatting price: {str(e)}")
            return None
            
        #Removed Redundant _can_make_request and _process_batch_updates functions as they are superseded by the enhanced retry and backoff mechanisms in the edited snippet.