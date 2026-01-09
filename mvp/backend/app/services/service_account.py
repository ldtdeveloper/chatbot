"""
Utilities for creating OpenAI service accounts and API keys.
"""

import httpx
import time
import logging
from app.core.dependencies import get_current_user
from typing import Dict, Any
from sqlalchemy.orm import Session

from fastapi import Depends
from app.models.user import User
from app.models.service_account_key import ServiceAccountKey
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_service_account(
    admin_key: str = None,
    project_id: str = None,
    name_prefix: str = "user",
    timeout: float = 30.0,
    db= Session,
    user= User  # Pass real user object
) -> Dict[str, Any]:
    admin_key = admin_key or settings.ADMIN_KEY
    project_id = project_id or settings.PROJECT_ID

    if not admin_key or not project_id:
        raise ValueError("Admin key or project ID missing")

    service_account_name = f"{name_prefix}-{user.username or user.id}-{int(time.time())}"

    url = f"https://api.openai.com/v1/organization/projects/{project_id}/service_accounts"

    headers = {
        "Authorization": f"Bearer {admin_key}",
        "Content-Type": "application/json",
    }

    payload = {"name": service_account_name}

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                raise ValueError(f"Failed - {response.status_code}: {response.text}")

            data = response.json()
            api_key_value = data.get("api_key", {}).get("value")

            if not api_key_value:
                raise ValueError("No API key returned")

            # TODO: Encrypt!
            # encrypted_key = fernet.encrypt(api_key_value.encode()).decode()

            new_record = ServiceAccountKey(
                user_id=user.id,
                email=user.email,
                key_name=f"Key - {service_account_name}",
                service_account_key=api_key_value,
                openai_service_account_id=data["id"],
                is_active=True
            )

            db.add(new_record)
            db.commit()
            db.refresh(new_record)

            return {
                "success": True,
                "service_account_id": data["id"],
                "api_key": api_key_value,
                "db_id": new_record.id
            }

    except Exception as e:
        raise ValueError(f"Error: {str(e)}")