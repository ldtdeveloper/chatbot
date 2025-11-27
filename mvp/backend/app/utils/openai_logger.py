"""
OpenAI Request Logger for Dev Environment
Logs all OpenAI API requests with URL, Headers, and Body
"""
import json
import logging
from app.config import settings

# Set up logger
logger = logging.getLogger("openai_requests")

def log_openai_request(url: str, headers: dict, body: dict = None, method: str = "POST"):
    """
    Log OpenAI API request in dev/local environment
    
    Args:
        url: Request URL
        headers: Request headers (will mask Authorization token)
        body: Request body (optional)
        method: HTTP method (default: POST)
    """
    # Only log in DEV and LOCAL environments
    if settings.app_env.upper() in ["DEV", "LOCAL"]:
        # Mask Authorization header for security
        masked_headers = headers.copy()
        if "Authorization" in masked_headers:
            auth_value = masked_headers["Authorization"]
            if auth_value.startswith("Bearer "):
                # Show first 10 chars and last 4 chars of token
                token = auth_value[7:]  # Remove "Bearer "
                if len(token) > 14:
                    masked_token = f"{token[:10]}...{token[-4:]}"
                else:
                    masked_token = "***"
                masked_headers["Authorization"] = f"Bearer {masked_token}"
            else:
                masked_headers["Authorization"] = "Bearer ***"
        
        # Format body as JSON string if it's a dict
        body_str = ""
        if body:
            if isinstance(body, dict):
                body_str = json.dumps(body, indent=2)
            else:
                body_str = str(body)
        
        # Log the request
        logger.info("OpenAI REQUEST -")
        logger.info(f"endpoint: {method} {url}")
        logger.info(f"headers: {json.dumps(masked_headers, indent=2)}")
        if body_str:
            logger.info(f"body: {body_str}")
        else:
            logger.info("body: (empty)")

def log_openai_websocket_connect(url: str, headers: dict):
    """
    Log OpenAI WebSocket connection in dev/local environment
    
    Args:
        url: WebSocket URL
        headers: Connection headers (will mask Authorization token)
    """
    # Only log in DEV and LOCAL environments
    if settings.app_env.upper() in ["DEV", "LOCAL"]:
        # Mask Authorization header for security
        masked_headers = headers.copy()
        if "Authorization" in masked_headers:
            auth_value = masked_headers["Authorization"]
            if auth_value.startswith("Bearer "):
                # Show first 10 chars and last 4 chars of token
                token = auth_value[7:]  # Remove "Bearer "
                if len(token) > 14:
                    masked_token = f"{token[:10]}...{token[-4:]}"
                else:
                    masked_token = "***"
                masked_headers["Authorization"] = f"Bearer {masked_token}"
            else:
                masked_headers["Authorization"] = "Bearer ***"
        
        logger.info("OpenAI REQUEST -")
        logger.info(f"endpoint: WebSocket {url}")
        logger.info(f"headers: {json.dumps(masked_headers, indent=2)}")
        logger.info("body: (WebSocket connection)")

def log_openai_websocket_message(message: dict):
    """
    Log OpenAI WebSocket message in dev/local environment
    
    Args:
        message: WebSocket message as dict
    """
    # Only log in DEV and LOCAL environments
    if settings.app_env.upper() in ["DEV", "LOCAL"]:
        message_str = json.dumps(message, indent=2)
        logger.info("OpenAI REQUEST -")
        logger.info("endpoint: WebSocket Message")
        logger.info("headers: (N/A for WebSocket message)")
        logger.info(f"body: {message_str}")

