from app.database import SessionLocal
from app.models.integration_config import IntegrationConfig
from app.utils.encryption import decrypt_api_key
from typing import Optional, Dict


def get_integration_config(agent_id: int) -> Optional[Dict[str, str]]:
    """
    Get integration config for an agent (HubSpot token and instructions).
    
    Returns:
        Dict with 'token' and 'instructions' keys, or None if not found
    """
    db = SessionLocal()
    try:
        config = db.query(IntegrationConfig).filter(
                IntegrationConfig.agent_id == agent_id,
                IntegrationConfig.is_active == True
            ).first()
        if not config:
            return None
        
        decrypted_key = decrypt_api_key(config.encrypted_key)
        return {
            'token': decrypted_key,
            'instructions': config.instructions or ''
        }

    finally:
        db.close()
