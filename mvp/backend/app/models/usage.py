"""
Usage model for plan management by superadmin
"""
from sqlalchemy import Column, Integer, String,ForeignKey,DateTime
from app.core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class UserMinuteBalance(Base):
    __tablename__ = "user_min_balance"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    total_minutes = Column(Integer, nullable=False)
    used_minutes = Column(Integer, nullable=False, default=0)
    remaining_minutes = Column(Integer, nullable=False)

    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

        
    # Relationships
    user = relationship("User", back_populates="user_min_balance", uselist=False)