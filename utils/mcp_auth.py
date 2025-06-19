"""
MCP Authentication and Authorization utilities.
Handles JWT token validation and MCP endpoint security.
"""
import os
import time
import secrets
import hashlib
import hmac
import base64
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Get configuration from environment
JWT_SECRET = os.getenv('JWT_SECRET', 'eZGyeSZpKNqux0PZ2Au8NsmCCR8hWWfDkCxIAJnheZM=')
MCP_TOKEN = os.getenv('MCP_TOKEN', 'cTs2QwNvbBMx2RsaQC1Sh8Z249ZpP-3IckzLK3YaXf0')
API_TOKEN = os.getenv('API_TOKEN', '1cm_y-8fvBJSJP5KtaJVZaXRthQr_F4Qi6MVB03w3QYwZrNJkJJER0fueBMv6bW3OvGurJRBhdE_vPF0PcEpTQ')

# Security scheme
security = HTTPBearer()

class MCPAuthenticator:
    """Handles MCP authentication and authorization."""
    
    def __init__(self):
        self.jwt_secret = JWT_SECRET
        self.mcp_token = MCP_TOKEN
        self.api_token = API_TOKEN
        
    def verify_simple_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a simple token and return basic payload.
        NOTE: This method performs a direct string comparison against self.api_token
        and self.mcp_token. It does not perform cryptographic JWT validation,
        even though it might be used by dependencies (like verify_jwt_dependency)
        that are integrated with JWT-expecting mechanisms (e.g., HTTPBearer).
        This is a simplified token check.
        """
        try:
            # For now, use simple token validation
            if secrets.compare_digest(token, self.api_token) or secrets.compare_digest(token, self.mcp_token):
                return {
                    'user_id': 'rehoboam_system',
                    'role': 'admin',
                    'type': 'api_token',
                    'valid': True
                }
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def verify_mcp_token(self, token: str) -> bool:
        """Verify MCP-specific token."""
        return secrets.compare_digest(token, self.mcp_token)
    
    def verify_api_token(self, token: str) -> bool:
        """Verify API token."""
        return secrets.compare_digest(token, self.api_token)
    
    def generate_mcp_session_token(self, user_id: str, duration_hours: int = 24) -> str:
        """
        Generate a session token for MCP access.
        NOTE: This method generates a simple base64 encoded token based on user_id,
        timestamp, and duration. It is NOT a cryptographically signed JWT.
        """
        # Simple token generation for now
        timestamp = str(int(time.time()))
        token_data = f"{user_id}:{timestamp}:{duration_hours}"
        return base64.urlsafe_b64encode(token_data.encode()).decode()

# Global authenticator instance
mcp_auth = MCPAuthenticator()

# FastAPI Dependencies
async def verify_jwt_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency for token verification.
    NOTE: This dependency relies on `mcp_auth.verify_simple_token` for actual validation.
    Therefore, it currently verifies tokens via direct string comparison rather than
    standard JWT cryptographic signature validation, despite using HTTPBearer.
    """
    payload = mcp_auth.verify_simple_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

async def verify_mcp_token_dependency(x_mcp_token: str = Header(None)) -> bool:
    """FastAPI dependency for MCP token verification."""
    if not x_mcp_token or not mcp_auth.verify_mcp_token(x_mcp_token):
        raise HTTPException(status_code=401, detail="Invalid MCP token")
    return True

async def verify_api_token_dependency(x_api_token: str = Header(None)) -> bool:
    """FastAPI dependency for API token verification."""
    if not x_api_token or not mcp_auth.verify_api_token(x_api_token):
        raise HTTPException(status_code=401, detail="Invalid API token")
    return True

async def optional_auth(authorization: str = Header(None)) -> Optional[Dict[str, Any]]:
    """Optional authentication dependency."""
    if not authorization:
        return None
    
    try:
        # Remove 'Bearer ' prefix if present
        token = authorization.replace('Bearer ', '') if authorization.startswith('Bearer ') else authorization
        return mcp_auth.verify_jwt_token(token)
    except Exception:
        return None

def create_system_token() -> str:
    """Create a system-level token for internal MCP operations."""
    # Simple system token generation
    timestamp = str(int(time.time()))
    token_data = f"rehoboam_system:system:{timestamp}"
    return base64.urlsafe_b64encode(token_data.encode()).decode()

# System token for internal operations
SYSTEM_TOKEN = create_system_token()

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for internal API calls."""
    return {
        'Authorization': f'Bearer {SYSTEM_TOKEN}',
        'X-MCP-Token': MCP_TOKEN,
        'X-API-Token': API_TOKEN
    }

logger.info("MCP Authentication system initialized")
logger.info(f"JWT Secret configured: {'Yes' if JWT_SECRET else 'No'}")
logger.info(f"MCP Token configured: {'Yes' if MCP_TOKEN else 'No'}")
logger.info(f"API Token configured: {'Yes' if API_TOKEN else 'No'}")
