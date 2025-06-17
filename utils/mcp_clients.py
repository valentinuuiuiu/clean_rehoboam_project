import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

MCP_REGISTRY_URL = "http://mcp-registry:3001/registry"
from typing import Optional, Dict, Any, List # Ensure List is imported
import json # Ensure json is imported for logging

logger = logging.getLogger(__name__)

MCP_REGISTRY_URL = "http://mcp-registry:3001/registry"

# Service name constants
CONSCIOUSNESS_SERVICE_NAMES = ["mcp-consciousness-layer", "consciousness-layer", "consciousness"]
MARKET_ANALYZER_SERVICE_NAMES = ["mcp-market-analyzer", "market-analyzer-service", "market-analyzer"]
REASONING_ORCHESTRATOR_SERVICE_NAMES = ["mcp-reasoning-orchestrator", "reasoning-service", "reasoning-engine"]
STRATEGY_SPECIALIST_SERVICE_NAMES = ["mcp-specialist-service", "mcp-strategy-specialist", "strategy-specialist"]
PORTFOLIO_OPTIMIZER_SERVICE_NAMES = ["mcp-portfolio-optimizer", "portfolio-optimizer-service", "portfolio-optimizer"]

# Endpoint constants
CONSCIOUSNESS_STATE_ENDPOINT = "/state"
CONSCIOUSNESS_EMOTIONS_ENDPOINT = "/emotions"

# Debug flag for logging registry responses
DEBUG_LOG_REGISTRY_RESPONSE = False
MARKET_ANALYSIS_ENDPOINT_TEMPLATE = "/analysis/{token}"
REASONING_ENDPOINT = "/reason"
STRATEGY_ENDPOINT = "/generate-strategy"
PORTFOLIO_ENDPOINT = "/optimize-portfolio"


async def _get_service_url_from_registry(client: httpx.AsyncClient, service_names_to_find: List[str], log_service_prefix: str) -> Optional[str]:
    """
    Helper function to query the MCP registry and find a service URL.
    """
    logger.info(f"Querying MCP Registry at {MCP_REGISTRY_URL} for {log_service_prefix} (candidates: {service_names_to_find}).")
    try:
        registry_response = await client.get(f"{MCP_REGISTRY_URL}/registry") # Corrected URL construction
        registry_response.raise_for_status()
        registry_data = registry_response.json()

        if DEBUG_LOG_REGISTRY_RESPONSE:
            try:
                logger.debug(f"MCP Registry raw response for {log_service_prefix}: {json.dumps(registry_data, indent=2)}")
            except TypeError:
                logger.debug(f"MCP Registry raw response (non-serializable) for {log_service_prefix}: {registry_data}")

        services_dict = None
        if "services" in registry_data and isinstance(registry_data["services"], dict):
            services_dict = registry_data["services"]
        elif isinstance(registry_data, dict) and not any(key in registry_data for key in ["services", "error", "message"]): # If no 'services' and not an error structure, assume flat map
            # This condition might need refinement based on actual flat structures encountered
            logger.debug(f"No 'services' key found; attempting to use root of registry_data as service map for {log_service_prefix}.")
            services_dict = registry_data

        if services_dict is not None:
            for service_key_to_find in service_names_to_find: # Iterate through desired names first
                for reg_service_name, service_info in services_dict.items():
                    if service_key_to_find.lower() == reg_service_name.lower():
                        if isinstance(service_info, dict):
                            service_url = service_info.get("url")
                            if service_url is None:
                                logger.warning(f"Service '{reg_service_name}' URL is None in MCP registry for {log_service_prefix}.")
                                continue # Try other aliases or registry entries
                            if not service_url: # Empty string
                                logger.warning(f"Service '{reg_service_name}' URL is empty in MCP registry for {log_service_prefix}.")
                                continue # Treat empty URL as invalid
                            logger.info(f"Found {log_service_prefix} URL: {service_url} (matched '{service_key_to_find}' with registry key '{reg_service_name}')")
                            return service_url
                        else:
                            logger.warning(f"Service entry for '{reg_service_name}' in MCP registry is not a dictionary for {log_service_prefix}.")
            logger.warning(f"Service names {service_names_to_find} not found in MCP Registry for {log_service_prefix} with valid URL.")
        else:
            logger.warning(f"MCP registry data does not contain 'services' key or it's not a dictionary for {log_service_prefix}.")

        return None

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching MCP registry for {log_service_prefix}: {str(e)}") # Simplified log
        return None # Do not re-raise, handle locally and return None
    except httpx.RequestError as e:
        logger.error(f"Network error fetching MCP registry for {log_service_prefix}: {str(e)}")
        return None # Do not re-raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding MCP registry JSON for {log_service_prefix}: {str(e)}")
        return None # Do not re-raise
    except Exception as e:
        logger.error(f"Unexpected error fetching MCP registry for {log_service_prefix}: {str(e)}")
        return None # Do not re-raise


async def get_mcp_consciousness_state() -> Optional[Dict[str, Any]]:
    """
    Fetches the state from the MCP Consciousness Layer service.
    """
    log_service_prefix = "MCP Consciousness Layer (State)"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            service_url = await _get_service_url_from_registry(client, CONSCIOUSNESS_SERVICE_NAMES, log_service_prefix)
            if not service_url: # Error already logged by _get_service_url_from_registry
                return None

            target_url = f"{service_url.rstrip('/')}{CONSCIOUSNESS_STATE_ENDPOINT}"
            logger.info(f"Fetching consciousness state from {target_url}")

            state_response = await client.get(target_url)
            state_response.raise_for_status()

            state_data = state_response.json()
            if not isinstance(state_data, dict):
                logger.warning(f"Unexpected data format from {log_service_prefix} at {target_url}. Expected dict, got {type(state_data)}.")
                # Optionally, return None or raise an error if format is critical
            else:
                logger.info("Successfully fetched consciousness state.")
            return state_data

    except httpx.TimeoutException:
        logger.error(f"Timeout during request to {log_service_prefix} or its registry lookup.")
        return None
    except httpx.HTTPStatusError as e: # Catch HTTPStatusError first
        logger.error(f"HTTP status error {e.response.status_code} for {log_service_prefix}: {e.response.text[:200]}")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error for {log_service_prefix}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {log_service_prefix}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_consciousness_state: {e}")
        return None


async def get_mcp_market_emotions() -> Optional[Dict[str, Any]]:
    """
    Fetches the market emotions from the MCP Consciousness Layer service.
    """
    log_service_prefix = "MCP Consciousness Layer (Emotions)"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            service_url = await _get_service_url_from_registry(client, CONSCIOUSNESS_SERVICE_NAMES, log_service_prefix)
            if not service_url: # Error already logged by _get_service_url_from_registry
                return None

            target_url = f"{service_url.rstrip('/')}{CONSCIOUSNESS_EMOTIONS_ENDPOINT}"
            logger.info(f"Fetching market emotions from {target_url}")

            emotions_response = await client.get(target_url)
            emotions_response.raise_for_status()

            emotions_data = emotions_response.json()
            if not isinstance(emotions_data, dict):
                logger.warning(f"Unexpected data format from {log_service_prefix} at {target_url}. Expected dict, got {type(emotions_data)}.")
                # Optionally, return None or raise an error
            else:
                logger.info("Successfully fetched market emotions.")
            return emotions_data

    except httpx.TimeoutException:
        logger.error(f"Timeout during request to {log_service_prefix} or its registry lookup.")
        return None
    except httpx.HTTPStatusError as e: # Catch HTTPStatusError first
        logger.error(f"HTTP status error {e.response.status_code} for {log_service_prefix}: {e.response.text[:200]}")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error for {log_service_prefix}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {log_service_prefix}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_market_emotions: {e}")
        return None


async def get_mcp_market_analysis(token: str) -> Optional[Dict[str, Any]]:
    """
    Fetches market analysis for a given token from the MCP Market Analyzer service.
    """
    log_service_prefix = "MCP Market Analyzer"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            service_url = await _get_service_url_from_registry(client, MARKET_ANALYZER_SERVICE_NAMES, log_service_prefix)
            if not service_url: # Error already logged by _get_service_url_from_registry
                return None

            target_url = f"{service_url.rstrip('/')}{MARKET_ANALYSIS_ENDPOINT_TEMPLATE.format(token=token)}"
            logger.info(f"Fetching market analysis for {token} from {target_url}")

            analysis_response = await client.get(target_url)
            analysis_response.raise_for_status()

            analysis_data = analysis_response.json()
            if not isinstance(analysis_data, dict):
                logger.warning(f"Unexpected data format from {log_service_prefix} for {token} at {target_url}. Expected dict, got {type(analysis_data)}.")
            else:
                logger.info(f"Successfully fetched market analysis for {token}.")
            return analysis_data

    except httpx.TimeoutException:
        logger.error(f"Timeout during request to {log_service_prefix} or its registry lookup.")
        return None
    except httpx.HTTPStatusError as e: # Catch HTTPStatusError first
        logger.error(f"HTTP status error {e.response.status_code} for {log_service_prefix}: {e.response.text[:200]}")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error for {log_service_prefix}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {log_service_prefix}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_market_analysis: {e}")
        return None


async def get_mcp_reasoning(prompt: str, task_type: str = "general", complexity: int = 5) -> Optional[Dict[str, Any]]:
    """
    Gets a reasoning response from the MCP Reasoning Orchestrator.
    """
    log_service_prefix = "MCP Reasoning Orchestrator"
    payload = {"prompt": prompt, "task_type": task_type, "complexity": complexity}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client: # Reasoning might take longer
            service_url = await _get_service_url_from_registry(client, REASONING_ORCHESTRATOR_SERVICE_NAMES, log_service_prefix)
            if not service_url: # Error already logged by _get_service_url_from_registry
                return None

            target_url = f"{service_url.rstrip('/')}{REASONING_ENDPOINT}"
            logger.info(f"Requesting reasoning from {target_url} with payload: {payload}")

            reasoning_response = await client.post(target_url, json=payload)
            reasoning_response.raise_for_status()

            response_data = reasoning_response.json()
            if not isinstance(response_data, dict):
                logger.warning(f"Unexpected data format from {log_service_prefix} at {target_url}. Expected dict, got {type(response_data)}.")
            else:
                logger.info("Successfully received reasoning response.")
            return response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout during request to {log_service_prefix} or its registry lookup.")
        return None
    except httpx.HTTPStatusError as e: # Catch HTTPStatusError first
        logger.error(f"HTTP status error {e.response.status_code} for {log_service_prefix}: {e.response.text[:200]}")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error for {log_service_prefix}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {log_service_prefix}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_reasoning: {e}")
        return None


async def get_mcp_specialist_strategy(token: str, analysis: Dict[str, Any], risk_profile: str) -> Optional[Dict[str, Any]]:
    """
    Gets a trading strategy from the MCP Strategy Specialist.
    """
    log_service_prefix = "MCP Strategy Specialist"
    payload = {"token": token, "analysis": analysis, "risk_profile": risk_profile}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            service_url = await _get_service_url_from_registry(client, STRATEGY_SPECIALIST_SERVICE_NAMES, log_service_prefix)
            if not service_url: # Error already logged by _get_service_url_from_registry
                return None

            target_url = f"{service_url.rstrip('/')}{STRATEGY_ENDPOINT}"
            logger.info(f"Requesting strategy from {target_url} for token {token}")

            strategy_response = await client.post(target_url, json=payload)
            strategy_response.raise_for_status()

            response_data = strategy_response.json()
            if not isinstance(response_data, dict):
                logger.warning(f"Unexpected data format from {log_service_prefix} for {token} at {target_url}. Expected dict, got {type(response_data)}.")
            else:
                logger.info(f"Successfully received strategy for {token}.")
            return response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout during request to {log_service_prefix} or its registry lookup.")
        return None
    except httpx.HTTPStatusError as e: # Catch HTTPStatusError first
        logger.error(f"HTTP status error {e.response.status_code} for {log_service_prefix}: {e.response.text[:200]}")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error for {log_service_prefix}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {log_service_prefix}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_specialist_strategy: {e}")
        return None


async def get_mcp_portfolio_optimization(current_token: str, risk_profile: str, market_conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Gets portfolio optimization advice from the MCP Portfolio Optimizer.
    """
    log_service_prefix = "MCP Portfolio Optimizer"
    payload = {"current_token": current_token, "risk_profile": risk_profile, "market_conditions": market_conditions}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            service_url = await _get_service_url_from_registry(client, PORTFOLIO_OPTIMIZER_SERVICE_NAMES, log_service_prefix)
            if not service_url: # Error already logged by _get_service_url_from_registry
                return None

            target_url = f"{service_url.rstrip('/')}{PORTFOLIO_ENDPOINT}"
            logger.info(f"Requesting portfolio optimization from {target_url} for token {current_token}")

            optimization_response = await client.post(target_url, json=payload)
            optimization_response.raise_for_status()

            response_data = optimization_response.json()
            if not isinstance(response_data, dict):
                logger.warning(f"Unexpected data format from {log_service_prefix} for {current_token} at {target_url}. Expected dict, got {type(response_data)}.")
            else:
                logger.info(f"Successfully received portfolio optimization for {current_token}.")
            return response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout during request to {log_service_prefix} or its registry lookup.")
        return None
    except httpx.HTTPStatusError as e: # Catch HTTPStatusError first
        logger.error(f"HTTP status error {e.response.status_code} for {log_service_prefix}: {e.response.text[:200]}")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error for {log_service_prefix}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {log_service_prefix}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_portfolio_optimization: {e}")
        return None


if __name__ == '__main__':
    import asyncio
    # import json # Make sure json is imported for JSONDecodeError (already at top)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    async def main():
        print("--- Testing get_mcp_consciousness_state ---")
        state = await get_mcp_consciousness_state()
        if state:
            print("Consciousness State:", json.dumps(state, indent=2))
        else:
            print("Failed to retrieve consciousness state.")

        print("\n--- Testing get_mcp_market_emotions ---")
        emotions = await get_mcp_market_emotions()
        if emotions:
            print("Market Emotions:", json.dumps(emotions, indent=2))
        else:
            print("Failed to retrieve market emotions.")

        print("\n--- Testing get_mcp_market_analysis ---")
        # Assuming mcp-market-analyzer service is running and has an ETH endpoint
        analysis_eth = await get_mcp_market_analysis(token="ETH")
        if analysis_eth:
            print("Market Analysis (ETH):", json.dumps(analysis_eth, indent=2))
        else:
            print("Failed to retrieve market analysis for ETH.")

        print("\n--- Testing get_mcp_reasoning ---")
        reasoning_resp = await get_mcp_reasoning(prompt="Explain the concept of Layer 2 rollups.", task_type="explanation", complexity=3)
        if reasoning_resp:
            print("Reasoning Response:", json.dumps(reasoning_resp, indent=2))
        else:
            print("Failed to retrieve reasoning response.")

        print("\n--- Testing get_mcp_specialist_strategy ---")
        # Dummy analysis data for testing
        dummy_analysis = {"sentiment": "bullish", "key_levels": {"support": "3000", "resistance": "3500"}}
        strategy_resp = await get_mcp_specialist_strategy(token="BTC", analysis=dummy_analysis, risk_profile="moderate")
        if strategy_resp:
            print("Specialist Strategy (BTC):", json.dumps(strategy_resp, indent=2))
        else:
            print("Failed to retrieve specialist strategy for BTC.")

        print("\n--- Testing get_mcp_portfolio_optimization ---")
        dummy_market_conditions = {"volatility": "high", "trend": "uptrend"}
        portfolio_resp = await get_mcp_portfolio_optimization(current_token="ETH", risk_profile="aggressive", market_conditions=dummy_market_conditions)
        if portfolio_resp:
            print("Portfolio Optimization (ETH):", json.dumps(portfolio_resp, indent=2))
        else:
            print("Failed to retrieve portfolio optimization for ETH.")

    asyncio.run(main())
