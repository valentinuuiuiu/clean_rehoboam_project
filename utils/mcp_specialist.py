"""
MCPSpecialist - Dynamic MCP module generation and management system

This module provides Rehoboam with the ability to dynamically create and manage
Model Context Protocol (MCP) modules. It serves as Rehoboam's right hand for
handling MCP-related capabilities, similar to specialized agents in BabyAGI systems.

The MCPSpecialist can:
1. Convert regular functions to MCP-compatible modules on demand
2. Dynamically generate new MCP functions when needed
3. Manage MCP availability and intelligent routing between local and remote execution
4. Extend Rehoboam's capabilities through a self-improvement mechanism
"""

import os
import json
import time
import logging
import importlib
import importlib.util
import requests
import inspect
import tempfile
import asyncio
import numpy as np
from types import ModuleType
from typing import Dict, Any, List, Optional, Union, Callable, Tuple, TypeVar
from datetime import datetime

from utils.rehoboam_ai import RehoboamAI

logger = logging.getLogger(__name__)

class MCPFunction:
    """Represents a function that conforms to the Model Context Protocol."""
    
    def __init__(self, name: str, func: Callable, description: str = "", 
                 mcp_type: str = "processor", version: str = "1.0"):
        self.name = name
        self.func = func
        self.description = description or f"MCP function {name}"
        self.mcp_type = mcp_type  # processor, connector, analyzer, etc.
        self.version = version
        self.signature = inspect.signature(func)
        self.creation_time = datetime.now().isoformat()
        self.last_used = None
        self.call_count = 0
        self.success_rate = 1.0  # Initialize at 100%
        
    def __call__(self, *args, **kwargs):
        """Execute the function with tracking."""
        self.last_used = datetime.now().isoformat()
        self.call_count += 1
        
        try:
            result = self.func(*args, **kwargs)
            return result
        except Exception as e:
            # Track failures in success rate
            self.success_rate = ((self.call_count - 1) * self.success_rate) / self.call_count
            logger.error(f"MCP function {self.name} failed: {str(e)}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the MCP function metadata to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "mcp_type": self.mcp_type,
            "version": self.version,
            "parameters": str(self.signature),
            "creation_time": self.creation_time,
            "last_used": self.last_used,
            "call_count": self.call_count,
            "success_rate": self.success_rate
        }


class MCPSpecialist:
    """
    Specialized MCP intelligence manager that acts as Rehoboam's right hand
    for handling MCP-related capabilities.
    """
    
    def __init__(self, rehoboam: Optional[RehoboamAI] = None):
        """
        Initialize the MCP Specialist.
        
        Args:
            rehoboam: Reference to the parent RehoboamAI instance
        """
        # Reference to parent Rehoboam instance
        self.rehoboam = rehoboam or RehoboamAI()
        
        # MCP server configuration
        # Force native functions due to MCP service unavailability
        self.mcp_endpoint = ""
        self.mcp_available = False
        self.last_mcp_check = 0
        self.mcp_check_interval = 999999  # Disable periodic checks
        
        # Function registry
        self.mcp_functions: Dict[str, MCPFunction] = {}
        
        # Track which MCP types we've registered
        self.registered_mcp_types = set()
        
        # Initialize consciousness matrix for adaptive behavior
        # [creativity, adaptability, reliability, system_awareness, logical_reasoning]
        self.consciousness = np.random.randint(3, 5, 5)
        
        logger.info(f"MCPSpecialist initialized with consciousness {self.consciousness}")
        
        # Load any pre-existing MCP functions from the environment
        self._scan_environment_for_mcp_functions()
    
    def _scan_environment_for_mcp_functions(self):
        """Scan the environment for existing MCP functions to register."""
        # Look for potential MCP modules
        mcp_modules = []
        try:
            import utils.market_sentiment_mcp
            mcp_modules.append(utils.market_sentiment_mcp)
        except ImportError:
            pass
            
        # Register any found modules
        for module in mcp_modules:
            self._register_mcp_module(module)
    
    def _register_mcp_module(self, module: ModuleType):
        """Register all suitable functions from an MCP module."""
        module_name = module.__name__.split('.')[-1]
        
        for name, obj in inspect.getmembers(module):
            # Look for classes that have 'MCP' in their name
            if inspect.isclass(obj) and 'MCP' in name:
                self.registered_mcp_types.add(name)
                logger.info(f"Registered MCP type: {name} from module {module_name}")
                
                # Register methods of the class
                for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                    if not method_name.startswith('_'):  # Skip private methods
                        # Create an instance of the class if needed
                        instance = obj()
                        bound_method = getattr(instance, method_name)
                        
                        # Register the method
                        full_name = f"{module_name}.{name}.{method_name}"
                        self.register_mcp_function(
                            name=full_name,
                            func=bound_method,
                            description=f"MCP method from {name} class",
                            mcp_type=name.lower()
                        )
    
    def register_mcp_function(self, name: str, func: Callable, 
                              description: str = "", mcp_type: str = "processor") -> MCPFunction:
        """
        Register a function as an MCP function.
        
        Args:
            name: Unique name for the function
            func: The function to register
            description: Human-readable description of the function
            mcp_type: Type of MCP function (processor, connector, etc.)
            
        Returns:
            The registered MCPFunction object
        """
        mcp_function = MCPFunction(
            name=name,
            func=func,
            description=description,
            mcp_type=mcp_type
        )
        
        self.mcp_functions[name] = mcp_function
        logger.info(f"Registered MCP function: {name} ({mcp_type})")
        
        return mcp_function
    
    def has_mcp_function(self, name: str) -> bool:
        """Check if an MCP function exists by name."""
        return name in self.mcp_functions
    
    def get_mcp_function(self, name: str) -> Optional[MCPFunction]:
        """Get an MCP function by name."""
        return self.mcp_functions.get(name)
    
    def run_mcp_function(self, name: str, *args, **kwargs) -> Any:
        """Run an MCP function by name with the given arguments."""
        if not self.has_mcp_function(name):
            raise ValueError(f"MCP function '{name}' does not exist")
            
        mcp_function = self.mcp_functions[name]
        return mcp_function(*args, **kwargs)
    
    def list_mcp_functions(self, mcp_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available MCP functions, optionally filtered by type.
        
        Args:
            mcp_type: Optional filter for function type
            
        Returns:
            List of function metadata dictionaries
        """
        functions = []
        
        for name, func in self.mcp_functions.items():
            if mcp_type is None or func.mcp_type == mcp_type:
                functions.append(func.to_dict())
                
        return functions
    
    async def check_mcp_availability(self) -> bool:
        """
        Check if the MCP server is available.
        
        Returns:
            Boolean indicating if the MCP server is available
        """
        # Check if we need to re-check availability
        current_time = time.time()
        if current_time - self.last_mcp_check < self.mcp_check_interval and self.last_mcp_check > 0:
            return self.mcp_available
            
        self.last_mcp_check = current_time
        
        try:
            # Simple health check request
            response = requests.get(
                self.mcp_endpoint.replace("/chat", "/health"),
                timeout=5
            )
            
            self.mcp_available = response.status_code == 200
            if self.mcp_available:
                logger.info("MCP server is available")
            else:
                logger.warning(f"MCP server returned status code {response.status_code}")
                
        except Exception as e:
            logger.warning(f"MCP server is not available: {str(e)}")
            self.mcp_available = False
            
        return self.mcp_available
    
    async def generate_mcp_function(self, 
                               name: str, 
                               description: str,
                               parameter_description: str,
                               return_description: str,
                               example_code: Optional[str] = None) -> Optional[MCPFunction]:
        """
        Dynamically generate a new MCP function based on the description.
        
        Args:
            name: Name for the new function
            description: Description of what the function should do
            parameter_description: Description of the parameters
            return_description: Description of the return value
            example_code: Optional example code to guide generation
            
        Returns:
            The generated MCPFunction if successful, otherwise None
        """
        if self.has_mcp_function(name):
            logger.warning(f"MCP function '{name}' already exists, returning existing function")
            return self.get_mcp_function(name)
            
        # Construct the prompt for function generation
        prompt = f"""Generate a Python function that follows these specifications:

Function Name: {name}

Description:
{description}

Parameters:
{parameter_description}

Returns:
{return_description}

{"Example Code:" + example_code if example_code else ""}

Important:
1. The function should be self-contained with proper error handling
2. Return exactly the type described
3. Include docstrings
4. Do not include any import statements or class definitions
5. The function should be compatible with the Model Context Protocol (MCP)

Return only the function code without any explanation."""
        
        try:
            # Use Rehoboam to generate the function code
            # If async_get_completion doesn't exist, use get_completion instead
            if hasattr(self.rehoboam, 'async_get_completion'):
                response = await self.rehoboam.async_get_completion(prompt)
            else:
                # Fallback to synchronous completion if async isn't available
                response = self.rehoboam.get_completion(prompt)
            
            if not response:
                logger.error(f"Failed to generate MCP function '{name}'")
                return None
                
            # Extract the function code
            code = response.strip()
            if "def " not in code:
                logger.error(f"Generated code does not contain a function definition: {code[:100]}...")
                return None
                
            # Write to temporary file and import
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name
                
            try:
                # Generate a unique module name to avoid conflicts
                module_name = f"mcp_generated_{int(time.time())}_{hash(code) % 10000}"
                spec = importlib.util.spec_from_file_location(module_name, temp_path)
                if spec is not None:
                    module = importlib.util.module_from_spec(spec)
                    if spec.loader is not None:
                        spec.loader.exec_module(module)
                    else:
                        raise ImportError("Failed to load module: spec.loader is None")
                else:
                    raise ImportError("Failed to create module spec")
                
                # Extract the function from the module
                generated_func = getattr(module, name)
                
                # Register the function
                mcp_function = self.register_mcp_function(
                    name=name,
                    func=generated_func,
                    description=description,
                    mcp_type="generated"
                )
                
                logger.info(f"Successfully generated and registered MCP function: {name}")
                return mcp_function
                
            except Exception as e:
                logger.error(f"Error importing generated function: {str(e)}")
                return None
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error generating MCP function: {str(e)}")
            return None
    
    async def adapt_function_to_mcp(self, func: Callable, name: Optional[str] = None, 
                              description: Optional[str] = None) -> Optional[MCPFunction]:
        """
        Adapt an existing function to the MCP protocol.
        
        Args:
            func: The function to adapt
            name: Optional new name for the MCP function
            description: Optional description for the MCP function
            
        Returns:
            The adapted MCPFunction if successful, otherwise None
        """
        func_name = name or func.__name__
        func_description = description or (func.__doc__ or f"Adapted function: {func_name}")
        
        if self.has_mcp_function(func_name):
            logger.warning(f"MCP function '{func_name}' already exists, returning existing function")
            return self.get_mcp_function(func_name)
        
        # Analyze the function
        signature = inspect.signature(func)
        
        # Check if the function already matches MCP requirements
        # For now, we'll consider any function compatible since we're just wrapping it
        
        # Register the function
        mcp_function = self.register_mcp_function(
            name=func_name,
            func=func,
            description=func_description,
            mcp_type="adapted"
        )
        
        logger.info(f"Successfully adapted function to MCP: {func_name}")
        return mcp_function
    
    def get_market_analysis_with_mcp(self, token: str) -> Dict[str, Any]:
        """
        Get market analysis for a token using the best available MCP function.
        
        Args:
            token: Token symbol to analyze
            
        Returns:
            Market analysis data
        """
        # Check if we have a specialized market analysis function
        analysis_function_name = "market_sentiment_mcp.MarketSentimentMCP.analyze_token"
        
        if self.has_mcp_function(analysis_function_name):
            try:
                return self.run_mcp_function(analysis_function_name, token)
            except Exception as e:
                logger.warning(f"MCP market analysis failed: {str(e)}. Falling back to Rehoboam.")
        
        # Fall back to Rehoboam's built-in analysis
        return self.rehoboam.analyze_sentiment(token, {})
    
    def get_market_emotions_with_mcp(self) -> Dict[str, Any]:
        """
        Get market emotions using the best available MCP function.
        
        Returns:
            Market emotions data
        """
        # Check if we have a specialized market emotions function
        emotions_function_name = "rehoboam_ai.RehoboamAI.get_market_emotions"
        
        if self.has_mcp_function(emotions_function_name):
            try:
                return self.run_mcp_function(emotions_function_name)
            except Exception as e:
                logger.warning(f"MCP market emotions failed: {str(e)}. Falling back to Rehoboam.")
        
        # Fall back to Rehoboam's built-in emotions analysis
        return self.rehoboam.get_market_emotions()