import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

MCP_REGISTRY_URL = "http://mcp-registry:3001/registry"
# Assuming the service name in the registry will be one of these
EXPECTED_SERVICE_NAMES = ["mcp-consciousness-layer", "consciousness-layer", "consciousness"]
# Assuming the state endpoint on the consciousness service
CONSCIOUSNESS_STATE_ENDPOINT = "/state"
CONSCIOUSNESS_EMOTIONS_ENDPOINT = "/emotions"

# New Service Names and Endpoints
MCP_MARKET_ANALYZER_NAMES = ["mcp-market-analyzer", "market-analyzer-service", "market-analyzer"]
MARKET_ANALYSIS_ENDPOINT_TEMPLATE = "/analysis/{token}" # Example: /analysis/ETH or /analyze?token=ETH

MCP_REASONING_ORCHESTRATOR_NAMES = ["mcp-reasoning-orchestrator", "reasoning-service", "reasoning-engine"]
REASONING_ENDPOINT = "/reason" # Assuming POST request

MCP_STRATEGY_SPECIALIST_NAMES = ["mcp-specialist-service", "mcp-strategy-specialist", "strategy-specialist"]
STRATEGY_ENDPOINT = "/generate-strategy" # Assuming POST request

MCP_PORTFOLIO_OPTIMIZER_NAMES = ["mcp-portfolio-optimizer", "portfolio-optimizer-service", "portfolio-optimizer"]
PORTFOLIO_ENDPOINT = "/optimize-portfolio" # Assuming POST request

async def get_mcp_consciousness_state() -> Optional[Dict[str, Any]]:
    """
    Fetches the state from the MCP Consciousness Layer service.

    It first queries the MCP Registry to find the service URL, then queries
    the consciousness service for its state.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Querying MCP Registry at {MCP_REGISTRY_URL} for consciousness service.")
            response = await client.get(MCP_REGISTRY_URL)
            response.raise_for_status()
            registry_data = response.json()

            consciousness_service_url = None
            if "services" in registry_data and isinstance(registry_data["services"], dict):
                for service_name, service_info in registry_data["services"].items():
                    if service_name.lower() in EXPECTED_SERVICE_NAMES and isinstance(service_info, dict) and "url" in service_info:
                        consciousness_service_url = service_info["url"]
                        logger.info(f"Found MCP Consciousness Layer URL: {consciousness_service_url} (from service '{service_name}')")
                        break

            if not consciousness_service_url:
                logger.error("MCP Consciousness Layer service not found in registry.")
                return None

            target_url = f"{consciousness_service_url.rstrip('/')}{CONSCIOUSNESS_STATE_ENDPOINT}"
            logger.info(f"Fetching consciousness state from {target_url}")

            state_response = await client.get(target_url)
            state_response.raise_for_status()

            state_data = state_response.json()
            logger.info("Successfully fetched consciousness state.")
            return state_data

    except httpx.TimeoutException:
        logger.error(f"Timeout while trying to connect to MCP services (registry or consciousness layer).")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error while fetching consciousness state: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_consciousness_state: {e}")
        return None


async def get_mcp_market_emotions() -> Optional[Dict[str, Any]]:
    """
    Fetches the market emotions from the MCP Consciousness Layer service.

    It first queries the MCP Registry to find the service URL, then queries
    the consciousness service for its market emotions data.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Querying MCP Registry at {MCP_REGISTRY_URL} for consciousness service (for emotions).")
            response = await client.get(MCP_REGISTRY_URL)
            response.raise_for_status()
            registry_data = response.json()

            consciousness_service_url = None
            if "services" in registry_data and isinstance(registry_data["services"], dict):
                for service_name, service_info in registry_data["services"].items():
                    if service_name.lower() in EXPECTED_SERVICE_NAMES and isinstance(service_info, dict) and "url" in service_info:
                        consciousness_service_url = service_info["url"]
                        logger.info(f"Found MCP Consciousness Layer URL: {consciousness_service_url} (from service '{service_name}') for emotions.")
                        break

            if not consciousness_service_url:
                logger.error("MCP Consciousness Layer service not found in registry (for emotions).")
                return None

            target_url = f"{consciousness_service_url.rstrip('/')}{CONSCIOUSNESS_EMOTIONS_ENDPOINT}"
            logger.info(f"Fetching market emotions from {target_url}")

            emotions_response = await client.get(target_url)
            emotions_response.raise_for_status()

            emotions_data = emotions_response.json()
            logger.info("Successfully fetched market emotions.")
            return emotions_data

    except httpx.TimeoutException:
        logger.error(f"Timeout while trying to connect to MCP services (registry or consciousness layer for emotions).")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error while fetching market emotions: {e}")
        return None
    except json.JSONDecodeError as e: # Added import json at the top if not already there
        logger.error(f"Error decoding JSON response for market emotions: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_market_emotions: {e}")
        return None


async def get_mcp_market_analysis(token: str) -> Optional[Dict[str, Any]]:
    """
    Fetches market analysis for a given token from the MCP Market Analyzer service.
    """
    service_name_logging = "MCP Market Analyzer"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Querying MCP Registry for {service_name_logging} service.")
            registry_response = await client.get(MCP_REGISTRY_URL)
            registry_response.raise_for_status()
            registry_data = registry_response.json()

            service_url = None
            if "services" in registry_data and isinstance(registry_data["services"], dict):
                for s_name, s_info in registry_data["services"].items():
                    if s_name.lower() in MCP_MARKET_ANALYZER_NAMES and isinstance(s_info, dict) and "url" in s_info:
                        service_url = s_info["url"]
                        logger.info(f"Found {service_name_logging} URL: {service_url} (from service '{s_name}')")
                        break

            if not service_url:
                logger.error(f"{service_name_logging} service not found in registry.")
                return None

            # Construct target URL - assuming template like /analysis/{token}
            # If it's /analyze?token={token}, this needs adjustment:
            # target_url = f"{service_url.rstrip('/')}/analyze?token={token}"
            target_url = f"{service_url.rstrip('/')}{MARKET_ANALYSIS_ENDPOINT_TEMPLATE.format(token=token)}"
            logger.info(f"Fetching market analysis for {token} from {target_url}")

            analysis_response = await client.get(target_url)
            analysis_response.raise_for_status()

            analysis_data = analysis_response.json()
            logger.info(f"Successfully fetched market analysis for {token}.")
            return analysis_data

    except httpx.TimeoutException:
        logger.error(f"Timeout while trying to connect to {service_name_logging} or registry.")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error while fetching market analysis: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {service_name_logging}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_market_analysis: {e}")
        return None


async def get_mcp_reasoning(prompt: str, task_type: str = "general", complexity: int = 5) -> Optional[Dict[str, Any]]:
    """
    Gets a reasoning response from the MCP Reasoning Orchestrator.
    """
    service_name_logging = "MCP Reasoning Orchestrator"
    payload = {"prompt": prompt, "task_type": task_type, "complexity": complexity}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client: # Reasoning might take longer
            logger.info(f"Querying MCP Registry for {service_name_logging} service.")
            registry_response = await client.get(MCP_REGISTRY_URL)
            registry_response.raise_for_status()
            registry_data = registry_response.json()

            service_url = None
            if "services" in registry_data and isinstance(registry_data["services"], dict):
                for s_name, s_info in registry_data["services"].items():
                    if s_name.lower() in MCP_REASONING_ORCHESTRATOR_NAMES and isinstance(s_info, dict) and "url" in s_info:
                        service_url = s_info["url"]
                        logger.info(f"Found {service_name_logging} URL: {service_url} (from service '{s_name}')")
                        break

            if not service_url:
                logger.error(f"{service_name_logging} service not found in registry.")
                return None

            target_url = f"{service_url.rstrip('/')}{REASONING_ENDPOINT}"
            logger.info(f"Requesting reasoning from {target_url} with payload: {payload}")

            reasoning_response = await client.post(target_url, json=payload)
            reasoning_response.raise_for_status()

            response_data = reasoning_response.json()
            logger.info("Successfully received reasoning response.")
            return response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout while trying to connect to {service_name_logging} or registry.")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error while getting reasoning: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {service_name_logging}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_reasoning: {e}")
        return None


async def get_mcp_specialist_strategy(token: str, analysis: Dict[str, Any], risk_profile: str) -> Optional[Dict[str, Any]]:
    """
    Gets a trading strategy from the MCP Strategy Specialist.
    """
    service_name_logging = "MCP Strategy Specialist"
    payload = {"token": token, "analysis": analysis, "risk_profile": risk_profile}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            logger.info(f"Querying MCP Registry for {service_name_logging} service.")
            registry_response = await client.get(MCP_REGISTRY_URL)
            registry_response.raise_for_status()
            registry_data = registry_response.json()

            service_url = None
            if "services" in registry_data and isinstance(registry_data["services"], dict):
                for s_name, s_info in registry_data["services"].items():
                    if s_name.lower() in MCP_STRATEGY_SPECIALIST_NAMES and isinstance(s_info, dict) and "url" in s_info:
                        service_url = s_info["url"]
                        logger.info(f"Found {service_name_logging} URL: {service_url} (from service '{s_name}')")
                        break

            if not service_url:
                logger.error(f"{service_name_logging} service not found in registry.")
                return None

            target_url = f"{service_url.rstrip('/')}{STRATEGY_ENDPOINT}"
            logger.info(f"Requesting strategy from {target_url} for token {token}")

            strategy_response = await client.post(target_url, json=payload)
            strategy_response.raise_for_status()

            response_data = strategy_response.json()
            logger.info(f"Successfully received strategy for {token}.")
            return response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout while trying to connect to {service_name_logging} or registry.")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error while getting strategy: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {service_name_logging}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_specialist_strategy: {e}")
        return None


async def get_mcp_portfolio_optimization(current_token: str, risk_profile: str, market_conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Gets portfolio optimization advice from the MCP Portfolio Optimizer.
    """
    service_name_logging = "MCP Portfolio Optimizer"
    payload = {"current_token": current_token, "risk_profile": risk_profile, "market_conditions": market_conditions}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            logger.info(f"Querying MCP Registry for {service_name_logging} service.")
            registry_response = await client.get(MCP_REGISTRY_URL)
            registry_response.raise_for_status()
            registry_data = registry_response.json()

            service_url = None
            if "services" in registry_data and isinstance(registry_data["services"], dict):
                for s_name, s_info in registry_data["services"].items():
                    if s_name.lower() in MCP_PORTFOLIO_OPTIMIZER_NAMES and isinstance(s_info, dict) and "url" in s_info:
                        service_url = s_info["url"]
                        logger.info(f"Found {service_name_logging} URL: {service_url} (from service '{s_name}')")
                        break

            if not service_url:
                logger.error(f"{service_name_logging} service not found in registry.")
                return None

            target_url = f"{service_url.rstrip('/')}{PORTFOLIO_ENDPOINT}"
            logger.info(f"Requesting portfolio optimization from {target_url} for token {current_token}")

            optimization_response = await client.post(target_url, json=payload)
            optimization_response.raise_for_status()

            response_data = optimization_response.json()
            logger.info(f"Successfully received portfolio optimization for {current_token}.")
            return response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout while trying to connect to {service_name_logging} or registry.")
        return None
    except httpx.RequestError as e:
        logger.error(f"HTTP request error while getting portfolio optimization: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response from {service_name_logging}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_mcp_portfolio_optimization: {e}")
        return None


if __name__ == '__main__':
    import asyncio
    import json # Make sure json is imported for JSONDecodeError

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
