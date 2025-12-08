"""
Report models for weekly/monthly report generation and tracking
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ReportFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserReportPreference(Base):
    """
    Stores user preferences for report delivery
    """
    __tablename__ = "user_report_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Subscription settings
    is_subscribed = Column(Boolean, default=True)  # User opted in for reports
    frequency = Column(Enum(ReportFrequency), default=ReportFrequency.WEEKLY)
    report_day = Column(Integer, default=0)  # 0=Monday for weekly, 1-28 for monthly
    report_hour = Column(Integer, default=9)  # Hour of day (0-23) in UTC
    
    # Tracking
    last_report_sent_at = Column(DateTime(timezone=True), nullable=True)
    reports_sent_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="report_preference")


class ReportJob(Base):
    """
    Job queue for report generation - tracks each report task
    """
    __tablename__ = "report_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Job details
    report_type = Column(Enum(ReportFrequency), default=ReportFrequency.WEEKLY)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    priority = Column(Integer, default=0)  # Higher = more urgent
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)  # When job should run
    started_at = Column(DateTime(timezone=True), nullable=True)  # When processing started
    completed_at = Column(DateTime(timezone=True), nullable=True)  # When job finished
    
    # Report period (what dates the report covers)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Report data (cached for retries)
    report_data = Column(Text, nullable=True)  # JSON string of report data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="report_jobs")
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.retry_count < self.max_retries and self.status == JobStatus.FAILED

