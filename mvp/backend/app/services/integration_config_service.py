from app.database import SessionLocal
from app.models.integration_config import IntegrationConfig
from app.utils.encryption import decrypt_api_key


def get_integration_config(agent_id: int):
    db = SessionLocal()
    try:
        response = db.query(IntegrationConfig.encrypted_key).filter(
                IntegrationConfig.agent_id == agent_id,
                IntegrationConfig.is_active == True
            ).first()
        if not response:
            return False
        decrypted_key = decrypt_api_key(response.encrypted_key)
        return decrypted_key

    finally:
        db.close()
