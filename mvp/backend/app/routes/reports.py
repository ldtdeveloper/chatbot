"""
Reports API Routes
Endpoints for managing user report preferences and triggering reports
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import  List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.report import (
    UserReportPreference, ReportJob, ReportFrequency
)
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from app.schemas.reports import ReportJobResponse,ReportPreferenceUpdate,ReportPreferenceResponse,ReportPreviewResponse,JobStatsResponse


router = APIRouter(prefix="/api/reports", tags=["Reports"])

# ==================== User Preferences ====================

@router.get("/preferences", response_model=ReportPreferenceResponse)
async def get_report_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's report preferences"""
    pref = db.query(UserReportPreference).filter(
        UserReportPreference.user_id == current_user.id
    ).first()
    
    if not pref:
        # Create default preferences
        pref = UserReportPreference(
            user_id=current_user.id,
            is_subscribed=True,
            frequency=ReportFrequency.WEEKLY,
            report_day=0,
            report_hour=9
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
    
    return ReportPreferenceResponse(
        id=pref.id,
        user_id=pref.user_id,
        is_subscribed=pref.is_subscribed,
        frequency=pref.frequency.value if pref.frequency else "weekly",
        report_day=pref.report_day,
        report_hour=pref.report_hour,
        last_report_sent_at=pref.last_report_sent_at.isoformat() if pref.last_report_sent_at else None,
        reports_sent_count=pref.reports_sent_count
    )


@router.put("/preferences", response_model=ReportPreferenceResponse)
async def update_report_preferences(
    update: ReportPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's report preferences"""
    pref = db.query(UserReportPreference).filter(
        UserReportPreference.user_id == current_user.id
    ).first()
    
    if not pref:
        pref = UserReportPreference(user_id=current_user.id)
        db.add(pref)
    
    if update.is_subscribed is not None:
        pref.is_subscribed = update.is_subscribed
    
    if update.frequency is not None:
        if update.frequency not in ['weekly', 'monthly']:
            raise HTTPException(status_code=400, detail="Invalid frequency")
        pref.frequency = ReportFrequency(update.frequency)
    
    if update.report_day is not None:
        if pref.frequency == ReportFrequency.WEEKLY and not 0 <= update.report_day <= 6:
            raise HTTPException(status_code=400, detail="Weekly report_day must be 0-6")
        if pref.frequency == ReportFrequency.MONTHLY and not 1 <= update.report_day <= 28:
            raise HTTPException(status_code=400, detail="Monthly report_day must be 1-28")
        pref.report_day = update.report_day
    
    if update.report_hour is not None:
        if not 0 <= update.report_hour <= 23:
            raise HTTPException(status_code=400, detail="report_hour must be 0-23")
        pref.report_hour = update.report_hour
    
    db.commit()
    db.refresh(pref)
    
    return ReportPreferenceResponse(
        id=pref.id,
        user_id=pref.user_id,
        is_subscribed=pref.is_subscribed,
        frequency=pref.frequency.value if pref.frequency else "weekly",
        report_day=pref.report_day,
        report_hour=pref.report_hour,
        last_report_sent_at=pref.last_report_sent_at.isoformat() if pref.last_report_sent_at else None,
        reports_sent_count=pref.reports_sent_count
    )


@router.post("/unsubscribe")
async def unsubscribe_from_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe from all reports"""
    pref = db.query(UserReportPreference).filter(
        UserReportPreference.user_id == current_user.id
    ).first()
    
    if not pref:
        pref = UserReportPreference(user_id=current_user.id, is_subscribed=False)
        db.add(pref)
    else:
        pref.is_subscribed = False
    
    db.commit()
    
    return {"message": "Successfully unsubscribed from reports"}


# ==================== Report Preview & Trigger ====================

@router.get("/preview", response_model=ReportPreviewResponse)
async def preview_report(
    frequency: str = Query(default="weekly", regex="^(weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview what the report would look like for current user"""
    report_service = ReportService(db)
    
    freq = ReportFrequency.WEEKLY if frequency == "weekly" else ReportFrequency.MONTHLY
    report_data = report_service.generate_report_data(current_user.id, freq)
    
    if not report_data:
        raise HTTPException(status_code=404, detail="Could not generate report")
    
    return report_data


@router.get("/preview/html")
async def preview_report_html(
    frequency: str = Query(default="weekly", regex="^(weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview the HTML email template"""
    from fastapi.responses import HTMLResponse
    
    report_service = ReportService(db)
    email_service = EmailService()
    
    freq = ReportFrequency.WEEKLY if frequency == "weekly" else ReportFrequency.MONTHLY
    report_data = report_service.generate_report_data(current_user.id, freq)
    
    if not report_data:
        raise HTTPException(status_code=404, detail="Could not generate report")
    
    html = email_service.generate_report_html(report_data)
    return HTMLResponse(content=html)


@router.post("/send-test")
async def send_test_report(
    frequency: str = Query(default="weekly", regex="^(weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a test report to the current user's email"""
    report_service = ReportService(db)
    email_service = EmailService()
    
    freq = ReportFrequency.WEEKLY if frequency == "weekly" else ReportFrequency.MONTHLY
    report_data = report_service.generate_report_data(current_user.id, freq)
    
    if not report_data:
        raise HTTPException(status_code=404, detail="Could not generate report")
    
    try:
        email_service.send_report(report_data)
        return {"message": f"Test report sent to {current_user.email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


# ==================== Job History ====================

@router.get("/history", response_model=List[ReportJobResponse])
async def get_report_history(
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report job history for current user"""
    jobs = db.query(ReportJob).filter(
        ReportJob.user_id == current_user.id
    ).order_by(
        ReportJob.created_at.desc()
    ).limit(limit).all()
    
    return [
        ReportJobResponse(
            id=job.id,
            user_id=job.user_id,
            report_type=job.report_type.value if job.report_type else "weekly",
            status=job.status.value if job.status else "pending",
            scheduled_at=job.scheduled_at.isoformat() if job.scheduled_at else "",
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            retry_count=job.retry_count,
            error_message=job.error_message
        )
        for job in jobs
    ]


# ==================== Admin Endpoints ====================

@router.get("/admin/stats", response_model=JobStatsResponse)
async def get_job_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job queue statistics (Admin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    report_service = ReportService(db)
    stats = report_service.get_job_stats()
    
    return JobStatsResponse(
        pending=stats.get('pending', 0),
        processing=stats.get('processing', 0),
        completed=stats.get('completed', 0),
        failed=stats.get('failed', 0),
        cancelled=stats.get('cancelled', 0)
    )


@router.post("/admin/trigger-weekly")
async def trigger_weekly_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger weekly report job creation (Admin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    report_service = ReportService(db)
    jobs_created = report_service.create_report_jobs_for_all_users(
        frequency=ReportFrequency.WEEKLY
    )
    
    return {"message": f"Created {jobs_created} weekly report jobs"}


@router.post("/admin/trigger-monthly")
async def trigger_monthly_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger monthly report job creation (Admin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    report_service = ReportService(db)
    jobs_created = report_service.create_report_jobs_for_all_users(
        frequency=ReportFrequency.MONTHLY
    )
    
    return {"message": f"Created {jobs_created} monthly report jobs"}


@router.post("/admin/process-now")
async def process_jobs_now(
    batch_size: int = Query(default=50, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually process pending jobs now (Admin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.scheduler import scheduler
    scheduler.process_pending_jobs(batch_size)
    
    return {"message": f"Processing up to {batch_size} pending jobs"}


@router.get("/admin/scheduler-info")
async def get_scheduler_info(
    current_user: User = Depends(get_current_user)
):
    """Get scheduler job information (Admin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.scheduler import scheduler
    
    return {
        "is_running": scheduler.is_running,
        "jobs": scheduler.get_jobs_info()
    }

