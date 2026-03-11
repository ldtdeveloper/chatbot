from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    text_agent_id = Column(Integer, ForeignKey("text_agents.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)

    # Human takeover control
    is_human_active = Column(Boolean, default=False)
    human_agent_id = Column(Integer, ForeignKey("human_agents.id"), nullable=True)

    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete"
    )

    contact = relationship("Contact", back_populates="conversations")
    text_agent = relationship("TextAgent", back_populates="conversations")
    human_agent = relationship("HumanAgent", back_populates="conversations")