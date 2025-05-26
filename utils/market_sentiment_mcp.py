"""
Market Sentiment Analysis using Model Context Protocol (MCP)

This module provides market sentiment analysis using the MCP protocol,
allowing us to use self-hosted language models for sentiment analysis
instead of relying on external APIs. When MCP is unavailable, it falls back
to RehoboamAI (DeepSeek API) and then to a basic rule-based approach.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta

# Import the MCP client from orbit package
from orbit import MCPClient

# Import market data utilities
from utils.web_data import WebDataFetcher

# Import RehoboamAI for fallback to DeepSeek API
from utils.rehoboam_ai import RehoboamAI

logger = logging.getLogger(__name__)

class MarketSentimentMCP:
    """Market sentiment analyzer using Model Context Protocol for self-hosted inference."""
    
    def __init__(self, mcp_url: Optional[str] = None, mcp_api_key: Optional[str] = None):
        """
        Initialize the market sentiment analyzer with MCP.
        
        Args:
            mcp_url: URL for the MCP server (defaults to environment variable or localhost)
            mcp_api_key: API key for the MCP server (defaults to environment variable)
        """
        # Set up MCP client
        self.mcp_url = mcp_url or os.environ.get("MCP_URL", "http://localhost:3000/v1/chat")
        self.mcp_api_key = mcp_api_key or os.environ.get("MCP_API_KEY")
        self.mcp_client = MCPClient(url=self.mcp_url, api_key=self.mcp_api_key)
        
        # Set up web data fetcher
        self.web_data = WebDataFetcher()
        
        # Initialize RehoboamAI for fallback
        self.rehoboam_ai = RehoboamAI(provider="deepseek", model="deepseek-chat")
        
        # Set up cache for sentiment analysis
        self.sentiment_cache = {}
        self.cache_duration = 1800  # 30 minutes
        
        logger.info("MarketSentimentMCP initialized with MCP endpoint: %s", self.mcp_url)
    
    async def analyze_token_sentiment(self, token: str) -> Dict[str, Any]:
        """
        Analyze market sentiment for a specific token using MCP with fallback options.
        
        Fallback chain:
        1. MCP Server
        2. DeepSeek API via RehoboamAI
        3. Basic rule-based approach
        
        Args:
            token: Token symbol to analyze (e.g., "ETH", "BTC")
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Check cache first
        cache_key = f"sentiment_{token}"
        if cache_key in self.sentiment_cache:
            cached_data = self.sentiment_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_duration:
                logger.debug(f"Using cached sentiment data for {token}")
                return cached_data["data"]
        
        # Gather market context for use across all methods
        market_data = self._gather_market_data(token)
        
        # Check if MCP server is available
        server_available = self.mcp_client.health_check()
        if not server_available:
            logger.warning("MCP server is not available. Trying DeepSeek API fallback.")
            return self._try_deepseek_fallback(token, market_data)
        
        try:
            # Construct market analysis text
            market_text = self._format_market_text(token, market_data)
            
            # Call MCP for sentiment analysis
            sentiment_data = self.mcp_client.sentiment_analysis(market_text, market_data)
            
            # Check for empty or error response
            if not sentiment_data or len(sentiment_data) == 0 or "error" in sentiment_data:
                logger.warning(f"Error or empty response in MCP sentiment analysis: {sentiment_data.get('error', 'Empty response')}")
                # Fall back to DeepSeek API
                return self._try_deepseek_fallback(token, market_data)
            else:
                # Cache successful results
                self.sentiment_cache[cache_key] = {
                    "timestamp": time.time(),
                    "data": sentiment_data
                }
                logger.info(f"Sentiment analysis for {token}: {sentiment_data.get('mood', 'unknown')}, " 
                           f"score: {sentiment_data.get('score', 0)}")
            
            return sentiment_data
            
        except Exception as e:
            logger.warning(f"Error in MCP sentiment analysis: {str(e)}")
            return self._try_deepseek_fallback(token, market_data)
    
    def _try_deepseek_fallback(self, token: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Try to use DeepSeek API via RehoboamAI as fallback.
        
        Args:
            token: Token symbol
            market_data: Market data dictionary
            
        Returns:
            Sentiment analysis results
        """
        try:
            # Check if we have a DeepSeek API key
            if self.rehoboam_ai.api_key:
                logger.info(f"Attempting DeepSeek API fallback for {token}")
                sentiment_data = self.rehoboam_ai.analyze_sentiment(token, market_data)
                
                # Normalize scores if using DeepSeek
                normalized_data = self._normalize_sentiment_data(sentiment_data)
                
                # Cache the result
                cache_key = f"sentiment_{token}"
                self.sentiment_cache[cache_key] = {
                    "timestamp": time.time(),
                    "data": normalized_data
                }
                
                logger.info(f"DeepSeek sentiment analysis for {token}: {normalized_data.get('mood', 'unknown')}, " 
                         f"score: {normalized_data.get('score', 0)}")
                
                return normalized_data
            else:
                logger.warning("No DeepSeek API key available. Using rule-based fallback.")
                return self._rule_based_sentiment_analysis(token, market_data)
                
        except Exception as e:
            logger.warning(f"Error in DeepSeek API fallback: {str(e)}")
            return self._rule_based_sentiment_analysis(token, market_data)
    
    def _gather_market_data(self, token: str) -> Dict[str, Any]:
        """
        Gather market data for sentiment analysis.
        
        Args:
            token: Token symbol
            
        Returns:
            Dictionary with market data
        """
        price_change = self.web_data.get_24h_change(token)
        volume = self.web_data.get_24h_volume(token)
        current_price = self.web_data.get_crypto_price(token)
        
        return {
            "token": token,
            "price": current_price,
            "change_24h": price_change,
            "volume_24h": volume,
            "timestamp": time.time()
        }
    
    def _format_market_text(self, token: str, market_data: Dict[str, Any]) -> str:
        """
        Format market data as text for MCP analysis.
        
        Args:
            token: Token symbol
            market_data: Market data dictionary
            
        Returns:
            Formatted text
        """
        market_text = f"Token: {token}\n"
        market_text += f"Current price: ${market_data.get('price', 'Unknown')}\n"
        market_text += f"24h price change: {market_data.get('change_24h', 'Unknown')}%\n"
        market_text += f"24h trading volume: ${market_data.get('volume_24h', 'Unknown')}\n\n"
        
        # Add news if available
        recent_news = self._get_recent_news(token)
        if recent_news:
            market_text += "Recent news:\n"
            for news_item in recent_news[:3]:
                market_text += f"- {news_item}\n"
                
        return market_text
    
    def _normalize_sentiment_data(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize sentiment data from different sources to a common format.
        
        Args:
            sentiment_data: Raw sentiment data
            
        Returns:
            Normalized sentiment data
        """
        # Create a normalized structure
        normalized = {
            "score": sentiment_data.get("score", 0),
            "mood": sentiment_data.get("mood", "neutral"),
            "factors": sentiment_data.get("factors", ["market data"]),
            "social_sentiment": sentiment_data.get("social_sentiment", "unknown"),
            "confidence": sentiment_data.get("confidence", 0.5)
        }
        
        # Ensure the score is in range [-1, 1]
        if normalized["score"] > 1.0:
            normalized["score"] = 1.0
        elif normalized["score"] < -1.0:
            normalized["score"] = -1.0
            
        # Ensure mood is one of the standard categories
        valid_moods = ["fearful", "cautious", "neutral", "optimistic", "euphoric"]
        if normalized["mood"] not in valid_moods:
            # Map to closest mood
            score = normalized["score"]
            if score < -0.6:
                normalized["mood"] = "fearful"
            elif score < -0.2:
                normalized["mood"] = "cautious"
            elif score < 0.2:
                normalized["mood"] = "neutral"
            elif score < 0.6:
                normalized["mood"] = "optimistic"
            else:
                normalized["mood"] = "euphoric"
                
        return normalized
    
    def _rule_based_sentiment_analysis(self, token: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rule-based sentiment analysis as final fallback.
        
        Args:
            token: Token symbol
            market_data: Market data dictionary
            
        Returns:
            Dictionary with basic sentiment analysis results
        """
        # Base sentiment on price change
        price_change = market_data.get('change_24h', 0)
        
        if price_change > 5:
            score = 0.8
            mood = "optimistic"
        elif price_change > 2:
            score = 0.6
            mood = "optimistic"
        elif price_change > 0:
            score = 0.2
            mood = "neutral"
        elif price_change > -2:
            score = -0.2
            mood = "cautious"
        elif price_change > -5:
            score = -0.6
            mood = "fearful"
        else:
            score = -0.8
            mood = "fearful"
        
        # Log fallback usage
        logger.info(f"Using fallback sentiment analysis for {token}: {mood}, score: {score}")
        
        return {
            "score": score,
            "mood": mood,
            "factors": ["price action", "market volatility"],
            "social_sentiment": "unknown",
            "confidence": 0.5
        }
    
    def _get_recent_news(self, token: str) -> List[str]:
        """
        Get recent news about the token (placeholder).
        
        This would normally fetch real news, but is a placeholder in this implementation.
        In a real implementation, you could use the web_data fetcher.
        
        Args:
            token: Token symbol
            
        Returns:
            List of recent news headlines
        """
        # This is a placeholder - in real implementation, fetch from news API or web
        return []