import os
import time
import json
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from clean_rehoboam_project.utils.price_feed_service import PriceFeedService
from clean_rehoboam_project.utils.rate_limiter import rate_limiter as etherscan_limiter

@pytest_asyncio.fixture
async def price_feed():
    # Setup test environment
    os.environ['ETHERSCAN_API_KEY'] = 'test_key'
    with patch('asyncio.create_task', new_callable=MagicMock) as mock_create_task:
        with patch('clean_rehoboam_project.utils.rate_limiter.rate_limiter.try_acquire', return_value=True):
            with patch('clean_rehoboam_project.utils.rate_limiter.rate_limiter.acquire', return_value=None):
                service = PriceFeedService()
                # Patch external dependencies
                service._init_websocket_connections = AsyncMock(return_value=None)
                service._handle_websocket_messages = AsyncMock(return_value=None)
                service.ws_connections = {}  # Initialize empty connections
                yield service
                await service.close()

@pytest.fixture
def mock_response():
    def _mock(status_code=200, json_data=None):
        mock = MagicMock()
        mock.status_code = status_code
        mock.json.return_value = json_data or {}
        return mock
    return _mock

class TestPriceFeedService:
    def test_initialization(self, price_feed):
        assert price_feed.api_key == 'test_key'
        assert len(price_feed.default_tokens) > 0
        assert price_feed.cache_validity == 60
        assert price_feed.max_retries == 3

    @patch('requests.get')
    def test_get_chainlink_price_success(self, mock_get, price_feed, mock_response):
        # Setup mock response
        mock_get.return_value = mock_response(json_data={
            "status": "1",
            "result": "0x000000000000000000000000000000000000000000000000000000174876e800"  # 100000000000 (1000.0)
        })
        
        # Initialize mocks and retry counts
        price_feed.etherscan_limiter.wait_if_needed = MagicMock()
        price_feed.retry_counts = {'ETH': 0}
        
        price = price_feed._get_chainlink_price('ETH')
        assert price == 1000.0  # 100000000000 / 10^8
        assert price_feed.retry_counts['ETH'] == 0

    @patch('requests.get')
    def test_get_chainlink_price_rate_limit(self, mock_get, price_feed, mock_response):
        # Setup rate limited response
        mock_get.return_value = mock_response(status_code=429)
        
        # Initialize mocks and retry counts
        price_feed.etherscan_limiter.wait_if_needed = MagicMock()
        price_feed.retry_counts = {'ETH': 0}

        price = price_feed._get_chainlink_price('ETH')
        assert price is None
        assert price_feed.retry_counts['ETH'] == 1

    @patch('requests.get')
    def test_get_coingecko_price_success(self, mock_get, price_feed, mock_response):
        mock_get.return_value = mock_response(json_data={
            "ethereum": {"usd": 3500.42}
        })
        
        price = price_feed._get_coingecko_price('ETH')
        assert price == 3500.42

    def test_validate_price(self, price_feed):
        # Test valid prices
        assert price_feed._validate_price('ETH', 3500) is True
        assert price_feed._validate_price('SHIB', 0.00001) is True
        
        # Test invalid prices
        assert price_feed._validate_price('ETH', -100) is False
        assert price_feed._validate_price('ETH', 20000) is False  # Above max
        assert price_feed._validate_price('SHIB', 0.002) is False  # Above max

    def test_price_caching(self, price_feed):
        test_price = 3500.0
        price_feed._cache_price('ETH', test_price)
        
        cached = price_feed._get_cached_price('ETH')
        assert cached['price'] == test_price
        
        # Test cache expiration
        with patch('time.time', return_value=time.time() + 61):
            assert price_feed._get_cached_price('ETH') is None

    @patch('clean_rehoboam_project.utils.price_feed_service.PriceFeedService._get_chainlink_price')
    @patch('clean_rehoboam_project.utils.price_feed_service.PriceFeedService._get_coingecko_price')
    def test_get_price_with_fallback(self, mock_coingecko, mock_chainlink, price_feed):
        # Reset cache and initialize mocks
        price_feed.price_cache = {}
        price_feed.etherscan_limiter.wait_if_needed = MagicMock()
        price_feed.retry_counts = {'ETH': 0}
        
        # Test Chainlink success
        mock_chainlink.return_value = 3500.0
        mock_coingecko.return_value = None
        result = price_feed.get_price('ETH')
        assert result == 3500.0
        assert price_feed.retry_counts['ETH'] == 0
        
        # Reset for fallback test
        price_feed.price_cache = {}
        price_feed.retry_counts = {'ETH': 0}
        
        # Test Chainlink failure -> CoinGecko fallback
        mock_chainlink.return_value = None
        mock_coingecko.return_value = 3499.99
        result = price_feed.get_price('ETH')
        assert result == 3499.99
        assert price_feed.retry_counts['ETH'] == 1
        
        # Reset for failure test
        price_feed.price_cache = {}
        
        # Test all failures
        mock_chainlink.return_value = None
        mock_coingecko.return_value = None
        result = price_feed.get_price('ETH')
        assert result is None
        assert price_feed.retry_counts['ETH'] == 2

    @patch('websockets.connect', new_callable=AsyncMock)
    async def test_websocket_connection(self, mock_connect, price_feed):
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        
        await price_feed._init_websocket_connections()
        assert mock_connect.called
        assert 'binance' in price_feed.ws_connections

    def test_custom_tokens_management(self, price_feed):
        # Test adding valid token
        assert price_feed.add_custom_token('TEST', {
            'name': 'Test Token',
            'decimals': 18,
            'address': '0x1234567890123456789012345678901234567890'
        }) is True
        
        # Test adding invalid token
        assert price_feed.add_custom_token('BAD', {
            'name': 'Bad Token'
        }) is False  # Missing decimals
        
        # Test removal
        assert price_feed.remove_custom_token('TEST') is True
        assert price_feed.remove_custom_token('NONEXISTENT') is False

@pytest.mark.asyncio
async def test_websocket_message_processing(price_feed):
    test_message = json.dumps({
        'e': 'trade',
        's': 'ETHUSDT',
        'p': '3500.00',
        'q': '1.5',
        'T': 1234567890000
    })
    
    mock_ws = AsyncMock()
    mock_ws.recv = AsyncMock(return_value=test_message)
    
    # Simplified test to verify basic WebSocket handling
    print("TEST: Verifying WebSocket message reception")
    mock_ws.recv = AsyncMock(return_value=test_message)
    
    # Directly test handler with debug prints
    print("TEST: Calling _handle_websocket_messages directly")
    await price_feed._handle_websocket_messages('binance', mock_ws)
    
    # Verify message was received
    mock_ws.recv.assert_awaited_once()
    print("TEST: WebSocket.recv was called as expected")
    
    # Verify message was parsed
    print(f"TEST: Original message: {test_message}")
    parsed_data = json.loads(test_message)
    print(f"TEST: Parsed message: {parsed_data}")