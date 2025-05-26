import requests
import re
import time
import json
import random
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from utils.logging_config import setup_logging

logger = setup_logging()

class ChainlinkFeedFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.feed_cache_file = 'chainlink_feeds.json'
        self.cache = {}  # In-memory cache for DDG search results
        self.last_request_time = time.time() - 3600  # Initialize last request time
        self.cache_duration = 3600  # Cache DDG results for 1 hour
        self.known_feeds = {
            'ETH/USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
            'BTC/USD': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
            'LINK/USD': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c'
        }

    def search_ddg_for_feed(self, pair: str) -> Optional[str]:
        """Search DuckDuckGo for Chainlink price feed address using enhanced parsing"""
        try:
            # Check cache first
            cache_key = f"ddg_feed_{pair}"
            if hasattr(self, 'cache') and cache_key in self.cache:
                logger.info(f"Using cached feed address for {pair}")
                return self.cache[cache_key]

            # Format search query for better results
            query = f"site:data.chain.link {pair} chainlink price feed ethereum mainnet"
            url = "https://html.duckduckgo.com/html/"
            params = {'q': query}
            
            # Implement rate limiting
            if hasattr(self, 'last_request_time'):
                time_since_last = time.time() - self.last_request_time
                if time_since_last < 3.0:  # 3 second minimum between requests
                    base_sleep = 3.0 - time_since_last
                    jitter = random.uniform(0, 0.5)  # Add 0-0.5s random jitter
                    sleep_time = base_sleep + jitter
                    logger.info(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
            self.last_request_time = time.time()
            
            # Make request with retries and exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code == 429:  # Too Many Requests
                        backoff = min(300, (2 ** attempt) + random.uniform(0, 0.5))
                        logger.warning(f"Rate limit exceeded, implementing backoff for {backoff:.2f}s")
                        time.sleep(backoff)
                        continue
                    elif response.status_code in [500, 502, 503, 504]:  # Server errors
                        backoff = min(60, (2 ** attempt) + random.uniform(0, 0.5))
                        logger.warning(f"Server error {response.status_code}, retrying in {backoff:.2f}s")
                        time.sleep(backoff)
                        continue
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(1)
                    
            # Use BeautifulSoup for better HTML parsing
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # First look in the most relevant areas (result titles and snippets)
            results = soup.select('.result__title, .result__snippet')
            found_addresses = set()
            
            for result in results:
                text = result.get_text()
                # Look for Ethereum addresses in the response
                matches = re.findall(r'0x[a-fA-F0-9]{40}', text)
                found_addresses.update(matches)
            
            # Also check full page content for any missed addresses
            full_text = soup.get_text()
            matches = re.findall(r'0x[a-fA-F0-9]{40}', full_text)
            found_addresses.update(matches)
            
            # Verify each found address
            for address in found_addresses:
                if self.verify_feed_contract(address):
                    logger.info(f"Found valid price feed for {pair}: {address}")
                    # Cache the result
                    self.known_feeds[pair] = address
                    return address
            
            logger.warning(f"No valid feed found for {pair}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error searching for feed {pair}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching for feed {pair}: {str(e)}")
            return None
            
    def verify_feed_contract(self, address: str) -> bool:
        """Basic verification of a potential feed contract"""
        try:
            # Chainlink feeds typically have these methods
            methods = ['latestAnswer', 'decimals', 'description']
            
            # You would normally verify this using web3, but for now just check format
            if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
                return False
                
            # Check if address is in known good feeds
            if address.lower() in [addr.lower() for addr in self.known_feeds.values()]:
                return True
                
            # Simple length and prefix check
            if len(address) != 42 or not address.startswith('0x'):
                return False
                
            # Check if address appears in known good format ranges
            if int(address[2:], 16) < 100:  # Suspiciously low address number
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error verifying feed contract: {str(e)}")
            return False
            
    def find_all_feeds(self) -> Dict[str, str]:
        """Find price feed addresses for common trading pairs"""
        pairs = [
            'ETH/USD', 'BTC/USD', 'LINK/USD', 'AAVE/USD',
            'UNI/USD', 'SNX/USD', 'SUSHI/USD'
        ]
        
        # Load existing cache
        try:
            with open(self.feed_cache_file, 'r') as f:
                feeds = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            feeds = {}
            
        # Start with known good feeds
        feeds.update(self.known_feeds)
        
        for pair in pairs:
            if pair not in feeds:
                logger.info(f"Searching for {pair} price feed...")
                address = self.search_ddg_for_feed(pair)
                if address:
                    feeds[pair] = address
                time.sleep(0.1)  # Minimal delay between requests
                
        # Cache results
        with open(self.feed_cache_file, 'w') as f:
            json.dump(feeds, f, indent=2)
            
        return feeds
