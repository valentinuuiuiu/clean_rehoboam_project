import pytest
from utils.web_data import WebDataFetcher
import time

class TestDDGIntegration:
    @pytest.fixture
    def fetcher(self):
        return WebDataFetcher()
        
    def test_ddg_price_fetch(self, fetcher):
        """Test DDG price fetching functionality"""
        # Test with a major cryptocurrency
        price = fetcher._fetch_ddg_price("BTC")
        assert price is not None
        assert 1000 < price < 1000000  # Reasonable BTC price range
        
    def test_price_verification_with_ddg_fallback(self, fetcher):
        """Test price verification using DDG as fallback"""
        # Test with known price range
        current_eth_price = 3500  # Example ETH price
        is_valid = fetcher.verify_price_feed("ETH", current_eth_price, tolerance=0.15)
        assert is_valid == True
        
        # Test with obviously wrong price
        wrong_price = 1  # Unrealistic ETH price
        is_valid = fetcher.verify_price_feed("ETH", wrong_price, tolerance=0.15)
        assert is_valid == False
        
    def test_ddg_rate_limiting(self, fetcher):
        """Test DDG rate limiting behavior with caching"""
        # First request should populate cache
        initial_price = fetcher._fetch_ddg_price("ETH")
        assert initial_price is not None, "Initial price fetch should succeed"
        
        # Subsequent requests should use cache
        prices = []
        for _ in range(3):
            price = fetcher._fetch_ddg_price("ETH")
            prices.append(price)
            time.sleep(0.2)  # Slightly longer delay between requests
            
        # All prices should be valid due to caching
        assert all(p is not None for p in prices), "Cached requests should always return prices"
        
        # All prices should be identical since they come from cache
        assert all(p == initial_price for p in prices), "Cached prices should be consistent"
