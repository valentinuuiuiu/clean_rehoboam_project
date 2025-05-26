"""
Rehoboam MCP Integration - Connects the Rehoboam AI with the MCPSpecialist

This module integrates the RehoboamAI core with the MCPSpecialist, allowing the
main consciousness to extend its capabilities through dynamic MCP functions.

It establishes the "cognitive hierarchy" relationship between Rehoboam and its
specialized tool creator.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable

from utils.rehoboam_ai import RehoboamAI
from utils.mcp_specialist import MCPSpecialist, MCPFunction

logger = logging.getLogger(__name__)

class RehoboamMCPIntegration:
    """
    Integration class that connects Rehoboam to the MCPSpecialist.
    This class enhances Rehoboam with the ability to dynamically create and
    use MCP functions as needed.
    """
    
    def __init__(self, rehoboam: Optional[RehoboamAI] = None):
        """
        Initialize the integration.
        
        Args:
            rehoboam: Existing Rehoboam instance, or create a new one if None
        """
        # Initialize Rehoboam core if not provided
        self.rehoboam = rehoboam or RehoboamAI()
        
        # Initialize the MCP Specialist with the same Rehoboam instance
        self.mcp_specialist = MCPSpecialist(self.rehoboam)
        
        # Map of capabilities to MCP function names
        self.capability_map: Dict[str, str] = {
            "sentiment_analysis": "market_sentiment_mcp.MarketSentimentMCP.analyze_token",
            "market_emotions": "rehoboam_ai.RehoboamAI.get_market_emotions",
            # Add more capabilities as they're developed
        }
        
        # Track function generation requests to avoid repetitive generation
        self.generation_requests = set()
        
        logger.info("RehoboamMCPIntegration initialized")
    
    async def check_mcp_availability(self) -> bool:
        """Check if the MCP server is available."""
        return await self.mcp_specialist.check_mcp_availability()
    
    async def get_sentiment_analysis(self, token: str) -> Dict[str, Any]:
        """
        Get sentiment analysis for a token using the best available method.
        
        This demonstrates the integration pattern - dynamically selecting the
        appropriate function based on availability.
        
        Args:
            token: Token symbol to analyze
            
        Returns:
            Sentiment analysis result
        """
        # First try the MCP specialist's built-in method
        result = self.mcp_specialist.get_market_analysis_with_mcp(token)
        
        # If no result or minimal result, try to create a new function
        if not result or len(result) < 3:
            await self._ensure_sentiment_analysis_function()
            # Try again with potentially new function
            result = self.mcp_specialist.get_market_analysis_with_mcp(token)
        
        return result
    
    async def get_market_emotions(self) -> Dict[str, Any]:
        """
        Get market emotions using the best available method.
        
        Returns:
            Market emotions data
        """
        # First try the MCP specialist's built-in method
        result = self.mcp_specialist.get_market_emotions_with_mcp()
        
        # If no result or minimal result, try to create a new function
        if not result or len(result) < 3:
            await self._ensure_market_emotions_function()
            # Try again with potentially new function
            result = self.mcp_specialist.get_market_emotions_with_mcp()
        
        return result
    
    async def _ensure_sentiment_analysis_function(self) -> None:
        """Ensure a sentiment analysis function exists or create one."""
        # Check if we've already tried to generate this
        if "sentiment_analysis" in self.generation_requests:
            return
            
        # Mark that we've tried generation
        self.generation_requests.add("sentiment_analysis")
        
        # Check if the function already exists
        function_name = self.capability_map["sentiment_analysis"]
        if self.mcp_specialist.has_mcp_function(function_name):
            return
            
        logger.info("Creating new sentiment analysis MCP function")
        
        # Create the function
        await self.mcp_specialist.generate_mcp_function(
            name="analyze_token_sentiment",
            description="Analyze the market sentiment for a cryptocurrency token",
            parameter_description="token: str - The token symbol to analyze",
            return_description="Dict with sentiment data including: score, mood, and confidence",
            example_code="""
def analyze_token_sentiment(token: str) -> Dict[str, Any]:
    \"\"\"Analyze the market sentiment for a cryptocurrency token.\"\"\"
    
    # Basic rule-based sentiment
    if token in ["BTC", "ETH"]:
        return {
            "token": token,
            "score": 0.5,
            "mood": "optimistic",
            "confidence": 0.7
        }
    else:
        return {
            "token": token,
            "score": 0.1,
            "mood": "neutral",
            "confidence": 0.6
        }
"""
        )
        
        # Update the capability map if needed
        self.capability_map["sentiment_analysis"] = "analyze_token_sentiment"
    
    async def _ensure_market_emotions_function(self) -> None:
        """Ensure a market emotions function exists or create one."""
        # Check if we've already tried to generate this
        if "market_emotions" in self.generation_requests:
            return
            
        # Mark that we've tried generation
        self.generation_requests.add("market_emotions")
        
        # Check if the function already exists
        function_name = self.capability_map["market_emotions"]
        if self.mcp_specialist.has_mcp_function(function_name):
            return
            
        logger.info("Creating new market emotions MCP function")
        
        # Create the function
        await self.mcp_specialist.generate_mcp_function(
            name="analyze_market_emotions",
            description="Analyze the emotional state of the cryptocurrency market",
            parameter_description="None",
            return_description="Dict with market emotions data including: primary_emotion, secondary_emotion, and intensity",
            example_code="""
def analyze_market_emotions() -> Dict[str, Any]:
    \"\"\"Analyze the emotional state of the cryptocurrency market.\"\"\"
    
    # Basic rule-based emotion analysis
    from datetime import datetime
    
    # Simple heuristic based on time of day
    hour = datetime.now().hour
    
    if hour < 6:
        return {
            "primary_emotion": "anticipation",
            "secondary_emotion": "uncertainty",
            "intensity": 0.6,
            "description": "Pre-market anticipation with uncertainty undercurrent",
            "timestamp": datetime.now().isoformat()
        }
    elif hour < 12:
        return {
            "primary_emotion": "optimism",
            "secondary_emotion": "caution",
            "intensity": 0.7,
            "description": "Morning optimism with cautious undercurrent",
            "timestamp": datetime.now().isoformat()
        }
    elif hour < 18:
        return {
            "primary_emotion": "calculated",
            "secondary_emotion": "tension",
            "intensity": 0.5,
            "description": "Afternoon calculated assessment with tension undercurrent",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "primary_emotion": "reflection",
            "secondary_emotion": "anticipation",
            "intensity": 0.4,
            "description": "Evening reflection with anticipation undercurrent",
            "timestamp": datetime.now().isoformat()
        }
"""
        )
        
        # Update the capability map if needed
        self.capability_map["market_emotions"] = "analyze_market_emotions"
    
    async def create_custom_mcp_function(self, capability: str, function_spec: Dict[str, str]) -> bool:
        """
        Create a custom MCP function based on a specification.
        
        Args:
            capability: Capability name to register
            function_spec: Function specification containing:
                - name: Function name
                - description: Function description
                - parameters: Parameter description
                - returns: Return value description
                - example: Optional example code
                
        Returns:
            True if function was created successfully, False otherwise
        """
        if capability in self.generation_requests:
            logger.warning(f"Already attempted to generate capability: {capability}")
            return False
            
        self.generation_requests.add(capability)
        
        try:
            result = await self.mcp_specialist.generate_mcp_function(
                name=function_spec.get("name", f"function_{capability}"),
                description=function_spec.get("description", f"Function for {capability}"),
                parameter_description=function_spec.get("parameters", ""),
                return_description=function_spec.get("returns", ""),
                example_code=function_spec.get("example", None)
            )
            
            if result:
                # Update capability map
                self.capability_map[capability] = result.name
                logger.info(f"Successfully created MCP function for capability: {capability}")
                return True
            else:
                logger.error(f"Failed to create MCP function for capability: {capability}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating MCP function for capability {capability}: {str(e)}")
            return False
            
    def get_available_capabilities(self) -> List[str]:
        """
        Get list of all available capabilities.
        
        Returns:
            List of capability names
        """
        return list(self.capability_map.keys())
    
    def get_registered_mcp_functions(self) -> List[Dict[str, Any]]:
        """
        Get all registered MCP functions.
        
        Returns:
            List of MCP function metadata
        """
        return self.mcp_specialist.list_mcp_functions()
    
    async def adapt_existing_function(self, func: Callable, capability_name: str) -> bool:
        """
        Adapt an existing Python function to the MCP system.
        
        Args:
            func: The function to adapt
            capability_name: Name for the capability
            
        Returns:
            True if adaptation was successful, False otherwise
        """
        try:
            result = await self.mcp_specialist.adapt_function_to_mcp(func)
            
            if result:
                # Register the capability
                self.capability_map[capability_name] = result.name
                logger.info(f"Successfully adapted function for capability: {capability_name}")
                return True
            else:
                logger.error(f"Failed to adapt function for capability: {capability_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adapting function for capability {capability_name}: {str(e)}")
            return False