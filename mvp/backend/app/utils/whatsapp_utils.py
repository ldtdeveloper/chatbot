import httpx
import logging
from sqlalchemy.orm import Session
from app.models.whatsapp_configs import WhatsappConfig

logger = logging.getLogger(__name__)

async def send_whatsapp_message(db: Session, text_agent_id: int, to: str, text: str):
    """
    Sends a WhatsApp message using the Meta Graph API.
    Retrieves the necessary config (access token, phone number ID) from the database.
    """
    try:
        config = db.query(WhatsappConfig).filter(
            WhatsappConfig.text_agent_id == text_agent_id
        ).first()

        if not config or not config.access_token or not config.phone_number_id:
            logger.error(f"WhatsApp config missing or incomplete for agent {text_agent_id}")
            return False

        url = f"https://graph.facebook.com/v18.0/{config.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                logger.info(f"WhatsApp message sent to {to}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message: {resp.status_code} - {resp.text}")
                return False
    except Exception:
        logger.exception("Error sending WhatsApp message")
        return False
