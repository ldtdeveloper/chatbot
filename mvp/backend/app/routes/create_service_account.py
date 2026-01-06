
"""
Utilities for creating OpenAI service accounts and API keys.
"""

import httpx
import time
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

def create_service_account(
    user_id: int,
    name_prefix: str = "user",
    timeout: float = 30.0,
) -> Dict[str, Any]:
    print("inside the service account")
    """
    Creates OpenAI service account using organization admin key.
    To be called in background after successful payment.
    """
    admin_key = settings.ADMIN_KEY
    project_id = settings.PROJECT_ID

    if not admin_key or not project_id:
        raise ValueError("OpenAI admin key or project ID not configured")

    service_account_name = f"{name_prefix}-{user_id}-{int(time.time())}"

    url = f"https://api.openai.com/v1/organization/projects/{project_id}/service_accounts"

    headers = {
        "Authorization": f"Bearer {admin_key}",
        "Content-Type": "application/json",
    }

    payload = {"name": service_account_name}

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()  # better error handling

            data = response.json()
            api_key = data.get("api_key", {}).get("value")
            
            if not api_key:
                raise ValueError("No API key returned from OpenAI")

            return {
                "success": True,
                "service_account_id": data.get("id"),
                "service_account_name": data.get("name"),
                "created_at": data.get("created_at"),
                "user_api_key": api_key,
                "user_id": user_id
            }

    except Exception as e:
        logger.exception(f"Failed to create OpenAI service account for user {user_id}")
        raise
    