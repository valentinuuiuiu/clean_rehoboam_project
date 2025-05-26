"""Rate limiter implementation with token bucket algorithm."""
import time
from typing import Dict, Optional
from dataclasses import dataclass
import threading
import logging

logger = logging.getLogger(__name__)

@dataclass
class TokenBucket:
    capacity: float
    rate: float
    tokens: float = 0.0
    last_update: float = time.time()
    
    def update(self):
        now = time.time()
        time_passed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + time_passed * self.rate)
        self.last_update = now

class RateLimiter:
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()
        
        # Default configurations for different services
        self.default_configs = {
            'chainlink': {'capacity': 30, 'rate': 1},    # 30 requests per second
            'coingecko': {'capacity': 10, 'rate': 0.5},  # 10 requests per 2 seconds
            'binance': {'capacity': 20, 'rate': 1},      # 20 requests per second
            'etherscan': {'capacity': 5, 'rate': 0.2},   # 5 requests per 5 seconds
            'default': {'capacity': 5, 'rate': 0.2}      # 5 requests per 5 seconds
        }

    def configure_limit(self, key: str, capacity: float, rate: float):
        """Configure rate limit for a specific service."""
        with self._lock:
            self.buckets[key] = TokenBucket(capacity=capacity, rate=rate)
        logger.info(f"Configured rate limit for {key}: {capacity} requests at {rate}/s")

    def try_acquire(self, key: str, tokens: float = 1.0) -> bool:
        """Try to acquire tokens from the bucket."""
        with self._lock:
            if key not in self.buckets:
                config = self.default_configs.get(key, self.default_configs['default'])
                self.configure_limit(key, **config)
                
            bucket = self.buckets[key]
            bucket.update()
            
            if bucket.tokens >= tokens:
                bucket.tokens -= tokens
                return True
                
            return False

    def get_wait_time(self, key: str, tokens: float = 1.0) -> float:
        """Calculate wait time until tokens are available."""
        with self._lock:
            if key not in self.buckets:
                config = self.default_configs.get(key, self.default_configs['default'])
                self.configure_limit(key, **config)
                
            bucket = self.buckets[key]
            bucket.update()
            
            if bucket.tokens >= tokens:
                return 0.0
                
            return (tokens - bucket.tokens) / bucket.rate

    async def acquire(self, key: str, tokens: float = 1.0):
        """Acquire tokens, waiting if necessary."""
        import asyncio
        
        while True:
            if self.try_acquire(key, tokens):
                return
            
            wait_time = self.get_wait_time(key, tokens)
            await asyncio.sleep(wait_time)

# Global rate limiter instance
rate_limiter = RateLimiter()

# Create specific limiter instances for different services
etherscan_limiter = rate_limiter
