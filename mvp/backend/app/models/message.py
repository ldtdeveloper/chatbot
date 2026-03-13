from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)

    content = Column(String, nullable=False)

    # Who sent the message?
    is_from_contact = Column(Boolean, default=True)
    is_from_agent = Column(Boolean, default=False)
    # If both False → AI message

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")