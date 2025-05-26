#!/usr/bin/env python
"""
Test script for the Model Context Protocol-based market sentiment analysis
"""

import os
import asyncio
import logging
import argparse
import sys
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MCP-Test")

# Import the sentiment analyzer
from utils.market_sentiment_mcp import MarketSentimentMCP
from utils.web_data import WebDataFetcher

async def test_sentiment_analysis(token: str):
    """Test sentiment analysis for a specific token."""
    logger.info(f"Testing MCP sentiment analysis for {token}...")
    
    # Get current price for context
    web_data = WebDataFetcher()
    price = web_data.get_crypto_price(token)
    price_change = web_data.get_24h_change(token)
    
    logger.info(f"Current {token} price: ${price:.2f} ({price_change:.2f}%)")
    
    # Initialize the MCP sentiment analyzer
    mcp_url = os.environ.get("MCP_URL", "http://localhost:3000/v1/chat")
    sentiment_analyzer = MarketSentimentMCP(mcp_url=mcp_url)
    
    try:
        # Test the analysis
        sentiment_data = await sentiment_analyzer.analyze_token_sentiment(token)
        
        # Print the results
        logger.info(f"MCP Sentiment Analysis Results for {token}:")
        logger.info(f"Score: {sentiment_data.get('score', 0):.2f}")
        logger.info(f"Mood: {sentiment_data.get('mood', 'unknown')}")
        logger.info(f"Confidence: {sentiment_data.get('confidence', 0):.2f}")
        
        if 'factors' in sentiment_data:
            logger.info(f"Key factors:")
            for factor in sentiment_data['factors']:
                logger.info(f"  - {factor}")
        
        if 'social_sentiment' in sentiment_data:
            logger.info(f"Social sentiment: {sentiment_data['social_sentiment']}")
        
        return sentiment_data
    except Exception as e:
        logger.error(f"Error testing MCP sentiment analysis: {str(e)}")
        return {"error": str(e)}

async def test_multiple_tokens(tokens: List[str]):
    """Test sentiment analysis for multiple tokens."""
    results = {}
    for token in tokens:
        result = await test_sentiment_analysis(token)
        results[token] = result
        
        # Add a small delay between tests
        await asyncio.sleep(1)
    
    return results

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test MCP-based market sentiment analysis")
    parser.add_argument("--token", default="ETH", help="Token to analyze (default: ETH)")
    parser.add_argument("--all", action="store_true", help="Analyze all major tokens")
    args = parser.parse_args()
    
    if args.all:
        # Test multiple major tokens
        tokens = ["BTC", "ETH", "LINK", "SOL", "MATIC", "AAVE", "UNI"]
        await test_multiple_tokens(tokens)
    else:
        # Test a single token
        await test_sentiment_analysis(args.token)

if __name__ == "__main__":
    asyncio.run(main())