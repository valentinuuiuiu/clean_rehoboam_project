
import pytest
import numpy as np
from utils.advanced_reasoning import AdvancedReasoning, SystemState

@pytest.fixture
def reasoning():
    return AdvancedReasoning()

@pytest.fixture
def sample_data():
    # Generate sample price and volume data
    np.random.seed(42)
    price_history = [100 * (1 + np.random.normal(0, 0.02)) for _ in range(100)]
    volume_history = [1000 * (1 + np.random.normal(0, 0.5)) for _ in range(100)]
    sentiment_data = {
        'social_media': 0.7,
        'news': 0.6,
        'technical': 0.8
    }
    market_signals = {
        'momentum': 0.5,
        'trend': 0.6,
        'volatility': 0.3
    }
    return price_history, volume_history, sentiment_data, market_signals

def test_market_state_analysis(reasoning, sample_data):
    price_history, volume_history, sentiment_data, market_signals = sample_data
    state, confidence = reasoning.analyze_market_state(
        price_history, volume_history, sentiment_data, market_signals
    )
    
    assert isinstance(state, SystemState)
    assert 0 <= confidence <= 1
    assert 0 <= state.market_volatility <= 1
    assert -1 <= state.trend_strength <= 1
    assert 0 <= state.liquidity_score <= 1
    assert 0 <= state.sentiment_score <= 1
    assert 0 <= state.risk_appetite <= 1
    assert isinstance(state.market_regime, str)
    assert 0 <= state.anomaly_score <= 1

def test_adaptive_volatility(reasoning, sample_data):
    price_history, *_ = sample_data
    volatility = reasoning._calculate_adaptive_volatility(price_history)
    assert isinstance(volatility, float)
    assert volatility >= 0

def test_complex_trend(reasoning, sample_data):
    price_history, *_ = sample_data
    trend = reasoning._analyze_complex_trend(price_history)
    assert isinstance(trend, float)

def test_market_liquidity(reasoning, sample_data):
    price_history, volume_history, *_ = sample_data
    liquidity = reasoning._assess_market_liquidity(volume_history, price_history)
    assert isinstance(liquidity, float)
    assert 0 <= liquidity <= 1

def test_sentiment_processing(reasoning, sample_data):
    _, _, sentiment_data, _ = sample_data
    sentiment = reasoning._process_sentiment(sentiment_data)
    assert isinstance(sentiment, float)
    assert 0 <= sentiment <= 1

def test_regime_detection(reasoning, sample_data):
    price_history, volume_history, *_ = sample_data
    regime = reasoning._detect_market_regime(price_history, volume_history)
    assert isinstance(regime, str)
    assert regime in [
        "volatile_uptrend", "volatile_downtrend", "stable_liquid",
        "stable_illiquid", "bullish_trend", "bearish_trend",
        "ranging", "unknown"
    ]

def test_anomaly_detection(reasoning, sample_data):
    price_history, volume_history, *_ = sample_data
    anomaly_score = reasoning._detect_anomalies(price_history, volume_history)
    assert isinstance(anomaly_score, float)
    assert 0 <= anomaly_score <= 1

def test_error_handling(reasoning):
    # Test with empty data
    state, confidence = reasoning.analyze_market_state([], [], {}, {})
    assert isinstance(state, SystemState)
    assert confidence == 0.0
    assert state.market_regime == "unknown"
