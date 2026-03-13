from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class HumanAgent(Base):
    __tablename__ = "human_agents"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)

    # OTP fields
    otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="human_agents")

    conversations = relationship("Conversation", back_populates="human_agent")