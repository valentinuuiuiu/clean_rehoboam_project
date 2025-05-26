"""
Test suite for the EnhancedMCPSpecialist

This module contains tests for the EnhancedMCPSpecialist class with its
expanded capabilities from the Model Context Protocol servers.
"""

import os
import sys
import json
import pytest
import logging
import asyncio
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rehoboam_ai import RehoboamAI
from utils.enhanced_mcp_specialist import EnhancedMCPSpecialist

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EnhancedMCP_Test")


@pytest.fixture
def rehoboam():
    """Fixture providing a Rehoboam instance."""
    return RehoboamAI()


@pytest.fixture
def enhanced_mcp(rehoboam):
    """Fixture providing an EnhancedMCPSpecialist instance."""
    return EnhancedMCPSpecialist(rehoboam)


def test_basic_initialization(enhanced_mcp):
    """Test basic initialization of EnhancedMCPSpecialist."""
    assert enhanced_mcp is not None
    assert enhanced_mcp.rehoboam is not None
    assert enhanced_mcp.reasoning is not None
    

def test_technical_indicators(enhanced_mcp):
    """Test technical indicator calculations."""
    # Test moving average
    prices = [100, 105, 110, 108, 112]
    ma = enhanced_mcp.run_mcp_function("calculate_moving_average", prices, 3)
    assert ma == pytest.approx(110.0, 0.01)
    
    # Test RSI
    prices = [100, 102, 104, 103, 105, 107, 109, 108, 110, 112, 111, 
              113, 115, 114, 116, 118, 117, 119, 120, 118]
    rsi = enhanced_mcp.run_mcp_function("calculate_rsi", prices)
    assert 20 <= rsi <= 80  # RSI can be outside 30-70 range with our sample data
    
    # Test volatility
    volatility = enhanced_mcp.run_mcp_function("calculate_volatility", prices)
    assert "volatility" in volatility
    assert "normalized_volatility" in volatility
    assert "sample_size" in volatility
    assert volatility["sample_size"] == len(prices)


def test_risk_assessment(enhanced_mcp):
    """Test risk assessment functionality."""
    risk_assessment = enhanced_mcp.run_mcp_function(
        "assess_position_risk",
        position_size=1.0,
        entry_price=3000.0,
        token="ETH",
        network="ethereum",
        side="buy"
    )
    
    assert "risk_score" in risk_assessment
    assert "max_drawdown" in risk_assessment
    assert "recommended_stop_loss" in risk_assessment
    assert risk_assessment["token"] == "ETH"
    assert risk_assessment["network"] == "ethereum"


def test_resource_management(enhanced_mcp):
    """Test resource management functionality."""
    # Create a resource
    resource_uri = enhanced_mcp.create_resource(
        template="market://price/{token}/{network}",
        params={"token": "BTC", "network": "ethereum"},
        data={"price": 60000.0, "timestamp": "2025-05-14T23:45:00Z"}
    )
    
    assert resource_uri == "market://price/BTC/ethereum"
    
    # Get the resource
    resource = enhanced_mcp.get_resource(resource_uri)
    assert resource is not None
    assert resource["params"]["token"] == "BTC"
    assert resource["params"]["network"] == "ethereum"
    
    # Subscribe to the resource
    enhanced_mcp.subscribe_to_resource(resource_uri)
    assert resource_uri in enhanced_mcp.subscriptions
    
    # Unsubscribe from the resource
    enhanced_mcp.unsubscribe_from_resource(resource_uri)
    assert resource_uri not in enhanced_mcp.subscriptions


def test_arbitrage_analysis(enhanced_mcp):
    """Test arbitrage opportunity analysis."""
    arbitrage = enhanced_mcp.run_mcp_function(
        "analyze_arbitrage_opportunity",
        token="ETH",
        buy_network="arbitrum",
        sell_network="ethereum",
        buy_price=3000.0,
        sell_price=3100.0
    )
    
    assert "raw_profit_percentage" in arbitrage
    assert "net_profit_percentage" in arbitrage
    assert "confidence" in arbitrage
    assert "recommended" in arbitrage
    
    # The profit should be approximately 3.33% before costs
    assert arbitrage["raw_profit_percentage"] == pytest.approx(3.33, 0.1)


def test_sequential_thinking(enhanced_mcp):
    """Test sequential thinking tools."""
    problem = "Should I enter a long ETH position given current market conditions?"
    thoughts = enhanced_mcp.run_mcp_function("create_thought_sequence", problem=problem)
    
    assert len(thoughts) > 0
    assert "thought" in thoughts[0]
    
    # Test counter arguments
    argument = "ETH is definitely going to increase in price."
    counter_args = enhanced_mcp.run_mcp_function("generate_counter_arguments", argument=argument)
    
    assert len(counter_args) > 0
    assert isinstance(counter_args[0], str)


@pytest.mark.asyncio
async def test_mcp_availability(enhanced_mcp):
    """Test MCP server availability check."""
    is_available = await enhanced_mcp.check_mcp_availability()
    # We don't assert a specific value, as MCP may or may not be available
    assert isinstance(is_available, bool)


@pytest.mark.asyncio
async def test_integrate_server_capabilities(enhanced_mcp):
    """Test integration with MCP server capabilities."""
    result = await enhanced_mcp.integrate_mcp_server_capabilities("sequentialthinking")
    assert isinstance(result, bool)


if __name__ == "__main__":
    # Run the tests directly
    pytest.main(["-xvs", __file__])