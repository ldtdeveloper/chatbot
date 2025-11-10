"""
OpenAI API sync utilities for prompts and versions
"""
import httpx
from typing import List
from app.utils.encryption import decrypt_api_key
from app.models.openai_key import OpenAIKey
from sqlalchemy.orm import Session


async def create_openai_prompt(
    api_key: OpenAIKey,
    name: str,
    instructions: str,
    db: Session
) -> dict:
    """
    Create a prompt on OpenAI API
    Returns: {"id": "pmpt_...", "version": "1"}
    """
    try:
        decrypted_key = decrypt_api_key(api_key.encrypted_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use /v1/prompts endpoint (not /v1/realtime/prompts)
            response = await client.post(
                "https://api.openai.com/v1/prompts",
                headers={
                    "Authorization": f"Bearer {decrypted_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": name,
                    "instructions": instructions
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    "id": data.get("id"),
                    "version": str(data.get("version", "1"))
                }
            else:
                error_msg = response.text
                raise Exception(f"OpenAI API error: {response.status_code} - {error_msg}")
                
    except Exception as e:
        raise Exception(f"Failed to create prompt on OpenAI: {str(e)}")


async def create_openai_prompt_version(
    api_key: OpenAIKey,
    prompt_id: str,
    instructions: str,
    db: Session
) -> str:
    """
    Create a new version of a prompt on OpenAI API
    Returns: version string (e.g., "2", "3", etc.)
    """
    try:
        decrypted_key = decrypt_api_key(api_key.encrypted_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use /v1/prompts/{id}/versions endpoint (not /v1/realtime/prompts)
            response = await client.post(
                f"https://api.openai.com/v1/prompts/{prompt_id}/versions",
                headers={
                    "Authorization": f"Bearer {decrypted_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "instructions": instructions
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                return str(data.get("version", "1"))
            else:
                error_msg = response.text
                raise Exception(f"OpenAI API error: {response.status_code} - {error_msg}")
                
    except Exception as e:
        raise Exception(f"Failed to create prompt version on OpenAI: {str(e)}")


async def list_openai_prompts(
    api_key: OpenAIKey
) -> List[dict]:
    """
    List all prompts from OpenAI's Realtime API
    Note: OpenAI API doesn't have a list endpoint, so we return empty list
    Prompts must be created through our system and stored locally
    """
    # OpenAI API doesn't support listing prompts via REST API
    # Prompts are managed through the Realtime WebSocket API or created via REST
    # We'll return an empty list and rely on locally stored prompts
    return []


async def get_openai_prompt(
    api_key: OpenAIKey,
    prompt_id: str
) -> dict:
    """
    Get a specific prompt from OpenAI API
    Returns: Prompt object with id, name, instructions, versions, etc.
    """
    try:
        decrypted_key = decrypt_api_key(api_key.encrypted_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use /v1/prompts/{id} endpoint (not /v1/realtime/prompts)
            response = await client.get(
                f"https://api.openai.com/v1/prompts/{prompt_id}",
                headers={
                    "Authorization": f"Bearer {decrypted_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.text
                raise Exception(f"OpenAI API error: {response.status_code} - {error_msg}")
                
    except Exception as e:
        raise Exception(f"Failed to get prompt from OpenAI: {str(e)}")


async def list_openai_prompt_versions(
    api_key: OpenAIKey,
    prompt_id: str
) -> List[dict]:
    """
    List all versions of a prompt from OpenAI API
    Returns: List of version objects with version, instructions, created_at, etc.
    """
    try:
        decrypted_key = decrypt_api_key(api_key.encrypted_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use /v1/prompts/{id}/versions endpoint (not /v1/realtime/prompts)
            response = await client.get(
                f"https://api.openai.com/v1/prompts/{prompt_id}/versions",
                headers={
                    "Authorization": f"Bearer {decrypted_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both list response and object with data property
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "data" in data:
                    return data["data"]
                else:
                    return []
            else:
                error_msg = response.text
                raise Exception(f"OpenAI API error: {response.status_code} - {error_msg}")
                
    except Exception as e:
        raise Exception(f"Failed to list prompt versions from OpenAI: {str(e)}")

