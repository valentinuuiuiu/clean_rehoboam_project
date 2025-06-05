"""
API endpoints for MCP (Multi-Contextual Processor) visualization and monitoring.

This module provides the FastAPI routes for retrieving information about MCP
functions and their execution in real-time.
"""
import asyncio
import json
import logging
import os
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
mcp_functions = []
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
    """Get all registered MCP functions."""
    return mcp_functions


@router.get("/function-calls", response_model=List[MCPFunctionExecution])
async def get_mcp_function_calls(limit: int = Query(100, description="Maximum number of calls to return")):
    """Get recent MCP function calls."""
    return mcp_function_calls[:limit]


@router.get("/functions/{function_name}", response_model=MCPFunction)
async def get_mcp_function(function_name: str = Path(..., description="Name of the MCP function")):
    """Get details of a specific MCP function."""
    for func in mcp_functions:
        if func["name"] == function_name:
            return func
    raise HTTPException(status_code=404, detail="MCP function not found")


@router.get("/status")
async def get_mcp_status():
    """Get the status of all MCP services."""
    try:
        # Check if MCP services are available
        # For now, we'll return a simulated status based on available functions
        services_status = {
            "registry": "connected" if len(mcp_functions) > 0 else "disconnected",
            "chainlink": "connected",
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
        await websocket.send_json({
            "type": "mcp_functions_list",
            "functions": mcp_functions
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
                        for func in mcp_functions:
                            if func["name"] == function_name:
                                await websocket.send_json({
                                    "type": "mcp_function_details",
                                    "function": func
                                })
                                break
                        
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
    
    # Add to in-memory store
    for i, existing_func in enumerate(mcp_functions):
        if existing_func["name"] == function["name"]:
            # Update existing function
            mcp_functions[i] = function
            break
    else:
        # Add new function
        mcp_functions.append(function)
    
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
    
    # Update last_execution in function record
    for func in mcp_functions:
        if func["name"] == execution["function_name"]:
            func["last_execution"] = execution
            break
    
    # Broadcast to WebSocket clients
    asyncio.create_task(broadcast_function_execution(execution))
    
    return execution


@router.get("/registry", dependencies=[Depends(verify_mcp_token_dependency)])
async def get_mcp_registry():
    """Get the complete MCP service registry with authentication."""
    try:
        # Return comprehensive MCP registry
        registry = {
            "services": {
                "chainlink-feeds": {
                    "url": "http://localhost:8001",
                    "status": "active",
                    "functions": ["get_price", "get_price_history", "get_supported_tokens"],
                    "description": "Chainlink oracle price feeds service"
                },
                "consciousness-layer": {
                    "url": "http://localhost:8002", 
                    "status": "active",
                    "functions": ["analyze_consciousness", "process_quantum_state", "sync_network"],
                    "description": "Rehoboam consciousness and quantum processing"
                },
                "etherscan-analyzer": {
                    "url": "http://localhost:8003",
                    "status": "active", 
                    "functions": ["analyze_transaction", "get_contract_info", "get_wallet_history"],
                    "description": "Ethereum blockchain analysis via Etherscan"
                },
                "vetal-foundry-forge": {
                    "url": "http://localhost:8004",
                    "status": "active",
                    "functions": ["deploy_contract", "test_contract", "verify_contract"],
                    "description": "Solidity contract development and deployment"
                }
            },
            "endpoint": os.getenv('MCP_ENDPOINT', 'http://localhost:8000/api/mcp'),
            "authentication": {
                "required": True,
                "type": "token",
                "header": "X-MCP-Token"
            },
            "updated_at": datetime.utcnow().isoformat()
        }
        return registry
    except Exception as e:
        logger.error(f"Error getting MCP registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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