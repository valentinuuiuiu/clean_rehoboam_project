"""Test WebSocket transaction monitoring"""
import asyncio
from utils.wallet_utils import TransactionMonitor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def tx_callback(tx_data: dict) -> None:
    """Simple transaction callback"""
    logger.info(f"New transaction: {tx_data}")

async def main():
    monitor = TransactionMonitor("wss://ethereum.publicnode.com")
    logger.info("Starting transaction monitor...")
    try:
        await monitor.watch_transactions(tx_callback)
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")

if __name__ == "__main__":
    asyncio.run(main())