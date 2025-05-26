
import pytest
from unittest.mock import Mock, patch
import json
import time
import os
from datetime import datetime
from utils.ai_market_analyzer import AIMarketAnalyzer

class TestAIMarketAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return AIMarketAnalyzer()
        
    @pytest.fixture
    def sample_market_data(self):
        return {
            "price_history": [100.0, 101.0, 102.0, 101.5, 103.0],
            "technical_indicators": {
                "rsi": 55.5,
                "macd": {"line": 0.5, "signal": 0.3, "histogram": 0.2},
                "bollinger_bands": {"upper": 105.0, "middle": 102.0, "lower": 99.0}
            },
            "market_events": ["Positive regulatory news", "Major partnership announced"]
        }

    def test_provider_selection(self, analyzer):
        """Test provider selection based on available API keys"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-openai-key',
            'OPENROUTER_API_KEY': 'test-router-key'
        }, clear=True):
            analyzer._setup_provider()
            assert analyzer.current_provider["provider"] == "openai"
        
    def test_initialization(self, analyzer):
        """Test proper initialization of AIMarketAnalyzer"""
        assert isinstance(analyzer, AIMarketAnalyzer)
        assert analyzer.cache_duration == 300
        assert len(analyzer.model_chain) == 3
        
    @patch('requests.post')
    def test_analyze_market_conditions(self, mock_post, analyzer, sample_market_data):
        """Test market analysis with mocked API response"""
        # Configure mock
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "sentiment": "bull",
                        "risk": "mid",
                        "levels": {"s": [98.0, 99.0], "r": [105.0, 107.0]},
                        "acts": ["increase_position", "set_stop_loss"],
                        "conf": 0.8
                    })
                }
            }]
        }
        
        # Perform analysis with coin_pair parameter
        result = analyzer.analyze_market_conditions(
            coin_pair="ETH-USD",
            price_history=sample_market_data["price_history"],
            technical_indicators=sample_market_data["technical_indicators"],
            market_events=sample_market_data["market_events"]
        )
        
        assert result["market_sentiment"] == "bullish"
        assert result["risk_level"] == "medium"
        assert len(result["support_levels"]) > 0
        assert len(result["resistance_levels"]) > 0
        
    @patch('requests.post')
    def test_error_handling(self, mock_post, analyzer, sample_market_data):
        """Test error handling with failed API request"""
        # Simulate API error
        mock_post.side_effect = Exception("API Error")
        
        # Perform analysis with coin_pair parameter
        result = analyzer.analyze_market_conditions(
            coin_pair="ETH-USD",
            price_history=sample_market_data["price_history"],
            technical_indicators=sample_market_data["technical_indicators"]
        )
        
        assert result["market_sentiment"] == "neutral"
        assert result["risk_level"] == "medium"
        assert result["prediction_confidence"] == 0.5
        
    def test_cache_behavior(self, analyzer, sample_market_data):
        """Test caching mechanism"""
        # Mock successful analysis result
        analyzer.cache = {
            f"market_analysis_{datetime.now().strftime('%Y%m%d_%H')}": (
                time.time(),
                {"market_sentiment": "bullish", "prediction_confidence": 0.9}
            )
        }
        
        # Should return cached result
        result = analyzer.analyze_market_conditions(
            coin_pair="ETH-USD",
            price_history=sample_market_data["price_history"],
            technical_indicators=sample_market_data["technical_indicators"]
        )
        
        assert result["market_sentiment"] == "bullish"
        assert result["prediction_confidence"] == 0.9

    def test_get_prediction_confidence(self, analyzer):
        """Test confidence calculation with different market conditions"""
        analysis = {
            "market_sentiment": "strongly_bullish",
            "risk_level": "low",
            "prediction_confidence": 0.8
        }
        confidence = analyzer.get_prediction_confidence(analysis)
        assert 0.8 < confidence <= 1.0
import pytest
import numpy as np
from utils.ai_market_analyzer import AIMarketAnalyzer, MarketPrediction

class TestAIMarketAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return AIMarketAnalyzer()
        
    @pytest.fixture
    def sample_data(self):
        # Generate sample price and volume data
        np.random.seed(42)
        price_data = [100 * (1 + np.random.normal(0, 0.02)) for _ in range(200)]
        volume_data = [1000 * (1 + np.random.normal(0, 0.5)) for _ in range(200)]
        return price_data, volume_data
        
    def test_initialization(self, analyzer):
        assert analyzer.lookback_period == 100
        assert analyzer.prediction_threshold == 0.75
        assert isinstance(analyzer.cached_predictions, dict)
        
    def test_analyze_market_conditions(self, analyzer, sample_data):
        price_data, volume_data = sample_data
        prediction = analyzer.analyze_market_conditions(price_data, volume_data)
        
        assert isinstance(prediction, MarketPrediction)
        assert 0 <= prediction.confidence <= 1
        assert prediction.trend_direction in ['bullish', 'bearish', 'unknown']
        assert len(prediction.supporting_factors) > 0
        
    def test_error_handling(self, analyzer):
        # Test with insufficient data
        prediction = analyzer.analyze_market_conditions([1.0], [100.0])
        assert prediction.trend_direction == "unknown"
        assert prediction.confidence == 0.0
        
    def test_cache_behavior(self, analyzer, sample_data):
        price_data, volume_data = sample_data
        
        # First prediction
        prediction1 = analyzer.analyze_market_conditions(price_data, volume_data)
        
        # Second prediction should be different (no caching in test)
        prediction2 = analyzer.analyze_market_conditions(price_data, volume_data)
        
        assert prediction1 is not prediction2
        
    def test_get_prediction_confidence(self, analyzer, sample_data):
        price_data, volume_data = sample_data
        features = analyzer._prepare_features(price_data, volume_data)
        
        confidence = analyzer._calculate_prediction_confidence(
            predicted_price=110.0,
            price_history=price_data,
            features=features
        )
        
        assert 0 <= confidence <= 1
