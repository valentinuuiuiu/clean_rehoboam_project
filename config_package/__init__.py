# Configuration package for Rehoboam trading platform

# Import from root config module
import sys
import os

# Add parent directory to path to import the root config.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the Config class from the root config.py
try:
    from config import Config as RootConfig
    Config = RootConfig
except ImportError:
    # Fallback in case of import issues
    class Config:
        pass

__all__ = ['Config']
