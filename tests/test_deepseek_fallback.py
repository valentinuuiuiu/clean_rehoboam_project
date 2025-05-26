"""
Test module for the RehoboamAI and DeepSeek integration.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock
from utils.rehoboam_ai import RehoboamAI
from utils.market_sentiment_mcp import MarketSentimentMCP
from orbit import MCPClient


class TestRehoboamAI:
    """Tests for the RehoboamAI module with DeepSeek integration."""
    
    def test_init(self):
        """Test initialization of RehoboamAI."""
        ai = RehoboamAI(provider="deepseek", model="deepseek-chat")
        assert ai.provider == "deepseek"
        assert ai.model == "deepseek-chat"
    
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"})
    def test_api_key_from_env(self):
        """Test that API key is loaded from environment variables."""
        ai = RehoboamAI(provider="deepseek", model="deepseek-chat")
        assert ai.api_key == "test-key"
    
    @patch("requests.post")
    def test_fallback_sentiment_analysis(self, mock_post):
        """Test the fallback sentiment analysis without API call."""
        ai = RehoboamAI(provider="deepseek", model="deepseek-chat")
        # Ensure API key is None to trigger fallback
        ai.api_key = None
        
        market_data = {
            "price": 3000,
            "change_24h": 2.5,
            "volume_24h": 1000000000
        }
        
        result = ai.analyze_sentiment("ETH", market_data)
        
        # Verify we got a fallback result without calling the API
        assert result["mood"] == "optimistic"
        assert result["score"] == 0.6
        assert mock_post.call_count == 0
    
    @patch("requests.post")
    def test_deepseek_api_call(self, mock_post):
        """Test the DeepSeek API call for sentiment analysis."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "score": 0.75,
                            "mood": "optimistic",
                            "factors": ["positive price action", "increasing volume"],
                            "social_sentiment": "positive",
                            "confidence": 0.85
                        })
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        ai = RehoboamAI(provider="deepseek", model="deepseek-chat")
        ai.api_key = "test-key"  # Ensure we have an API key
        
        market_data = {
            "price": 3000,
            "change_24h": 2.5,
            "volume_24h": 1000000000
        }
        
        result = ai.analyze_sentiment("ETH", market_data)
        
        # Verify we got the mocked API result
        assert result["mood"] == "optimistic"
        assert result["score"] == 0.75
        assert result["confidence"] == 0.85
        assert mock_post.call_count == 1


class TestMarketSentimentMCP:
    """Tests for the MarketSentimentMCP with DeepSeek fallback."""
    
    @patch.object(MCPClient, "health_check", return_value=False)
    @patch.object(RehoboamAI, "analyze_sentiment")
    def test_deepseek_fallback_when_mcp_unavailable(self, mock_analyze, mock_health):
        """Test that DeepSeek is used as fallback when MCP is unavailable."""
        # Mock DeepSeek response
        mock_analyze.return_value = {
            "score": 0.7,
            "mood": "optimistic",
            "factors": ["price increase", "high volume"],
            "social_sentiment": "positive",
            "confidence": 0.8
        }
        
        mcp = MarketSentimentMCP()
        
        # Ensure RehoboamAI instance has an API key
        mcp.rehoboam_ai.api_key = "test-key"
        
        # Call analyze_token_sentiment synchronously for testing
        result = asyncio.run(mcp.analyze_token_sentiment("ETH"))
        
        # Verify we got the mocked DeepSeek result
        assert result["mood"] == "optimistic"
        assert result["score"] == 0.7
        assert result["confidence"] == 0.8
        
        # Verify health check was called
        assert mock_health.call_count == 1
        
        # Verify DeepSeek was called
        assert mock_analyze.call_count == 1
    
    @patch.object(MCPClient, "health_check", return_value=False)
    @patch.object(RehoboamAI, "analyze_sentiment", side_effect=Exception("API Error"))
    def test_rule_based_fallback_when_deepseek_fails(self, mock_analyze, mock_health):
        """Test that rule-based fallback is used when DeepSeek fails."""
        mcp = MarketSentimentMCP()
        
        # Ensure RehoboamAI instance has an API key to attempt DeepSeek
        mcp.rehoboam_ai.api_key = "test-key"
        
        # Monkey patch the web_data to return controlled values
        mcp.web_data.get_24h_change = lambda token: 3.5
        
        # Call analyze_token_sentiment synchronously for testing
        result = asyncio.run(mcp.analyze_token_sentiment("ETH"))
        
        # Verify we got the rule-based result based on 3.5% price change
        assert result["mood"] == "optimistic"
        assert result["score"] == 0.6
        assert result["confidence"] == 0.5
        
        # Verify health check was called
        assert mock_health.call_count == 1
        
        # Verify DeepSeek was called but failed
        assert mock_analyze.call_count == 1


# Add asyncio import for async test cases
import asyncio