"""
Tests for the MCPSpecialist - Rehoboam's MCP creation and management system
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.mcp_specialist import MCPSpecialist, MCPFunction
from utils.rehoboam_ai import RehoboamAI


@pytest.fixture
def mock_rehoboam():
    with patch('utils.rehoboam_ai.RehoboamAI') as mock:
        # Configure the mock RehoboamAI
        instance = mock.return_value
        instance.async_get_completion = AsyncMock(return_value="def test_function(x, y):\n    \"\"\"Test function\"\"\"\n    return x + y")
        instance.analyze_sentiment = MagicMock(return_value={"sentiment": "neutral", "score": 0.0, "confidence": 0.5})
        instance.get_market_emotions = MagicMock(return_value={"emotion": "fear", "intensity": 0.7})
        yield mock


@pytest.fixture
def mcp_specialist(mock_rehoboam):
    return MCPSpecialist(mock_rehoboam.return_value)


def test_mcp_function_creation():
    """Test the creation of MCPFunction objects."""
    def sample_func(x, y):
        """Sample function docstring"""
        return x + y
    
    # Create MCP function
    mcp_func = MCPFunction(
        name="test_add",
        func=sample_func,
        description="Test addition function",
        mcp_type="processor"
    )
    
    # Test attributes
    assert mcp_func.name == "test_add"
    assert mcp_func.description == "Test addition function"
    assert mcp_func.mcp_type == "processor"
    assert mcp_func.call_count == 0
    assert mcp_func.success_rate == 1.0
    
    # Test function call
    result = mcp_func(3, 4)
    assert result == 7
    assert mcp_func.call_count == 1
    assert mcp_func.last_used is not None
    
    # Test to_dict
    func_dict = mcp_func.to_dict()
    assert func_dict["name"] == "test_add"
    assert func_dict["description"] == "Test addition function"
    assert func_dict["mcp_type"] == "processor"
    assert func_dict["call_count"] == 1
    assert func_dict["success_rate"] == 1.0


def test_mcp_specialist_initialization(mcp_specialist):
    """Test MCPSpecialist initialization."""
    assert mcp_specialist is not None
    assert mcp_specialist.rehoboam is not None
    assert isinstance(mcp_specialist.mcp_functions, dict)
    assert len(mcp_specialist.consciousness) == 5  # Consciousness vector initialized


def test_register_mcp_function(mcp_specialist):
    """Test registering an MCP function."""
    def test_func(x):
        return x * 2
    
    # Register function
    func = mcp_specialist.register_mcp_function(
        name="test_double",
        func=test_func,
        description="Double a number",
        mcp_type="processor"
    )
    
    # Verify registration
    assert mcp_specialist.has_mcp_function("test_double")
    assert mcp_specialist.get_mcp_function("test_double") is func
    
    # Test function execution through MCPSpecialist
    result = mcp_specialist.run_mcp_function("test_double", 5)
    assert result == 10


def test_list_mcp_functions(mcp_specialist):
    """Test listing MCP functions."""
    # Register a few functions
    def func1(x): return x + 1
    def func2(x): return x * 2
    def func3(x): return x ** 2
    
    mcp_specialist.register_mcp_function("add_one", func1, mcp_type="processor")
    mcp_specialist.register_mcp_function("double", func2, mcp_type="processor")
    mcp_specialist.register_mcp_function("square", func3, mcp_type="analyzer")
    
    # List all functions
    all_funcs = mcp_specialist.list_mcp_functions()
    assert len(all_funcs) == 3
    
    # List functions by type
    processor_funcs = mcp_specialist.list_mcp_functions(mcp_type="processor")
    assert len(processor_funcs) == 2
    
    analyzer_funcs = mcp_specialist.list_mcp_functions(mcp_type="analyzer")
    assert len(analyzer_funcs) == 1
    assert analyzer_funcs[0]["name"] == "square"


@pytest.mark.asyncio
async def test_check_mcp_availability(mcp_specialist):
    """Test checking MCP server availability."""
    # Mock the requests.get call
    with patch('requests.get') as mock_get:
        # Test when server is available
        mock_get.return_value.status_code = 200
        available = await mcp_specialist.check_mcp_availability()
        assert available is True
        
        # Test when server returns error
        mock_get.return_value.status_code = 500
        available = await mcp_specialist.check_mcp_availability()
        assert available is False
        
        # Test when server request raises exception
        mock_get.side_effect = Exception("Connection error")
        available = await mcp_specialist.check_mcp_availability()
        assert available is False


@pytest.mark.asyncio
async def test_generate_mcp_function(mcp_specialist):
    """Test generating an MCP function."""
    # This test requires creating a temporary file and importing it,
    # so we'll mock the file operations
    with patch('tempfile.NamedTemporaryFile'), \
         patch('importlib.util.spec_from_file_location'), \
         patch('importlib.util.module_from_spec'), \
         patch('os.unlink'):
        
        # Mock the generated module
        mock_module = MagicMock()
        mock_module.test_function = lambda x, y: x + y
        
        # Mock the loader execution
        spec_mock = MagicMock()
        with patch('importlib.util.module_from_spec', return_value=mock_module), \
             patch('importlib.util.spec_from_file_location', return_value=spec_mock):
            
            # Test function generation
            func = await mcp_specialist.generate_mcp_function(
                name="test_function",
                description="Test function that adds two numbers",
                parameter_description="x: first number, y: second number",
                return_description="The sum of x and y"
            )
            
            # Verify function was registered
            assert func is not None
            assert mcp_specialist.has_mcp_function("test_function")
            
            # Test the function
            mcp_specialist.rehoboam.async_get_completion.assert_called_once()
            
            # Try to generate the same function again
            func2 = await mcp_specialist.generate_mcp_function(
                name="test_function",
                description="Test function that adds two numbers",
                parameter_description="x: first number, y: second number", 
                return_description="The sum of x and y"
            )
            
            # Should return the existing function without regenerating
            assert func2 is func
            assert mcp_specialist.rehoboam.async_get_completion.call_count == 1


@pytest.mark.asyncio
async def test_adapt_function_to_mcp(mcp_specialist):
    """Test adapting an existing function to MCP protocol."""
    def sample_func(a, b, c=None):
        """Sample function with docstring"""
        return a + b + (c or 0)
    
    # Adapt the function
    func = await mcp_specialist.adapt_function_to_mcp(sample_func)
    
    # Verify adaptation
    assert func is not None
    assert mcp_specialist.has_mcp_function("sample_func")
    
    # Test execution
    result = mcp_specialist.run_mcp_function("sample_func", 1, 2, 3)
    assert result == 6
    
    # Test with custom name and description
    func2 = await mcp_specialist.adapt_function_to_mcp(
        sample_func,
        name="custom_add",
        description="Custom addition function"
    )
    
    assert func2.name == "custom_add"
    assert func2.description == "Custom addition function"


def test_market_analysis_with_mcp(mcp_specialist):
    """Test getting market analysis through MCP."""
    # Test with no specialized function registered
    analysis = mcp_specialist.get_market_analysis_with_mcp("BTC")
    
    # Should fall back to Rehoboam
    mcp_specialist.rehoboam.analyze_sentiment.assert_called_once_with("BTC", {})
    assert "sentiment" in analysis
    
    # Register a specialized function
    def custom_analysis(token):
        return {"token": token, "sentiment": "bullish", "score": 0.8}
    
    mcp_specialist.register_mcp_function(
        "market_sentiment_mcp.MarketSentimentMCP.analyze_token",
        custom_analysis
    )
    
    # Test with specialized function
    analysis = mcp_specialist.get_market_analysis_with_mcp("ETH")
    assert analysis["token"] == "ETH"
    assert analysis["sentiment"] == "bullish"
    
    # Test with failing specialized function
    def failing_analysis(token):
        raise Exception("Analysis failed")
    
    # Replace with failing function
    mcp_specialist.mcp_functions["market_sentiment_mcp.MarketSentimentMCP.analyze_token"].func = failing_analysis
    
    # Should fall back to Rehoboam
    analysis = mcp_specialist.get_market_analysis_with_mcp("LTC")
    mcp_specialist.rehoboam.analyze_sentiment.assert_called_with("LTC", {})


def test_market_emotions_with_mcp(mcp_specialist):
    """Test getting market emotions through MCP."""
    # Test with no specialized function registered
    emotions = mcp_specialist.get_market_emotions_with_mcp()
    
    # Should fall back to Rehoboam
    mcp_specialist.rehoboam.get_market_emotions.assert_called_once()
    assert "emotion" in emotions
    
    # Register a specialized function
    def custom_emotions():
        return {"emotion": "euphoria", "intensity": 0.9, "greed_fear_index": 85}
    
    mcp_specialist.register_mcp_function(
        "rehoboam_ai.RehoboamAI.get_market_emotions",
        custom_emotions
    )
    
    # Test with specialized function
    emotions = mcp_specialist.get_market_emotions_with_mcp()
    assert emotions["emotion"] == "euphoria"
    assert emotions["greed_fear_index"] == 85
    
    # Test with failing specialized function
    def failing_emotions():
        raise Exception("Emotions analysis failed")
    
    # Replace with failing function
    mcp_specialist.mcp_functions["rehoboam_ai.RehoboamAI.get_market_emotions"].func = failing_emotions
    
    # Should fall back to Rehoboam
    emotions = mcp_specialist.get_market_emotions_with_mcp()
    # Called twice now (first call + fallback call)
    assert mcp_specialist.rehoboam.get_market_emotions.call_count == 2