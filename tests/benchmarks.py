
"""Rehoboam Performance Benchmark Tests"""
import time
import pytest
from trading_controller import TradingController
from utils.market_data import SampleDataGenerator

@pytest.fixture
def trading_controller():
    return TradingController()

@pytest.fixture
def sample_data():
    return SampleDataGenerator().generate(100)  # 100 assets

def test_decision_latency(trading_controller, sample_data):
    """Test decision-making meets latency requirements"""
    start = time.perf_counter()
    trading_controller.make_trading_decision(sample_data)
    latency = time.perf_counter() - start
    assert latency < 0.5  # 500ms maximum latency
    print(f"\nDecision latency: {latency*1000:.2f}ms")

def test_llm_cache_performance(trading_controller, sample_data):
    """Test LLM cache hit rate and speed"""
    # Warm up cache
    trading_controller.make_trading_decision(sample_data)
    
    # Test cached performance
    start = time.perf_counter()
    result = trading_controller.make_trading_decision(sample_data)
    cached_latency = time.perf_counter() - start
    
    assert cached_latency < 0.1  # 100ms for cached decisions
    assert trading_controller.llm_cache_hit_rate() > 0.7
    print(f"\nCached decision latency: {cached_latency*1000:.2f}ms")

def test_throughput(trading_controller, sample_data):
    """Test system throughput under load"""
    start = time.perf_counter()
    for _ in range(100):
        trading_controller.make_trading_decision(sample_data)
    total_time = time.perf_counter() - start
    
    assert total_time < 10  # 100 decisions in <10 seconds
    print(f"\nThroughput: {100/total_time:.2f} decisions/sec")

def test_market_data_processing(trading_controller):
    """Test market data processing speed"""
    large_data = SampleDataGenerator().generate(1000)  # 1000 assets
    start = time.perf_counter()
    trading_controller.process_market_data(large_data)
    process_time = time.perf_counter() - start
    
    assert process_time < 1.0  # 1 second for 1000 assets
    print(f"\nMarket data processing: {process_time*1000:.2f}ms")
