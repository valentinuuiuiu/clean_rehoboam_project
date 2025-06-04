"""
Unified Configuration for Rehoboam System
========================================

This module provides a unified configuration interface for all Rehoboam components.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import from the root config.py file directly
import importlib.util
spec = importlib.util.spec_from_file_location("root_config", os.path.join(os.path.dirname(__file__), "config.py"))
root_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_config)
BaseConfig = root_config.Config

class RehoboamConfig(BaseConfig):
    """
    Unified configuration for the Rehoboam system
    """
    
    # Consciousness parameters
    CONSCIOUSNESS_THRESHOLD = 0.7
    AI_CONFIDENCE_THRESHOLD = 0.6
    HUMAN_BENEFIT_THRESHOLD = 0.5
    
    # Pipeline parameters
    AGENT_ANALYSIS_INTERVAL = 30
    BOT_FEEDBACK_TIMEOUT = 300
    MAX_CONCURRENT_EXECUTIONS = 5
    LEARNING_THRESHOLD = 0.1
    
    # API parameters
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    
    # Logging
    LOG_LEVEL = "INFO"
    
    # Trading strategies
    STRATEGIES = {
        "arbitrage": {
            "enabled": True,
            "risk_level": 0.3,
            "max_position_size": 1.0,
            "weight": 0.4,
            "description": "Standard arbitrage trading strategy"
        },
        "conscious_arbitrage": {
            "enabled": True,
            "consciousness_threshold": 0.7,
            "human_benefit_weight": 0.3,
            "weight": 0.6,
            "description": "Consciousness-guided arbitrage for human benefit"
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        return True