import pytest
import httpx
import json
from unittest.mock import patch, AsyncMock, MagicMock

from utils.mcp_clients import _get_service_url_from_registry, MCP_REGISTRY_URL

MOCK_SERVICE_NAME_FOUND = "consciousness-layer"
MOCK_SERVICE_URL_FOUND = "http://consciousness-layer-service:3005"
MOCK_SERVICE_NAME_ALIAS = "mcp-consciousness-layer" # an alias that should also be found

MOCK_REGISTRY_DATA_VALID = {
    "services": {
        MOCK_SERVICE_NAME_FOUND: {
            "url": MOCK_SERVICE_URL_FOUND,
            "description": "Provides consciousness state.",
            "functions": ["get_state", "get_emotions_stream"]
        },
        "market-analyzer": {
            "url": "http://market-analyzer-service:3002",
            "description": "Analyzes market data.",
            "functions": ["analyze_token", "get_trends"]
        }
    },
    "last_updated": "2024-05-28T12:00:00Z"
}

@pytest.mark.asyncio
async def test_get_service_url_success():
    """Test successful retrieval of a service URL from the registry."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND, MOCK_SERVICE_NAME_ALIAS],
        "TestContext"
    )

    assert service_url == MOCK_SERVICE_URL_FOUND
    mock_client.get.assert_called_once_with(f"{MCP_REGISTRY_URL}/registry") # Ensure this matches the actual call in the function

@pytest.mark.asyncio
async def test_get_service_url_success_alias():
    """Test successful retrieval using an alias service name."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        ["some-other-name", MOCK_SERVICE_NAME_ALIAS, MOCK_SERVICE_NAME_FOUND], # Alias first in this list
        "TestContextAlias"
    )
    # The current implementation of _get_service_url_from_registry iterates through service_names_to_find
    # and then iterates through the registry's services. It should find by MOCK_SERVICE_NAME_FOUND first if it's checked.
    # Let's adjust mock data so MOCK_SERVICE_NAME_ALIAS would be the one found.

    registry_data_alias_first = {
        "services": {
            MOCK_SERVICE_NAME_ALIAS: { # This is the key in the registry
                 "url": "http://alias-url:3000",
                 "description": "Alias service"
            },
             MOCK_SERVICE_NAME_FOUND: { # This also exists
                 "url": MOCK_SERVICE_URL_FOUND,
                 "description": "Original service"
            }
        }
    }
    mock_response.json.return_value = registry_data_alias_first

    service_url_alias = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_ALIAS, "another_name_not_present"], # Only the alias is in this find list
        "TestContextAlias"
    )
    assert service_url_alias == "http://alias-url:3000"


@pytest.mark.asyncio
async def test_get_service_url_success_case_insensitive():
    """Test case-insensitive lookup for service names."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND.upper(), "nonexistent-service"], # Search with uppercase
        "TestContextCaseInsensitive"
    )
    assert service_url == MOCK_SERVICE_URL_FOUND # Should still find it

@pytest.mark.asyncio
async def test_get_service_url_not_found(caplog):
    """Test when the service name is not found in the registry."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    service_name_not_found = "nonexistent-service"
    service_url = await _get_service_url_from_registry(
        mock_client,
        [service_name_not_found, "another-one-gone"],
        "TestContextNotFound"
    )

    assert service_url is None
    # Updated expected log message based on the modified function's logging
    expected_log = f"Service names ['{service_name_not_found.lower()}', '{'another-one-gone'.lower()}'] not found in MCP Registry for TestContextNotFound with valid URL."
    assert expected_log in caplog.text


@pytest.mark.asyncio
async def test_get_service_url_registry_http_error(caplog):
    """Test handling of HTTPStatusError when fetching from registry."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.HTTPStatusError(
        "Registry error", request=MagicMock(), response=MagicMock(status_code=500)
    )

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextHttpError"
    )
    assert service_url is None
    # Check for the simplified log message from the updated function
    assert "HTTP error fetching MCP registry for TestContextHttpError: Registry error" in caplog.text


@pytest.mark.asyncio
async def test_get_service_url_registry_network_error(caplog):
    """Test handling of RequestError (network error) when fetching from registry."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.RequestError("Network down", request=MagicMock())

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextNetworkError"
    )
    assert service_url is None
    assert "Network error fetching MCP registry for TestContextNetworkError: Network down" in caplog.text

@pytest.mark.asyncio
async def test_get_service_url_registry_invalid_json(caplog):
    """Test handling of invalid JSON response from registry."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0) # No need to pass "doc" and 0 for modern Python
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextInvalidJson"
    )
    assert service_url is None
    # Check for the simplified log message
    assert "Error decoding MCP registry JSON for TestContextInvalidJson: Invalid JSON" in caplog.text

@pytest.mark.asyncio
async def test_get_service_url_registry_unexpected_structure_no_services_key(caplog):
    """Test registry data missing the 'services' key."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"other_key": "some_data"} # Missing 'services'
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextNoServicesKey"
    )
    assert service_url is None
    # The function will fall through to the general "not found" if the structure is not as expected.
    expected_log = f"Service names ['{MOCK_SERVICE_NAME_FOUND.lower()}'] not found in MCP Registry for TestContextNoServicesKey with valid URL."
    assert expected_log in caplog.text

@pytest.mark.asyncio
async def test_get_service_url_registry_unexpected_structure_services_not_dict(caplog):
    """Test registry data where 'services' is not a dictionary."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"services": ["item1", "item2"]} # 'services' is a list
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextServicesNotDict"
    )
    assert service_url is None
    # The function now logs this message more generically.
    assert "MCP registry data does not contain 'services' key or it's not a dictionary for TestContextServicesNotDict" in caplog.text


@pytest.mark.asyncio
async def test_get_service_url_registry_unexpected_structure_service_not_dict(caplog):
    """Test registry data where a service entry under 'services' is not a dictionary."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "services": {
            MOCK_SERVICE_NAME_FOUND: "this_should_be_a_dict" # Service entry is a string
        }
    }
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextServiceNotDict"
    )
    assert service_url is None
    # The current implementation logs "Service entry for '{reg_service_name}' is not a dictionary."
    assert f"Service entry for '{MOCK_SERVICE_NAME_FOUND}' in MCP registry is not a dictionary for TestContextServiceNotDict" in caplog.text
    # The function will also log that the service name was ultimately not found with a valid URL.
    assert f"Service names ['{MOCK_SERVICE_NAME_FOUND.lower()}'] not found in MCP Registry for TestContextServiceNotDict with valid URL." in caplog.text

@pytest.mark.asyncio
async def test_get_service_url_registry_unexpected_structure_service_missing_url(caplog):
    """Test registry data where a service dictionary is missing the 'url' key."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "services": {
            MOCK_SERVICE_NAME_FOUND: {
                "description": "Missing URL here" # No 'url' key
            }
        }
    }
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextServiceMissingUrl"
    )
    assert service_url is None
    # The log for missing URL is now more specific to the key `reg_service_name`
    assert f"Service '{MOCK_SERVICE_NAME_FOUND}' URL is None in MCP registry for TestContextServiceMissingUrl" in caplog.text
    assert f"Service names ['{MOCK_SERVICE_NAME_FOUND.lower()}'] not found in MCP Registry for TestContextServiceMissingUrl with valid URL." in caplog.text

@pytest.mark.asyncio
async def test_get_service_url_registry_empty_services_dict(caplog):
    """Test registry data with an empty 'services' dictionary."""
    # This scenario is now covered by the general "not found" log if 'services' is empty
    # or "MCP registry data does not contain 'services' key" if the key is there but the dict is empty.
    # The latter is more specific if the 'services' key exists but is an empty dict.
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"services": {}} # Empty services dict
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextEmptyServices"
    )
    assert service_url is None
    # If services_dict is empty, it will fall through to the "not found" log
    assert f"Service names ['{MOCK_SERVICE_NAME_FOUND.lower()}'] not found in MCP Registry for TestContextEmptyServices with valid URL." in caplog.text

@pytest.mark.asyncio
async def test_get_service_url_general_exception_during_request(caplog):
    """Test handling of a general Exception during the HTTP request."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = Exception("Some general error")

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextGeneralException"
    )
    assert service_url is None
    assert "Unexpected error fetching MCP registry for TestContextGeneralException: Some general error" in caplog.text

@pytest.mark.asyncio
async def test_get_service_url_found_but_url_is_none(caplog):
    """Test when a service is found but its URL is explicitly None."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "services": {
            MOCK_SERVICE_NAME_FOUND: {
                "url": None, # URL is None
                "description": "Service with None URL"
            }
        }
    }
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextUrlNone"
    )
    assert service_url is None
    assert f"Service '{MOCK_SERVICE_NAME_FOUND}' URL is None in MCP registry for TestContextUrlNone." in caplog.text
    assert f"Service names ['{MOCK_SERVICE_NAME_FOUND.lower()}'] not found in MCP Registry for TestContextUrlNone with valid URL." in caplog.text


@pytest.mark.asyncio
async def test_get_service_url_found_but_url_is_empty_string(caplog):
    """Test when a service is found but its URL is an empty string."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "services": {
            MOCK_SERVICE_NAME_FOUND: {
                "url": "", # URL is empty string
                "description": "Service with empty URL"
            }
        }
    }
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND],
        "TestContextUrlEmpty"
    )
    assert service_url is None # Empty string URL is now treated as invalid and results in None
    assert f"Service '{MOCK_SERVICE_NAME_FOUND}' URL is empty in MCP registry for TestContextUrlEmpty." in caplog.text
    assert f"Service names ['{MOCK_SERVICE_NAME_FOUND.lower()}'] not found in MCP Registry for TestContextUrlEmpty with valid URL." in caplog.text


@pytest.mark.asyncio
async def test_get_service_url_multiple_names_to_find_first_one_exists():
    """Test providing multiple service names to find, where the first one exists."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        [MOCK_SERVICE_NAME_FOUND, "market-analyzer", "nonexistent-service"], # MOCK_SERVICE_NAME_FOUND is "consciousness-layer"
        "TestContextMultipleFindFirst"
    )
    assert service_url == MOCK_SERVICE_URL_FOUND # Correct, "consciousness-layer" is first and found

@pytest.mark.asyncio
async def test_get_service_url_multiple_names_to_find_second_one_exists():
    """Test providing multiple service names, where the second one exists."""
    # The function iterates service_names_to_find in order.
    # For each name, it iterates through the registry.
    # So, "nonexistent-service" is checked first against all registry entries.
    # Then "market-analyzer" is checked. It should match "market-analyzer" in the registry.
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    service_url = await _get_service_url_from_registry(
        mock_client,
        ["nonexistent-service", "market-analyzer", MOCK_SERVICE_NAME_FOUND],
        "TestContextMultipleFindSecond"
    )
    # Expected: "market-analyzer" URL because it's found before MOCK_SERVICE_NAME_FOUND ("consciousness-layer") in the search list.
    assert service_url == MOCK_REGISTRY_DATA_VALID["services"]["market-analyzer"]["url"]

@pytest.mark.asyncio
async def test_get_service_url_registry_response_logged(caplog):
    """Test that the registry response is logged when debug_log_registry_response is True."""
    import logging # Required for caplog.set_level and logger.level
    from utils import mcp_clients as mcp_clients_module # To access the logger instance

    # Set caplog level to capture DEBUG messages
    caplog.set_level(logging.DEBUG)

    # Also set the level of the specific logger instance used in mcp_clients
    original_level = mcp_clients_module.logger.level
    mcp_clients_module.logger.setLevel(logging.DEBUG)

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    with patch('utils.mcp_clients.DEBUG_LOG_REGISTRY_RESPONSE', True):
        await _get_service_url_from_registry(
            mock_client,
            [MOCK_SERVICE_NAME_FOUND],
            "TestContextLogResponse"
        )

    assert "MCP Registry raw response for TestContextLogResponse:" in caplog.text
    assert json.dumps(MOCK_REGISTRY_DATA_VALID, indent=2) in caplog.text

    # Restore original logger level
    mcp_clients_module.logger.setLevel(original_level)

@pytest.mark.asyncio
async def test_get_service_url_registry_response_not_logged_by_default(caplog):
    """Test that the registry response is NOT logged by default (DEBUG_LOG_REGISTRY_RESPONSE is False)."""
    # caplog by default captures WARNING and above. If DEBUG_LOG_REGISTRY_RESPONSE is False,
    # the specific debug log for raw response should not appear.
    # No need to set caplog level to DEBUG here, as we are asserting absence of a DEBUG log.

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_REGISTRY_DATA_VALID
    mock_client.get.return_value = mock_response

    # Ensure it's False, or not set (defaults to False in the module)
    with patch('utils.mcp_clients.DEBUG_LOG_REGISTRY_RESPONSE', False):
        await _get_service_url_from_registry(
            mock_client,
            [MOCK_SERVICE_NAME_FOUND],
            "TestContextNoLogResponse"
        )

    assert "MCP Registry raw response for TestContextNoLogResponse:" not in caplog.text
    assert json.dumps(MOCK_REGISTRY_DATA_VALID, indent=2) not in caplog.text


# Test data for consciousness state
MOCK_CONSCIOUSNESS_STATE_DATA = {"awareness_level": 0.9, "cognitive_load": 0.3}
MOCK_CONSCIOUSNESS_SERVICE_URL = "http://fake-consciousness-service:1234"

# Test data for market analysis
MOCK_MARKET_ANALYSIS_DATA = {"token": "ETH", "sentiment": "bullish", "price_target": 4000}
MOCK_MARKET_ANALYZER_SERVICE_URL = "http://fake-market-analyzer:5678"

# Test data for reasoning
MOCK_REASONING_PAYLOAD = {"prompt": "test prompt", "task_type": "test_task", "complexity": 1}
MOCK_REASONING_RESPONSE_DATA = {"request_id": "req_123", "content": "reasoned output"}
MOCK_REASONING_SERVICE_URL = "http://fake-reasoning-service:9012"


# === Tests for get_mcp_consciousness_state ===

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_consciousness_state_success(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.INFO)
    mock_get_url.return_value = MOCK_CONSCIOUSNESS_SERVICE_URL

    mock_response_data = MOCK_CONSCIOUSNESS_STATE_DATA

    async def mock_client_get(url, **kwargs):
        assert url == f"{MOCK_CONSCIOUSNESS_SERVICE_URL}/state"
        mock_resp = AsyncMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response_data
        return mock_resp

    with patch('httpx.AsyncClient.get', side_effect=mock_client_get):
        # Need to import the actual function to test
        from utils.mcp_clients import get_mcp_consciousness_state
        result = await get_mcp_consciousness_state()

    assert result == mock_response_data
    mock_get_url.assert_called_once()
    assert "Successfully fetched consciousness state." in caplog.text

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_consciousness_state_service_url_not_found(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.WARNING) # _get_service_url_from_registry logs a warning
    mock_get_url.return_value = None # Simulate service URL not found

    from utils.mcp_clients import get_mcp_consciousness_state
    result = await get_mcp_consciousness_state()

    assert result is None
    # The calling function get_mcp_consciousness_state itself doesn't log when service_url is None,
    # it relies on _get_service_url_from_registry to have logged the reason.
    # So, caplog might be empty or contain unrelated logs if other parts of the test setup log something.
    # The key is that the function correctly returns None. Logging for _get_service_url_from_registry
    # is tested separately.

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_consciousness_state_service_call_http_error(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.ERROR)
    mock_get_url.return_value = MOCK_CONSCIOUSNESS_SERVICE_URL

    # Mock the response object for HTTPStatusError
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 500
    mock_http_response.text = "Internal Server Error"

    with patch('httpx.AsyncClient.get', side_effect=httpx.HTTPStatusError("Service error", request=MagicMock(), response=mock_http_response)) as mock_actual_get:
        from utils.mcp_clients import get_mcp_consciousness_state
        result = await get_mcp_consciousness_state()

    assert result is None
    mock_actual_get.assert_called_once_with(f"{MOCK_CONSCIOUSNESS_SERVICE_URL}/state")
    assert "HTTP status error 500 for MCP Consciousness Layer (State): Internal Server Error" in caplog.text

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_consciousness_state_service_call_network_error(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.ERROR)
    mock_get_url.return_value = MOCK_CONSCIOUSNESS_SERVICE_URL

    with patch('httpx.AsyncClient.get', side_effect=httpx.RequestError("Network down", request=MagicMock())) as mock_actual_get:
        from utils.mcp_clients import get_mcp_consciousness_state
        result = await get_mcp_consciousness_state()

    assert result is None
    mock_actual_get.assert_called_once_with(f"{MOCK_CONSCIOUSNESS_SERVICE_URL}/state")
    assert "HTTP request error for MCP Consciousness Layer (State): Network down" in caplog.text

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_consciousness_state_invalid_json(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.ERROR)
    mock_get_url.return_value = MOCK_CONSCIOUSNESS_SERVICE_URL

    mock_service_response = AsyncMock(spec=httpx.Response)
    mock_service_response.status_code = 200
    mock_service_response.json.side_effect = json.JSONDecodeError("Bad JSON", "doc", 0)

    with patch('httpx.AsyncClient.get', return_value=mock_service_response) as mock_actual_get:
        from utils.mcp_clients import get_mcp_consciousness_state
        result = await get_mcp_consciousness_state()

    assert result is None
    mock_actual_get.assert_called_once_with(f"{MOCK_CONSCIOUSNESS_SERVICE_URL}/state")
    assert "Error decoding JSON response from MCP Consciousness Layer (State)" in caplog.text

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_consciousness_state_unexpected_data_type(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.WARNING) # This logs a warning
    mock_get_url.return_value = MOCK_CONSCIOUSNESS_SERVICE_URL

    mock_response_data = ["list", "instead", "of", "dict"] # Unexpected data type

    mock_service_response = AsyncMock(spec=httpx.Response)
    mock_service_response.status_code = 200
    mock_service_response.json.return_value = mock_response_data

    with patch('httpx.AsyncClient.get', return_value=mock_service_response):
        from utils.mcp_clients import get_mcp_consciousness_state
        result = await get_mcp_consciousness_state()

    assert result == mock_response_data # Function currently returns it
    assert f"Unexpected data format from MCP Consciousness Layer (State) at {MOCK_CONSCIOUSNESS_SERVICE_URL}/state. Expected dict, got <class 'list'>" in caplog.text


# === Tests for get_mcp_market_analysis ===

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_market_analysis_success(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.INFO)
    mock_get_url.return_value = MOCK_MARKET_ANALYZER_SERVICE_URL
    test_token = "ETH"

    async def mock_client_get(url, **kwargs):
        assert url == f"{MOCK_MARKET_ANALYZER_SERVICE_URL}/analysis/{test_token}"
        mock_resp = AsyncMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_MARKET_ANALYSIS_DATA
        return mock_resp

    with patch('httpx.AsyncClient.get', side_effect=mock_client_get):
        from utils.mcp_clients import get_mcp_market_analysis
        result = await get_mcp_market_analysis(test_token)

    assert result == MOCK_MARKET_ANALYSIS_DATA
    mock_get_url.assert_called_once()
    assert f"Successfully fetched market analysis for {test_token}." in caplog.text

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_market_analysis_service_url_not_found(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.WARNING)
    mock_get_url.return_value = None
    from utils.mcp_clients import get_mcp_market_analysis
    result = await get_mcp_market_analysis("ETH")
    assert result is None
    # Similar to the consciousness state test, the main function doesn't log here.
    # _get_service_url_from_registry's logging is tested separately.

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_market_analysis_service_call_http_error(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.ERROR)
    mock_get_url.return_value = MOCK_MARKET_ANALYZER_SERVICE_URL
    test_token = "BTC"

    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 503
    mock_http_response.text = "Service Unavailable"

    with patch('httpx.AsyncClient.get', side_effect=httpx.HTTPStatusError("Service down", request=MagicMock(), response=mock_http_response)) as mock_actual_get:
        from utils.mcp_clients import get_mcp_market_analysis
        result = await get_mcp_market_analysis(test_token)
    assert result is None
    mock_actual_get.assert_called_once_with(f"{MOCK_MARKET_ANALYZER_SERVICE_URL}/analysis/{test_token}")
    assert "HTTP status error 503 for MCP Market Analyzer: Service Unavailable" in caplog.text

# ... (similar tests for network error, invalid json, unexpected data type for market_analysis) ...
@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_market_analysis_invalid_json(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.ERROR)
    mock_get_url.return_value = MOCK_MARKET_ANALYZER_SERVICE_URL
    test_token = "ETH"
    mock_service_response = AsyncMock(spec=httpx.Response)
    mock_service_response.status_code = 200
    mock_service_response.json.side_effect = json.JSONDecodeError("Bad JSON", "doc", 0)
    with patch('httpx.AsyncClient.get', return_value=mock_service_response) as mock_actual_get:
        from utils.mcp_clients import get_mcp_market_analysis
        result = await get_mcp_market_analysis(test_token)
    assert result is None
    mock_actual_get.assert_called_once_with(f"{MOCK_MARKET_ANALYZER_SERVICE_URL}/analysis/{test_token}")
    assert "Error decoding JSON response from MCP Market Analyzer" in caplog.text

# === Tests for get_mcp_reasoning ===

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_reasoning_success(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.INFO)
    mock_get_url.return_value = MOCK_REASONING_SERVICE_URL

    async def mock_client_post(url, *, json: dict, **kwargs): # Corrected signature
        assert url == f"{MOCK_REASONING_SERVICE_URL}/reason"
        assert json == MOCK_REASONING_PAYLOAD
        mock_resp = AsyncMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = MOCK_REASONING_RESPONSE_DATA
        return mock_resp

    with patch('httpx.AsyncClient.post', side_effect=mock_client_post) as mock_post_method:
        from utils.mcp_clients import get_mcp_reasoning
        result = await get_mcp_reasoning(
            MOCK_REASONING_PAYLOAD["prompt"],
            MOCK_REASONING_PAYLOAD["task_type"],
            MOCK_REASONING_PAYLOAD["complexity"]
        )

    assert result == MOCK_REASONING_RESPONSE_DATA
    mock_get_url.assert_called_once()
    mock_post_method.assert_called_once()
    assert "Successfully received reasoning response." in caplog.text

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_reasoning_service_url_not_found(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.WARNING)
    mock_get_url.return_value = None
    from utils.mcp_clients import get_mcp_reasoning
    result = await get_mcp_reasoning("p", "t", 1)
    assert result is None
    # Similar to the other "service_url_not_found" tests.

@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_reasoning_service_call_http_error(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.ERROR)
    mock_get_url.return_value = MOCK_REASONING_SERVICE_URL

    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 500
    mock_http_response.text = "Server Error"

    with patch('httpx.AsyncClient.post', side_effect=httpx.HTTPStatusError("Service unavailable", request=MagicMock(), response=mock_http_response)) as mock_post_method:
        from utils.mcp_clients import get_mcp_reasoning
        result = await get_mcp_reasoning("p", "t", 1)
    assert result is None
    mock_post_method.assert_called_once()
    assert "HTTP status error 500 for MCP Reasoning Orchestrator: Server Error" in caplog.text

# ... (similar tests for network error, invalid json, unexpected data type for reasoning) ...
@pytest.mark.asyncio
@patch('utils.mcp_clients._get_service_url_from_registry', new_callable=AsyncMock)
async def test_get_mcp_reasoning_invalid_json(mock_get_url, caplog):
    import logging
    caplog.set_level(logging.ERROR)
    mock_get_url.return_value = MOCK_REASONING_SERVICE_URL
    mock_service_response = AsyncMock(spec=httpx.Response)
    mock_service_response.status_code = 200
    mock_service_response.json.side_effect = json.JSONDecodeError("Bad JSON", "doc", 0)
    with patch('httpx.AsyncClient.post', return_value=mock_service_response) as mock_post_method:
        from utils.mcp_clients import get_mcp_reasoning
        result = await get_mcp_reasoning("p", "t", 1)
    assert result is None
    mock_post_method.assert_called_once()
    assert "Error decoding JSON response from MCP Reasoning Orchestrator" in caplog.text
