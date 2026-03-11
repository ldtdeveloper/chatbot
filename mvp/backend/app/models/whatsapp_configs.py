from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class WhatsappConfig(Base):
    __tablename__ = "whatsapp_configs"

    id = Column(Integer, primary_key=True, index=True)
    text_agent_id = Column(Integer, ForeignKey("text_agents.id"), unique=True, nullable=False)

    phone_number_id = Column(String(50), nullable=True, index=True)
    phone_number= Column(String(50),nullable=True,index=True)
    access_token = Column(Text, nullable=True)
    business_id = Column(String(50), nullable=True)
    dashboard_slug = Column(String, unique=True, index=True)

    status = Column(String(30), default="pending")
    connected_at = Column(DateTime(timezone=True), nullable=True)
    last_webhook_received_at = Column(DateTime(timezone=True), nullable=True)

    webhook_verify_token = Column(String(100), nullable=True)
    text_agent = relationship(
        "TextAgent",
        back_populates="whatsapp_config"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

   