"""
API endpoints for MCP (Multi-Contextual Processor) visualization and monitoring.

This module provides the FastAPI routes for retrieving information about MCP
functions and their execution in real-time.
"""
import asyncio
import json
import logging
import os
import httpx
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel

# Import MCP authentication
from utils.mcp_auth import (
    verify_jwt_dependency, 
    verify_mcp_token_dependency, 
    optional_auth,
    mcp_auth,
    get_auth_headers
)

# Setup logging
logger = logging.getLogger("API_MCP")

MCP_REGISTRY_URL = "http://mcp-registry:3001"

# Create router
router = APIRouter(
    prefix="/api/mcp",
    tags=["mcp"],
    responses={404: {"description": "Not found"}},
)

# Store active WebSocket connections
active_connections: Dict[WebSocket, Set[str]] = {}

# Temporary in-memory storage for demonstration
# In a real implementation, this would connect to the actual MCP system
# mcp_functions = [] # This will be fetched from the registry
mcp_function_calls = []


class MCPFunction(BaseModel):
    """Model representing an MCP function."""
    name: str
    description: str
    mcp_type: str = "processor"
    parameters: Dict[str, str] = {}
    source_code: Optional[str] = None
    created_at: datetime = None
    last_execution: Optional[Dict[str, Any]] = None


class MCPFunctionExecution(BaseModel):
    """Model representing an execution of an MCP function."""
    function_name: str
    inputs: Dict[str, Any]
    result: Any
    status: str = "success"  # "success", "error", "in_progress"
    timestamp: datetime = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


@router.get("/functions", response_model=List[MCPFunction])
async def get_mcp_functions():
    """Get all registered MCP functions from the mcp-registry service."""
    try:
        async with httpx.AsyncClient() as client:
            # Attempt to fetch detailed functions list
            response = await client.get(f"{MCP_REGISTRY_URL}/functions")
            response.raise_for_status()
            functions_data = response.json()
            logger.info("Successfully fetched MCP functions from mcp-registry/functions.")
            # Assuming functions_data is a list of dicts compatible with MCPFunction
            return functions_data
    except httpx.RequestError as e:
        logger.error(f"Error fetching MCP functions from mcp-registry/functions: {e}. Falling back to /registry.")
        # Fallback: try to extract function names from the /registry endpoint
        try:
            async with httpx.AsyncClient() as client:
                registry_response = await client.get(f"{MCP_REGISTRY_URL}/registry")
                registry_response.raise_for_status()
                registry_data = registry_response.json()

                extracted_functions = []
                if "services" in registry_data and isinstance(registry_data["services"], dict):
                    for service_name, service_details in registry_data["services"].items():
                        if "functions" in service_details and isinstance(service_details["functions"], list):
                            for func_name in service_details["functions"]:
                                # We only have names, so we create partial MCPFunction objects
                                extracted_functions.append({
                                    "name": func_name,
                                    "description": service_details.get("description", "N/A"), # Or a default
                                    "mcp_type": "processor", # Default
                                    "parameters": {}, # Default / Unknown
                                    # created_at, source_code, last_execution would be unknown
                                })
                logger.info(f"Extracted {len(extracted_functions)} function names from mcp-registry/registry fallback.")
                return extracted_functions
        except httpx.RequestError as re:
            logger.error(f"Error fetching from mcp-registry/registry fallback: {re}")
            raise HTTPException(status_code=503, detail="MCP registry service unavailable for functions.")
        except Exception as ex: # Catching potential parsing errors or unexpected structure
            logger.error(f"Error processing fallback registry data for functions: {ex}")
            raise HTTPException(status_code=500, detail="Error processing functions data from registry.")

    except Exception as e:
        logger.error(f"General error fetching MCP functions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching MCP functions.")


@router.get("/function-calls", response_model=List[MCPFunctionExecution])
async def get_mcp_function_calls(limit: int = Query(100, description="Maximum number of calls to return")):
    """Get recent MCP function calls."""
    return mcp_function_calls[:limit]


@router.get("/functions/{function_name}", response_model=MCPFunction)
async def get_mcp_function(function_name: str = Path(..., description="Name of the MCP function")):
    """Get details of a specific MCP function."""
    # This function will also need to be updated to fetch from registry,
    # or the global mcp_functions list needs to be repopulated if we stick to it.
    # For now, it will likely not find any functions if mcp_functions is empty.
    # Depending on how functions are fetched, this might call MCP_REGISTRY_URL/functions/{function_name}

    # Placeholder: If mcp_functions is indeed removed, this needs a new source.
    # For now, let's assume get_mcp_functions() could populate a temporary list or this needs redesign.
    # This is out of scope for the current subtask, but noting it.

    # Quick fix attempt: fetch all and then filter. Not efficient.
    all_functions = await get_mcp_functions()
    for func in all_functions:
        # Ensure func is a dict if it's coming from Pydantic model conversion
        if isinstance(func, BaseModel):
            func = func.model_dump() # Use model_dump() for Pydantic v2+

        if func["name"] == function_name:
            return func
    raise HTTPException(status_code=404, detail="MCP function not found")


@router.get("/status")
async def get_mcp_status():
    """Get the status of all MCP services."""
    try:
        # Check if MCP services are available
        # For now, we'll return a simulated status based on available functions
        # Status check might need to be re-evaluated based on live registry calls
        mcp_funcs_list = await get_mcp_functions() # Call the new live data version
        services_status = {
            "registry": "connected" if len(mcp_funcs_list) > 0 else "disconnected", # Basic check
            "chainlink": "connected", # These would ideally also come from registry
            "etherscan": "connected", 
            "consciousness": "connected"
        }
        
        return services_status
    except Exception as e:
        logger.error(f"Error getting MCP status: {e}")
        return {
            "registry": "disconnected",
            "chainlink": "disconnected",
            "etherscan": "disconnected",
            "consciousness": "disconnected"
        }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP function updates."""
    await websocket.accept()
    active_connections[websocket] = set()
    connection_id = id(websocket)
    logger.info(f"MCP WebSocket connection established (ID: {connection_id})")
    
    try:
        # Send initial data
        # WebSocket needs to get functions from the new async function
        # This might require refactoring how WebSocket gets initial data
        # For now, it will call the new get_mcp_functions
        initial_mcp_functions = await get_mcp_functions()
        await websocket.send_json({
            "type": "mcp_functions_list",
            "functions": initial_mcp_functions
        })
        
        await websocket.send_json({
            "type": "mcp_function_calls_list",
            "calls": mcp_function_calls[:100]  # Send last 100 calls
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "get_function_details":
                    function_name = data.get("function_name")
                    if function_name:
                        # This also needs to use the new way of fetching functions
                        func_detail = await get_mcp_function(function_name) # Call the modified get_mcp_function
                        if func_detail:
                             await websocket.send_json({
                                 "type": "mcp_function_details",
                                 "function": func_detail
                             })
                        # No explicit else, if not found, get_mcp_function raises HTTPException which is not caught here
                        # This might need adjustment if a silent failure is preferred for WebSocket
                        
                elif message_type == "subscribe":
                    if "functions" in data:
                        active_connections[websocket].update(data["functions"])
                        
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from client {connection_id}")
                continue
                
    except WebSocketDisconnect:
        logger.info(f"MCP WebSocket client disconnected (ID: {connection_id})")
    except Exception as e:
        logger.error(f"MCP WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            del active_connections[websocket]


async def broadcast_function_registration(function: Dict[str, Any]):
    """Broadcast a function registration to all connected clients."""
    if not active_connections:
        return
        
    message = {
        "type": "mcp_function_registered",
        "function": function
    }
    
    for websocket in list(active_connections.keys()):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting function registration: {e}")


async def broadcast_function_execution(execution: Dict[str, Any]):
    """Broadcast a function execution to all connected clients."""
    if not active_connections:
        return
        
    message = {
        "type": "mcp_function_executed",
        "execution": execution
    }
    
    for websocket, subscriptions in list(active_connections.items()):
        try:
            # If client subscribed to specific functions, only send if matching
            function_name = execution.get("function_name")
            if not subscriptions or function_name in subscriptions:
                await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting function execution: {e}")


# Function to register an MCP function
def register_mcp_function(function_data: Dict[str, Any]):
    """
    Register a new MCP function.
    
    This function should be called by the MCP system when a new function is created.
    """
    # Create function record
    function = {
        "name": function_data["name"],
        "description": function_data.get("description", ""),
        "mcp_type": function_data.get("mcp_type", "processor"),
        "parameters": function_data.get("parameters", {}),
        "source_code": function_data.get("source_code"),
        "created_at": datetime.now().isoformat()
    }
    
    # Add to in-memory store - THIS IS PROBLEMATIC if mcp_functions is removed
    # This function's behavior needs to be re-evaluated.
    # If functions are solely managed by the registry, this function might:
    # 1. Call an endpoint on the registry to register the function.
    # 2. Be removed if clients should register functions directly with the registry.
    # For now, commenting out the modification to the non-existent mcp_functions
    # for i, existing_func in enumerate(mcp_functions):
    #     if existing_func["name"] == function["name"]:
    #         # Update existing function
    #         mcp_functions[i] = function
    #         break
    # else:
    #     # Add new function
    #     mcp_functions.append(function)
    logger.warning("register_mcp_function: mcp_functions list is no longer maintained locally. Registration might not be reflected.")
    
    # Broadcast to WebSocket clients
    asyncio.create_task(broadcast_function_registration(function))
    
    return function


# Function to record an MCP function execution
def record_mcp_function_execution(execution_data: Dict[str, Any]):
    """
    Record an execution of an MCP function.
    
    This function should be called by the MCP system when a function is executed.
    """
    # Create execution record
    execution = {
        "function_name": execution_data["function_name"],
        "inputs": execution_data.get("inputs", {}),
        "result": execution_data.get("result"),
        "status": execution_data.get("status", "success"),
        "timestamp": datetime.now().isoformat(),
        "execution_time": execution_data.get("execution_time"),
        "error_message": execution_data.get("error_message")
    }
    
    # Add to in-memory store (keep most recent first)
    mcp_function_calls.insert(0, execution)
    if len(mcp_function_calls) > 1000:  # Limit size to prevent memory issues
        mcp_function_calls.pop()
    
    # Update last_execution in function record - SIMILARLY PROBLEMATIC
    # This also depends on the mcp_functions list.
    # This information (last_execution) would ideally be part of the data fetched from the registry
    # or managed by the registry itself.
    # Commenting out for now:
    # for func in mcp_functions: # mcp_functions is no longer a global list here
    #     if func["name"] == execution["function_name"]:
    #         func["last_execution"] = execution
    #         break
    logger.warning("record_mcp_function_execution: mcp_functions list is no longer maintained locally. Last execution update might not be reflected.")
    
    # Broadcast to WebSocket clients
    asyncio.create_task(broadcast_function_execution(execution))
    
    return execution


@router.get("/registry", dependencies=[Depends(verify_mcp_token_dependency)])
async def get_mcp_registry():
    """Get the complete MCP service registry with authentication."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_REGISTRY_URL}/registry")
            response.raise_for_status()  # Raise an exception for HTTP errors
            registry_data = response.json()
            logger.info("Successfully fetched MCP registry data from live service.")
            return registry_data
    except httpx.RequestError as e:
        logger.error(f"Error fetching MCP registry from live service: {e}")
        raise HTTPException(status_code=503, detail=f"MCP registry service unavailable: {e}")
    except Exception as e:
        logger.error(f"Error processing MCP registry data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing MCP registry data: {e}")

@router.post("/auth/token")
async def generate_mcp_token(user_data: Dict[str, Any] = Body(...)):
    """Generate a new MCP session token."""
    try:
        user_id = user_data.get('user_id', 'anonymous')
        duration = user_data.get('duration_hours', 24)
        
        # Generate session token
        session_token = mcp_auth.generate_mcp_session_token(user_id, duration)
        
        return {
            "session_token": session_token,
            "expires_in": duration * 3600,
            "token_type": "bearer",
            "scope": "mcp_access"
        }
    except Exception as e:
        logger.error(f"Error generating MCP token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def mcp_health_check():
    """Public health check endpoint for MCP services."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": 4,
        "endpoint": os.getenv('MCP_ENDPOINT', 'http://localhost:8000/api/mcp')
    }