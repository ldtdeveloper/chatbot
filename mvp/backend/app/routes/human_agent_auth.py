"""
Human Agent Authentication Routes
- OTP-based login via email
- JWT token issuance
- Protected agent profile endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import random
from jose import jwt, JWTError

from app.core.database import get_db
from app.models.human_agent import HumanAgent
from app.models.whatsapp_configs import WhatsappConfig
from app.services.email_service import EmailService
from app.tasks.email_task import send_email_task
from app.core.config import settings
from app.models.user import User
import string

router = APIRouter(prefix="/human-agent", tags=["Agent Auth"])

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
security = HTTPBearer()

# email_service = EmailService()  # Instantiate once (or use dependency injection)

def create_agent_token(agent_id: int, owner_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=8)
    payload = {
        "agent_id": agent_id,
        "owner_id": owner_id,
        "role": "agent",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

class SendOtpRequest(BaseModel):
    email: str
    slug: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str
    security_code: str
    slug: str

@router.get("/owner-info/{slug}")
def get_owner_info(slug: str, db: Session = Depends(get_db)):
    # Slug is an encrypted token — look up via WhatsappConfig.dashboard_slug
    config = db.query(WhatsappConfig).filter(
        WhatsappConfig.dashboard_slug == slug
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Get the text agent to find the owner
    text_agent = config.text_agent
    if not text_agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get the owner (user)
    owner = db.query(User).filter(User.id == text_agent.user_id).first()

    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    return {"name": f"{owner.username}'s Dashboard", "username": owner.username}

@router.post("/send-otp")
def send_otp(
    payload: SendOtpRequest,
    db: Session = Depends(get_db)
):
    email = payload.email.strip().lower()

    # Find the owner/business from the slug
    config = db.query(WhatsappConfig).filter(
        WhatsappConfig.dashboard_slug == payload.slug
    ).first()

    if not config or not config.text_agent:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    owner_id = config.text_agent.user_id

    # Find the agent, ensuring they belong to this owner
    agent = db.query(HumanAgent).filter(
        HumanAgent.email == email,
        HumanAgent.is_active == True,
        HumanAgent.user_id == owner_id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not registered as an agent for this company"
        )

    otp = str(random.randint(100000, 999999))
    security_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Save OTP + Security Code (overloading expiry for both)
    agent.otp = f"{otp}:{security_code}"
    agent.otp_expiry = datetime.utcnow() + timedelta(minutes=10)

    db.commit()

    # Move email sending to Celery task
    subject = "Your Login Verification Codes"
    html_content = f"""
    <html>
        <body style='font-family: Arial, sans-serif;'>
            <h3>Hello {agent.name},</h3>
            <p>Use the following codes to log in:</p>
            <div style='background: #f1f5f9; padding: 15px; border-radius: 8px;'>
                <p><strong>OTP (6-digit):</strong> <span style='font-size: 20px;'>{otp}</span></p>
                <p><strong>Security Code:</strong> <span style='font-size: 20px;'>{security_code}</span></p>
            </div>
            <p>These codes will expire in 10 minutes.</p>
        </body>
    </html>
    """
    
    try:
        send_email_task.delay(email, subject, html_content)
    except Exception as e:
        logger.error(f"Failed to queue OTP email: {e}")
        # We don't necessarily want to fail the whole request if queueing fails, 
        # but the user won't get the email. For now, let's keep it consistent with other routes.
        # If we want to be strict, we could uncomment the rollback logic.
        # agent.otp = None
        # agent.otp_expiry = None
        # db.commit()
        # raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return {"message": "OTP sent successfully to your email"}

@router.post("/verify-otp")
def verify_otp(
    payload: VerifyOtpRequest,
    db: Session = Depends(get_db)
):
    email = payload.email.strip().lower()
    otp_input = payload.otp.strip()

    # Find the owner/business from the slug
    config = db.query(WhatsappConfig).filter(
        WhatsappConfig.dashboard_slug == payload.slug
    ).first()

    if not config or not config.text_agent:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    owner_id = config.text_agent.user_id

    # Verify the agent belongs to this exact dashboard's owner
    agent = db.query(HumanAgent).filter(
        HumanAgent.email == email,
        HumanAgent.user_id == owner_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")

    if not agent.otp or ":" not in agent.otp:
        raise HTTPException(status_code=400, detail="No active verification session")

    stored_otp, stored_security = agent.otp.split(":")

    if stored_otp != otp_input or stored_security != payload.security_code.strip().upper():
        raise HTTPException(status_code=400, detail="Invalid OTP or Security Code")

    if datetime.utcnow() > agent.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP expired")

    # Success: clear OTP, set online, issue token
    agent.otp = None
    agent.otp_expiry = None
    agent.is_online = True

    db.commit()

    token = create_agent_token(agent.id, agent.user_id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "agent_name": agent.name,
        "agent_id": agent.id,
        "owner_id": agent.user_id,
        "role": "agent"
    }

def get_current_agent(credentials=Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("role") != "agent":
            raise HTTPException(status_code=403, detail="Not authorized")

        return payload

    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

@router.get("/me")
def get_agent_profile(
    current_agent=Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    agent = db.query(HumanAgent).filter(
        HumanAgent.id == current_agent["agent_id"]
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "id": agent.id,
        "name": agent.name,
        "email": agent.email,
        "is_online": agent.is_online,
        "role": "agent"
    }
