"""
Report Generation Service
Generates weekly/monthly reports for users with their dashboard statistics
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.openai_key import OpenAIKey
from app.models.agent import Agent
from app.models.interaction import Interaction
from app.models.report import (
    UserReportPreference, ReportJob, ReportFrequency, JobStatus
)


class ReportService:
    """Service for generating user reports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_report_period(self, frequency: ReportFrequency) -> tuple:
        """Get the start and end dates for the report period"""
        now = datetime.now(timezone.utc)
        
        if frequency == ReportFrequency.WEEKLY:
            period_end = now
            period_start = now - timedelta(days=7)
        else:
            period_end = now
            period_start = now - timedelta(days=30)
        
        return period_start, period_end
    
    def get_previous_period(self, frequency: ReportFrequency, period_start: datetime) -> tuple:
        """Get the previous period for comparison"""
        if frequency == ReportFrequency.WEEKLY:
            prev_end = period_start
            prev_start = period_start - timedelta(days=7)
        else:
            prev_end = period_start
            prev_start = period_start - timedelta(days=30)
        
        return prev_start, prev_end
    
    def generate_report_data(
        self, 
        user_id: int, 
        frequency: ReportFrequency = ReportFrequency.WEEKLY
    ) -> Dict[str, Any]:
        """Generate report data for a user"""
        period_start, period_end = self.get_report_period(frequency)
        prev_start, prev_end = self.get_previous_period(frequency, period_start)
        
        # Get user info
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get user's API keys
        keys = self.db.query(OpenAIKey).filter(OpenAIKey.user_id == user_id).all()
        key_ids = [k.id for k in keys]
        
        # Current period interactions
        current_interactions = self.db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.started_at >= period_start,
            Interaction.started_at <= period_end
        ).all()
        
        # Previous period interactions
        prev_interactions = self.db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.started_at >= prev_start,
            Interaction.started_at <= prev_end
        ).all()
        
        # Calculate totals
        total_interactions = len(current_interactions)
        total_expenses = sum(i.estimated_cost or 0 for i in current_interactions)
        total_duration = sum(i.duration_seconds or 0 for i in current_interactions)
        
        prev_total_interactions = len(prev_interactions)
        prev_total_expenses = sum(i.estimated_cost or 0 for i in prev_interactions)
        
        # Calculate percentage changes
        if prev_total_interactions > 0:
            interactions_change = ((total_interactions - prev_total_interactions) / prev_total_interactions) * 100
        else:
            interactions_change = 100.0 if total_interactions > 0 else 0.0
        
        if prev_total_expenses > 0:
            expenses_change = ((total_expenses - prev_total_expenses) / prev_total_expenses) * 100
        else:
            expenses_change = 100.0 if total_expenses > 0 else 0.0
        
        # Get agent count
        total_agents = self.db.query(Agent).filter(Agent.user_id == user_id).count()
        
        # Get active keys count
        active_keys = len([k for k in keys if k.is_active])
        
        # Daily breakdown
        daily_stats = []
        days = 7 if frequency == ReportFrequency.WEEKLY else 30
        for i in range(days):
            day = period_end - timedelta(days=days - 1 - i)
            day_date = day.date()
            
            day_interactions = [
                inter for inter in current_interactions
                if inter.started_at and inter.started_at.date() == day_date
            ]
            
            daily_stats.append({
                'date': day_date.strftime('%Y-%m-%d'),
                'interactions': len(day_interactions),
                'expenses': round(sum(inter.estimated_cost or 0 for inter in day_interactions), 2)
            })
        
        # Per-key breakdown
        key_stats = []
        for key in keys:
            key_interactions = [
                inter for inter in current_interactions
                if inter.openai_key_id == key.id
            ]
            key_agents = self.db.query(Agent).filter(
                Agent.user_id == user_id,
                Agent.openai_key_id == key.id
            ).count()
            
            key_stats.append({
                'key_name': key.key_name,
                'key_id': key.id,
                'is_active': key.is_active,
                'interactions': len(key_interactions),
                'expenses': round(sum(inter.estimated_cost or 0 for inter in key_interactions), 2),
                'agents': key_agents
            })
        
        # Top agents by usage
        agent_usage = {}
        for inter in current_interactions:
            if inter.agent_id:
                if inter.agent_id not in agent_usage:
                    agent_usage[inter.agent_id] = {'count': 0, 'cost': 0}
                agent_usage[inter.agent_id]['count'] += 1
                agent_usage[inter.agent_id]['cost'] += inter.estimated_cost or 0
        
        top_agents = []
        for agent_id, usage in sorted(agent_usage.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                top_agents.append({
                    'name': agent.name,
                    'interactions': usage['count'],
                    'expenses': round(usage['cost'], 2)
                })
        
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            },
            'report_period': {
                'start': period_start.isoformat(),
                'end': period_end.isoformat(),
                'frequency': frequency.value
            },
            'summary': {
                'total_interactions': total_interactions,
                'total_expenses': round(total_expenses, 2),
                'total_duration_minutes': round(total_duration / 60, 1),
                'total_agents': total_agents,
                'active_keys': active_keys,
                'interactions_change': round(interactions_change, 1),
                'expenses_change': round(expenses_change, 1)
            },
            'daily_breakdown': daily_stats,
            'key_breakdown': key_stats,
            'top_agents': top_agents,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def create_report_jobs_for_all_users(
        self, 
        frequency: ReportFrequency = ReportFrequency.WEEKLY,
        scheduled_at: datetime = None
    ) -> int:
        """Create report jobs for all subscribed users"""
        if scheduled_at is None:
            scheduled_at = datetime.now(timezone.utc)
        
        period_start, period_end = self.get_report_period(frequency)
        
        # Get all active users
        users = self.db.query(User).filter(User.is_active == True).all()
        
        jobs_created = 0
        
        for user in users:
            # Check user preferences
            pref = self.db.query(UserReportPreference).filter(
                UserReportPreference.user_id == user.id
            ).first()
            
            # Skip if user explicitly unsubscribed
            if pref and not pref.is_subscribed:
                continue
            
            # Skip if preference exists but frequency doesn't match
            if pref and pref.frequency != frequency:
                continue
            
            # Check if job already exists for this period
            existing_job = self.db.query(ReportJob).filter(
                ReportJob.user_id == user.id,
                ReportJob.report_type == frequency,
                ReportJob.period_start == period_start,
                ReportJob.period_end == period_end,
                ReportJob.status.in_([JobStatus.PENDING, JobStatus.PROCESSING, JobStatus.COMPLETED])
            ).first()
            
            if existing_job:
                continue
            
            # Create new job
            job = ReportJob(
                user_id=user.id,
                report_type=frequency,
                status=JobStatus.PENDING,
                scheduled_at=scheduled_at,
                period_start=period_start,
                period_end=period_end
            )
            self.db.add(job)
            jobs_created += 1
        
        self.db.commit()
        return jobs_created
    
    def create_report_jobs_batched(
        self, 
        frequency: ReportFrequency = ReportFrequency.WEEKLY,
        batch_size: int = 1000,
        scheduled_at: datetime = None
    ) -> int:
        """
        Create report jobs in batches for scalability (100k+ users)
        Uses pagination to avoid loading all users into memory
        """
        if scheduled_at is None:
            scheduled_at = datetime.now(timezone.utc)
        
        period_start, period_end = self.get_report_period(frequency)
        
        jobs_created = 0
        offset = 0
        
        while True:
            # Fetch users in batches using pagination
            users_batch = self.db.query(User).filter(
                User.is_active == True
            ).offset(offset).limit(batch_size).all()
            
            if not users_batch:
                break  # No more users
            
            batch_jobs = []
            
            for user in users_batch:
                # Check user preferences
                pref = self.db.query(UserReportPreference).filter(
                    UserReportPreference.user_id == user.id
                ).first()
                
                # Skip if user explicitly unsubscribed
                if pref and not pref.is_subscribed:
                    continue
                
                # Skip if preference exists but frequency doesn't match
                if pref and pref.frequency != frequency:
                    continue
                
                # Check if job already exists for this period
                existing_job = self.db.query(ReportJob).filter(
                    ReportJob.user_id == user.id,
                    ReportJob.report_type == frequency,
                    ReportJob.period_start == period_start,
                    ReportJob.period_end == period_end,
                    ReportJob.status.in_([JobStatus.PENDING, JobStatus.PROCESSING, JobStatus.COMPLETED])
                ).first()
                
                if existing_job:
                    continue
                
                # Create new job
                batch_jobs.append(ReportJob(
                    user_id=user.id,
                    report_type=frequency,
                    status=JobStatus.PENDING,
                    scheduled_at=scheduled_at,
                    period_start=period_start,
                    period_end=period_end
                ))
            
            # Bulk insert batch
            if batch_jobs:
                self.db.bulk_save_objects(batch_jobs)
                self.db.commit()
                jobs_created += len(batch_jobs)
                print(f"[ReportService] Created batch of {len(batch_jobs)} jobs (total: {jobs_created})")
            
            offset += batch_size
            
            # Safety check - if we've processed 500k users, something might be wrong
            if offset > 500000:
                print(f"[ReportService] Warning: Processed {offset} users, stopping as safety measure")
                break
        
        return jobs_created
    
    def get_pending_jobs(self, batch_size: int = 500) -> List[ReportJob]:
        """Get pending jobs for processing"""
        now = datetime.now(timezone.utc)
        
        jobs = self.db.query(ReportJob).filter(
            ReportJob.status == JobStatus.PENDING,
            ReportJob.scheduled_at <= now
        ).order_by(
            ReportJob.priority.desc(),
            ReportJob.scheduled_at.asc()
        ).limit(batch_size).all()
        
        return jobs
    
    def get_retry_jobs(self, batch_size: int = 20) -> List[ReportJob]:
        """Get failed jobs that can be retried"""
        now = datetime.now(timezone.utc)
        
        jobs = self.db.query(ReportJob).filter(
            ReportJob.status == JobStatus.FAILED,
            ReportJob.retry_count < ReportJob.max_retries,
            ReportJob.next_retry_at <= now
        ).order_by(
            ReportJob.next_retry_at.asc()
        ).limit(batch_size).all()
        
        return jobs
    
    def mark_job_processing(self, job: ReportJob) -> None:
        """Mark a job as being processed"""
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        self.db.commit()
    
    def mark_job_completed(self, job: ReportJob, report_data: dict = None) -> None:
        """Mark a job as completed"""
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        if report_data:
            job.report_data = json.dumps(report_data)
        
        # Update user's last report sent time
        pref = self.db.query(UserReportPreference).filter(
            UserReportPreference.user_id == job.user_id
        ).first()
        
        if pref:
            pref.last_report_sent_at = datetime.now(timezone.utc)
            pref.reports_sent_count += 1
        
        self.db.commit()
    
    def mark_job_failed(self, job: ReportJob, error_message: str) -> None:
        """Mark a job as failed"""
        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.retry_count += 1
        
        # Schedule retry with exponential backoff
        if job.can_retry():
            backoff_minutes = 5 * (2 ** job.retry_count)
            job.next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=backoff_minutes)
        
        self.db.commit()
    
    def get_job_stats(self) -> Dict[str, int]:
        """Get statistics about report jobs"""
        stats = {}
        for status in JobStatus:
            count = self.db.query(ReportJob).filter(
                ReportJob.status == status
            ).count()
            stats[status.value] = count
        return stats
