"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional

class ReportPreferenceResponse(BaseModel):
    id: int
    user_id: int
    is_subscribed: bool
    frequency: str
    report_day: int
    report_hour: int
    last_report_sent_at: Optional[str]
    reports_sent_count: int
    
    class Config:
        from_attributes = True


class ReportPreferenceUpdate(BaseModel):
    is_subscribed: Optional[bool] = None
    frequency: Optional[str] = None
    report_day: Optional[int] = None
    report_hour: Optional[int] = None


class ReportJobResponse(BaseModel):
    id: int
    user_id: int
    report_type: str
    status: str
    scheduled_at: str
    completed_at: Optional[str]
    retry_count: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class ReportPreviewResponse(BaseModel):
    user: dict
    report_period: dict
    summary: dict
    daily_breakdown: list
    key_breakdown: list
    top_agents: list
    generated_at: str


class JobStatsResponse(BaseModel):
    pending: int
    processing: int
    completed: int
    failed: int
    cancelled: int