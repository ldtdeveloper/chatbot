from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.human_agent import HumanAgent
from app.models.user import User
from app.models.text_agents import TextAgent
from app.models.whatsapp_configs import WhatsappConfig
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.tasks.email_task import send_email_task

router = APIRouter(prefix="/api/human-agents", tags=["Employee Management"])

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    is_online: bool

    class Config:
        from_attributes = True

@router.post("", response_model=EmployeeResponse)
def add_employee(
    payload: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin adds a new employee"""
    # Check if employee already exists
    existing = db.query(HumanAgent).filter(HumanAgent.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists."
        )

    new_agent = HumanAgent(
        name=payload.name,
        email=payload.email,
        user_id=current_user.id,
        is_active=True
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    # Look up the encrypted dashboard slug from the user's WhatsApp agent config
    wa_agent = db.query(TextAgent).filter(
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).first()
    config = wa_agent.whatsapp_config if wa_agent else None
    slug = config.dashboard_slug if config and config.dashboard_slug else current_user.username
    login_url = f"{settings.frontend_base_url}/agent-login/{slug}"
    subject = "Employee Login URL for WhatsApp Agent"
    email_html = f"""
    <html>
        <body style='font-family: Arial, sans-serif;'>
            <h3>Hello {new_agent.name},</h3>
            <p>You have been added as an agent. You can log in to manage conversations at:</p>
            <div style='background: #f1f5f9; padding: 15px; border-radius: 8px;'>
                <p><a href="{login_url}">{login_url}</a></p>
            </div>
            <p>Thank you for using our platform.</p>
        </body>
    </html>
    """
    try:
        send_email_task.delay(new_agent.email, subject, email_html)
    except Exception as e:
        print(f"Failed to send email to {new_agent.email}: {e}")

    return new_agent

@router.get("", response_model=List[EmployeeResponse])
def list_employees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all employees for the user"""
    employees = db.query(HumanAgent).filter(
        HumanAgent.user_id == current_user.id
    ).all()
    return employees

@router.delete("/{agent_id}")
def remove_employee(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an employee"""
    agent = db.query(HumanAgent).filter(
        HumanAgent.id == agent_id,
        HumanAgent.user_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(agent)
    db.commit()
    return {"message": "Employee removed successfully"}
