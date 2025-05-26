"""
Tests for the RehoboamMCPIntegration class
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.rehoboam_mcp_integration import RehoboamMCPIntegration
from utils.rehoboam_ai import RehoboamAI
from utils.mcp_specialist import MCPSpecialist


@pytest.fixture
def mock_rehoboam():
    with patch('utils.rehoboam_ai.RehoboamAI') as mock:
        # Configure the mock
        instance = mock.return_value
        instance.get_completion = MagicMock(return_value="def test_function(x): return x * 2")
        instance.analyze_sentiment = MagicMock(return_value={"sentiment": "neutral", "score": 0})
        instance.get_market_emotions = MagicMock(return_value={
            "emotion": "fear", 
            "intensity": 0.7,
            "description": "Market fear with caution"
        })
        yield mock


@pytest.fixture
def mock_mcp_specialist():
    with patch('utils.mcp_specialist.MCPSpecialist') as mock:
        # Configure the mock
        instance = mock.return_value
        instance.check_mcp_availability = AsyncMock(return_value=False)
        instance.get_market_analysis_with_mcp = MagicMock(return_value={
            "token": "BTC",
            "sentiment": "bullish",
            "score": 0.8,
            "confidence": 0.7
        })
        instance.get_market_emotions_with_mcp = MagicMock(return_value={
            "emotion": "greed",
            "intensity": 0.8,
            "description": "Market greed with excitement"
        })
        instance.generate_mcp_function = AsyncMock(return_value=True)
        instance.has_mcp_function = MagicMock(return_value=True)
        instance.list_mcp_functions = MagicMock(return_value=[
            {"name": "func1", "description": "Test function 1"},
            {"name": "func2", "description": "Test function 2"}
        ])
        yield mock


@pytest.fixture
def integration(mock_rehoboam, mock_mcp_specialist):
    # Patch the MCPSpecialist class in the RehoboamMCPIntegration module
    with patch('utils.rehoboam_mcp_integration.MCPSpecialist', return_value=mock_mcp_specialist.return_value):
        # Create the integration with the mock Rehoboam
        integration = RehoboamMCPIntegration(mock_rehoboam.return_value)
        yield integration


def test_initialization(integration, mock_rehoboam, mock_mcp_specialist):
    """Test initialization of RehoboamMCPIntegration."""
    assert integration.rehoboam is mock_rehoboam.return_value
    assert integration.mcp_specialist is mock_mcp_specialist.return_value
    assert isinstance(integration.capability_map, dict)
    assert "sentiment_analysis" in integration.capability_map
    assert "market_emotions" in integration.capability_map


@pytest.mark.asyncio
async def test_check_mcp_availability(integration):
    """Test checking MCP server availability."""
    availability = await integration.check_mcp_availability()
    assert availability is False
    integration.mcp_specialist.check_mcp_availability.assert_called_once()


def test_get_sentiment_analysis(integration):
    """Test getting sentiment analysis for a token."""
    result = asyncio.run(integration.get_sentiment_analysis("BTC"))
    assert result["token"] == "BTC"
    assert result["sentiment"] == "bullish"
    assert result["score"] == 0.8
    integration.mcp_specialist.get_market_analysis_with_mcp.assert_called_with("BTC")


def test_get_market_emotions(integration):
    """Test getting market emotions."""
    result = asyncio.run(integration.get_market_emotions())
    assert result["emotion"] == "greed"
    assert result["intensity"] == 0.8
    integration.mcp_specialist.get_market_emotions_with_mcp.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_sentiment_analysis_function(integration):
    """Test ensuring sentiment analysis function exists."""
    # Make the function not exist first time
    integration.mcp_specialist.has_mcp_function.return_value = False
    
    # Create a basic function
    def analyze_token(token):
        return {"token": token, "sentiment": "neutral", "score": 0}
    
    # Test the function creation
    integration.mcp_specialist.generate_mcp_function.return_value = analyze_token
    
    # Call the method that ensures the function exists
    await integration._ensure_sentiment_analysis_function()
    
    # Verify it was called with proper parameters
    integration.mcp_specialist.generate_mcp_function.assert_called_once()
    args = integration.mcp_specialist.generate_mcp_function.call_args[1]
    assert args["name"] == "analyze_token_sentiment"
    assert "sentiment" in args["description"].lower()


@pytest.mark.asyncio
async def test_ensure_market_emotions_function(integration):
    """Test ensuring market emotions function exists."""
    # Make the function not exist first time
    integration.mcp_specialist.has_mcp_function.return_value = False
    
    # Create a basic function
    def analyze_emotions():
        return {"emotion": "fear", "intensity": 0.5}
    
    # Test the function creation
    integration.mcp_specialist.generate_mcp_function.return_value = analyze_emotions
    
    # Call the method that ensures the function exists
    await integration._ensure_market_emotions_function()
    
    # Verify it was called with proper parameters
    integration.mcp_specialist.generate_mcp_function.assert_called_once()
    args = integration.mcp_specialist.generate_mcp_function.call_args[1]
    assert args["name"] == "analyze_market_emotions"
    assert "emotion" in args["description"].lower()


@pytest.mark.asyncio
async def test_create_custom_mcp_function(integration):
    """Test creating a custom MCP function."""
    # Set up the test
    function_spec = {
        "name": "test_function",
        "description": "Test function",
        "parameters": "param1: int, param2: str",
        "returns": "Dict with result",
        "example": "def test_function(param1, param2): return {'result': param1}"
    }
    
    # Test creating a function
    result = await integration.create_custom_mcp_function("test_capability", function_spec)
    
    # Verify the results
    assert result is True
    integration.mcp_specialist.generate_mcp_function.assert_called_once()
    assert "test_capability" in integration.capability_map
    assert integration.capability_map["test_capability"] == "test_function"
    
    # Test trying to create the same function again
    integration.mcp_specialist.generate_mcp_function.reset_mock()
    result = await integration.create_custom_mcp_function("test_capability", function_spec)
    
    # Verify it skips generation for known capabilities
    assert result is False
    integration.mcp_specialist.generate_mcp_function.assert_not_called()


def test_get_available_capabilities(integration):
    """Test getting available capabilities."""
    # Add some capabilities
    integration.capability_map.update({
        "test1": "func1",
        "test2": "func2"
    })
    
    capabilities = integration.get_available_capabilities()
    
    # Check the capabilities list
    assert isinstance(capabilities, list)
    assert "sentiment_analysis" in capabilities
    assert "market_emotions" in capabilities
    assert "test1" in capabilities
    assert "test2" in capabilities


def test_get_registered_mcp_functions(integration):
    """Test getting registered MCP functions."""
    functions = integration.get_registered_mcp_functions()
    
    # Verify the result
    assert len(functions) == 2
    assert functions[0]["name"] == "func1"
    assert functions[1]["name"] == "func2"
    integration.mcp_specialist.list_mcp_functions.assert_called_once()


@pytest.mark.asyncio
async def test_adapt_existing_function(integration):
    """Test adapting an existing function to MCP."""
    # Create a test function
    def test_function(x, y):
        return x + y
    
    # Setup the mock
    mock_mcp_function = MagicMock()
    mock_mcp_function.name = "test_function"
    integration.mcp_specialist.adapt_function_to_mcp = AsyncMock(return_value=mock_mcp_function)
    
    # Test the adaptation
    result = await integration.adapt_existing_function(test_function, "addition")
    
    # Verify results
    assert result is True
    integration.mcp_specialist.adapt_function_to_mcp.assert_called_once_with(test_function)
    assert integration.capability_map["addition"] == "test_function"
    
    # Test error handling
    integration.mcp_specialist.adapt_function_to_mcp = AsyncMock(return_value=None)
    result = await integration.adapt_existing_function(test_function, "failed_addition")
    
    # Verify error handling
    assert result is False
    assert "failed_addition" not in integration.capability_map