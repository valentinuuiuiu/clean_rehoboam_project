import os
import logging
import time
from utils.price_feed_service import PriceFeedService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_price_feeds():
    """Test price feeds for all supported cryptocurrencies with enhanced error reporting"""
    print("\nTesting price feeds for all supported cryptocurrencies:")
    print("=" * 50)

    price_service = PriceFeedService()
    # Focus on our favorite tokens plus AMP
    symbols = ['MANA', 'EAI', 'XRP', 'XMR', 'AMP']
    results = {'success': [], 'failed': []}

    for symbol in symbols:
        try:
            print(f"\nFetching price for {symbol}...")
            start_time = time.time()
            price = price_service.get_price(symbol)

            if price is not None and isinstance(price, (int, float)):
                fetch_time = time.time() - start_time
                print(f"✅ {symbol}: ${float(price):.2f} (fetched in {fetch_time:.2f}s)")
                results['success'].append(symbol)
            else:
                print(f"❌ {symbol}: Failed to fetch price (None or invalid type returned)")
                results['failed'].append(symbol)

        except Exception as e:
            print(f"❌ Error fetching {symbol} price: {str(e)}")
            results['failed'].append(symbol)

    # Print summary
    print("\nTest Summary:")
    print("=" * 50)
    print(f"Successful: {len(results['success'])}/{len(symbols)} ({', '.join(results['success'])})")
    if results['failed']:
        print(f"Failed: {len(results['failed'])}/{len(symbols)} ({', '.join(results['failed'])})")
    print("=" * 50)

if __name__ == "__main__":
    test_price_feeds()