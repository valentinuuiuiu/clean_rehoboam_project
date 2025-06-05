"""
API Server endpoints for AI Companion Creator

This module provides the FastAPI routes for creating and interacting with
AI companions using Rehoboam's MCP capabilities.
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, Depends, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils.rehoboam_ai import RehoboamAI
from utils.ai_companion_creator import AICompanionCreator, CompanionCharacter

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API_Companions")

# Initialize the AI Companion Creator with enhanced consciousness
# This will be initialized from the main API server's consciousness layers
rehoboam = None
companion_creator = None

def initialize_companion_system(rehoboam_instance, companion_creator_instance):
    """Initialize the companion system with consciousness layers from main API."""
    global rehoboam, companion_creator
    rehoboam = rehoboam_instance
    companion_creator = companion_creator_instance
    logger.info("Companion system initialized with Rehoboam consciousness")

# Create router with redirect_slashes=False to prevent 307 redirects
router = APIRouter(prefix="/api/companions", tags=["companions"], redirect_slashes=False)

# Fixed configuration to prevent automatic redirects
# FastAPI will not automatically redirect between /api/companions and /api/companions/ now

# Keep track of active WebSocket connections
active_connections: List[WebSocket] = []

# Connected sessions keyed by session_id
connected_sessions: Dict[str, Dict[str, Any]] = {}


# Models for request/response
class CompanionCreate(BaseModel):
    """Model for companion creation request."""
    name: str
    themes: List[str]
    archetypes: List[str]
    complexity: float = 0.7


class CompanionInteract(BaseModel):
    """Model for companion interaction request."""
    message: str
    session_id: Optional[str] = "default"


class CompanionEvolve(BaseModel):
    """Model for companion evolution request."""
    session_id: Optional[str] = "default"


class BackstoryGenerate(BaseModel):
    """Model for backstory generation request."""
    character_name: str
    character_traits: List[Dict[str, Any]]
    cultural_influences: List[str]
    story_depth: float = 0.7
    key_events: Optional[List[str]] = None


@router.get("")
async def get_companions():
    """
    Get all available companions.
    Accessible via /api/companions with no trailing slash.
    """
    try:
        logger.info("Fetching all companions")
        companions_list = list(companion_creator.characters.values())
        logger.info(f"Found {len(companions_list)} companions")
        return companions_list
    except Exception as e:
        logger.error(f"Error getting companions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}")
async def get_companion(name: str):
    """Get a specific companion by name."""
    try:
        if name not in companion_creator.characters:
            raise HTTPException(status_code=404, detail=f"Companion '{name}' not found")
        
        return companion_creator.characters[name]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting companion {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
async def create_companion(companion: CompanionCreate):
    """Create a new AI companion."""
    try:
        # Check if companion already exists
        if companion.name in companion_creator.characters:
            raise HTTPException(
                status_code=400, 
                detail=f"Companion '{companion.name}' already exists"
            )
        
        # Create the companion
        created_companion = await companion_creator.create_character(
            name=companion.name,
            themes=companion.themes,
            archetypes=companion.archetypes,
            complexity=companion.complexity
        )
        
        # Update meta_information with creation timestamp
        created_companion.meta_information["created_timestamp"] = datetime.now().isoformat()
        
        # Save the companion
        companion_creator.save_character(created_companion)
        
        # Notify connected clients
        await broadcast_companion_update(
            f"New companion '{companion.name}' has been created",
            created_companion.name
        )
        
        return created_companion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating companion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}/conversation")
async def get_conversation(name: str, session_id: str = "default"):
    """Get conversation history for a companion."""
    try:
        if name not in companion_creator.characters:
            raise HTTPException(status_code=404, detail=f"Companion '{name}' not found")
        
        # Get session ID
        full_session_id = f"{name}:{session_id}"
        
        # Check if session exists
        if full_session_id not in companion_creator.character_sessions:
            return []
        
        # Return conversation history
        return companion_creator.character_sessions[full_session_id].get("conversation_history", [])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation for {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{name}/interact")
async def interact_with_companion(name: str, interaction: CompanionInteract):
    """Interact with an AI companion."""
    try:
        if name not in companion_creator.characters:
            raise HTTPException(status_code=404, detail=f"Companion '{name}' not found")

        # Get session ID
        full_session_id = f"{name}:{interaction.session_id}"

        # Interact with the companion
        response = await companion_creator.interact_with_character(
            character_name=name,
            user_input=interaction.message,
            session_id=full_session_id
        )

        # Notify connected clients
        await broadcast_conversation_update(
            f"New message in conversation with '{name}'",
            name,
            full_session_id
        )

        return {"response": response}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error interacting with companion {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{name}/evolve")
async def evolve_companion(name: str, evolution: CompanionEvolve):
    """Evolve an AI companion based on interaction history."""
    try:
        if name not in companion_creator.characters:
            raise HTTPException(status_code=404, detail=f"Companion '{name}' not found")
        
        # Get session ID
        full_session_id = f"{name}:{evolution.session_id}"
        
        # Check if session exists
        if full_session_id not in companion_creator.character_sessions:
            raise HTTPException(
                status_code=400, 
                detail=f"No interaction session found for '{name}'"
            )
        
        # Evolve the companion
        evolution_summary = await companion_creator.evolve_character(
            character_name=name,
            session_id=full_session_id
        )
        
        # Add timestamp to evolution summary
        evolution_summary["timestamp"] = datetime.now().isoformat()
        
        # If traits evolved, notify connected clients
        if evolution_summary.get("traits_evolved"):
            await broadcast_companion_update(
                f"Companion '{name}' has evolved based on interactions",
                name
            )
        
        return evolution_summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evolving companion {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws", name="companions_websocket")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    logger.info(f"WebSocket connection attempt from {websocket.client}")
    
    try:
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        
        # Generate a unique connection ID
        connection_id = str(uuid.uuid4())
        
        # Store the connection ID in the WebSocket object
        websocket.connection_id = connection_id

        # Add to active connections only after successful accept
        active_connections.append(websocket)
        
        # Send heartbeat to verify connection is working
        await websocket.send_text('{"type":"ping"}')
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "connection_id": connection_id,
            "message": "Connected to AI Companion WebSocket server",
            "timestamp": datetime.now().isoformat()
        })
        
        # Wait for messages
        while True:
            try:
                data = await websocket.receive_text()
                
                # Parse data
                try:
                    message = json.loads(data)
                    
                    # Handle subscribing to specific companion sessions
                    if message.get("type") == "subscribe_session":
                        companion_name = message.get("companion_name")
                        session_id = message.get("session_id", "default")
                        full_session_id = f"{companion_name}:{session_id}"
                        
                        # Initialize session tracking if needed
                        if full_session_id not in connected_sessions:
                            connected_sessions[full_session_id] = {"connections": set()}
                        
                        # Add this connection to the session
                        connected_sessions[full_session_id]["connections"].add(connection_id)
                        
                        await websocket.send_json({
                            "type": "subscription_confirmed",
                            "session_id": full_session_id,
                            "message": f"Subscribed to updates for {companion_name}"
                        })
                    
                    # Handle pong messages (heartbeat)
                    elif message.get("type") == "pong":
                        # Do nothing, just keep the connection alive
                        pass
                    
                    # Simply echo other messages for debugging
                    else:
                        await websocket.send_json({
                            "type": "echo",
                            "message": message
                        })
                        
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON data"
                    })
                
            except (WebSocketDisconnect, RuntimeError) as e:
                logger.info(f"Client disconnected: {e}")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                break
    finally:
        # Remove from active connections
        if websocket in active_connections:
            active_connections.remove(websocket)
        
        # Remove from all sessions
        for session_data in connected_sessions.values():
            if websocket.connection_id in session_data["connections"]:
                session_data["connections"].remove(websocket.connection_id)


async def broadcast_companion_update(message: str, companion_name: str):
    """Broadcast a companion update to all connected clients."""
    if not active_connections:
        return
    
    update = {
        "type": "companion_update",
        "timestamp": datetime.now().isoformat(),
        "companion_name": companion_name,
        "message": message
    }
    
    try:
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_json(update)
            except Exception as e:
                logger.error(f"Error sending companion update: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            if connection in active_connections:
                active_connections.remove(connection)
    except Exception as e:
        logger.error(f"Error in broadcast_companion_update: {str(e)}")


async def broadcast_conversation_update(message: str, companion_name: str, session_id: str):
    """Broadcast a conversation update to clients subscribed to the session."""
    if not active_connections or session_id not in connected_sessions:
        return
    
    update = {
        "type": "conversation_update",
        "timestamp": datetime.now().isoformat(),
        "companion_name": companion_name,
        "session_id": session_id,
        "message": message
    }
    
    # Get connections subscribed to this session
    try:
        # Get connection IDs subscribed to this session
        connection_ids = connected_sessions[session_id]["connections"]
        
        disconnected = []
        for connection in active_connections:
            try:
                # Each connection should have a unique ID associated with it
                # This may be stored as an attribute or we can use the object's ID
                socket_id = connection.connection_id
                
                # Only send to connections subscribed to this session
                if socket_id in connection_ids:
                    await connection.send_json(update)
            except Exception as e:
                logger.error(f"Error sending to connection: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            if connection in active_connections:
                active_connections.remove(connection)
    except Exception as e:
        logger.error(f"Error in broadcast_conversation_update: {str(e)}")


@router.post("/backstory/generate", status_code=200)
async def generate_backstory(backstory_request: BackstoryGenerate):
    """Generate a backstory for a companion character using Rehoboam's AI."""
    try:
        logger.info(f"Backstory generation request for character: {backstory_request.character_name}")
        
        # Generate the backstory using the MCP function
        backstory = companion_creator._generate_backstory(
            character_name=backstory_request.character_name,
            character_traits=backstory_request.character_traits,
            cultural_influences=backstory_request.cultural_influences,
            story_depth=backstory_request.story_depth,
            key_events=backstory_request.key_events
        )
        
        logger.info(f"Backstory successfully generated for character: {backstory_request.character_name}")
        
        # Broadcast the update to all clients
        await broadcast_companion_update(
            json.dumps({
                "type": "backstory_generation", 
                "character_name": backstory_request.character_name,
                "success": True
            }),
            "system"
        )
        
        return backstory
    except Exception as e:
        logger.error(f"Error generating backstory: {str(e)}")
        
        # Broadcast the error to all clients
        await broadcast_companion_update(
            json.dumps({
                "type": "backstory_generation", 
                "character_name": backstory_request.character_name,
                "success": False,
                "error": str(e)
            }),
            "system"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}/backstory", status_code=200)
async def get_backstory(name: str):
    """Get the backstory for a specific companion."""
    try:
        if name not in companion_creator.characters:
            raise HTTPException(status_code=404, detail=f"Companion '{name}' not found")
        
        character = companion_creator.characters[name]
        
        # If the character has a backstory property in meta_information, return it
        if hasattr(character, 'meta_information') and 'backstory' in character.meta_information:
            return character.meta_information['backstory']
        
        # Otherwise return a default response
        return {
            "backstory": f"The backstory for {name} has not yet been generated.",
            "key_moments": [],
            "relationships": [],
            "secrets": [],
            "future_goals": []
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting backstory for companion {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))