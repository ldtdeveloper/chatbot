"""
Scheduler Service using APScheduler
Manages cron jobs for weekly/monthly report generation

OPTIMIZED FOR 100K+ USERS:
- Batch size: 500 (was 50)
- Frequency: Every 1 minute (was 5 minutes)
- Concurrent processing: 10 workers
- Batched job creation: 1000 users per batch
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from app.database import SessionLocal
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from app.models.report import ReportFrequency, JobStatus


# ==================== SCALABILITY CONFIG ====================
BATCH_SIZE = 500           # Jobs per processing cycle (was 50)
PROCESS_INTERVAL = 1       # Minutes between processing (was 5)
MAX_WORKERS = 10           # Concurrent email workers
JOB_CREATION_BATCH = 1000  # Users per job creation batch
# ============================================================


class ReportScheduler:
    """Scheduler for automated report generation - Optimized for 100k+ users"""
    
    _instance: Optional['ReportScheduler'] = None
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='UTC')
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    
    @classmethod
    def get_instance(cls) -> 'ReportScheduler':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = ReportScheduler()
        return cls._instance
    
    def start(self):
        """Start the scheduler with all jobs"""
        if self.is_running:
            print("[Scheduler] Already running")
            return
        
        # Weekly report job creation - Every Monday at 8:00 UTC
        self.scheduler.add_job(
            func=self.create_weekly_report_jobs,
            trigger=CronTrigger(day_of_week='mon', hour=8, minute=0),
            id='create_weekly_jobs',
            name='Create weekly report jobs',
            replace_existing=True
        )
        
        # Monthly report job creation - 1st of every month at 8:00 UTC
        self.scheduler.add_job(
            func=self.create_monthly_report_jobs,
            trigger=CronTrigger(day=1, hour=8, minute=0),
            id='create_monthly_jobs',
            name='Create monthly report jobs',
            replace_existing=True
        )
        
        # Process pending jobs - Every 1 minute (optimized)
        self.scheduler.add_job(
            func=self.process_pending_jobs,
            trigger=CronTrigger(minute=f'*/{PROCESS_INTERVAL}'),
            id='process_pending_jobs',
            name='Process pending report jobs',
            replace_existing=True
        )
        
        # Retry failed jobs - Every 10 minutes
        self.scheduler.add_job(
            func=self.retry_failed_jobs,
            trigger=CronTrigger(minute='*/10'),
            id='retry_failed_jobs',
            name='Retry failed report jobs',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        print(f"[Scheduler] Started - Optimized for 100k+ users")
        print(f"[Scheduler] Config: batch={BATCH_SIZE}, interval={PROCESS_INTERVAL}min, workers={MAX_WORKERS}")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.executor.shutdown(wait=False)
            self.is_running = False
            print("[Scheduler] Stopped")
    
    def create_weekly_report_jobs(self):
        """Create report jobs for all weekly subscribers (batched for scale)"""
        print(f"[Scheduler] Creating weekly report jobs at {datetime.now(timezone.utc)}")
        db = SessionLocal()
        try:
            service = ReportService(db)
            jobs_created = service.create_report_jobs_batched(
                frequency=ReportFrequency.WEEKLY,
                batch_size=JOB_CREATION_BATCH
            )
            print(f"[Scheduler] Created {jobs_created} weekly report jobs")
        except Exception as e:
            print(f"[Scheduler] Error creating weekly jobs: {e}")
        finally:
            db.close()
    
    def create_monthly_report_jobs(self):
        """Create report jobs for all monthly subscribers (batched for scale)"""
        print(f"[Scheduler] Creating monthly report jobs at {datetime.now(timezone.utc)}")
        db = SessionLocal()
        try:
            service = ReportService(db)
            jobs_created = service.create_report_jobs_batched(
                frequency=ReportFrequency.MONTHLY,
                batch_size=JOB_CREATION_BATCH
            )
            print(f"[Scheduler] Created {jobs_created} monthly report jobs")
        except Exception as e:
            print(f"[Scheduler] Error creating monthly jobs: {e}")
        finally:
            db.close()
    
    def _process_single_job(self, job_id: int) -> tuple:
        """Process a single job in a worker thread"""
        db = SessionLocal()
        try:
            report_service = ReportService(db)
            email_service = EmailService()
            
            job = db.query(report_service.db.query.__self__.query(
                __import__('app.models.report', fromlist=['ReportJob']).ReportJob
            ).filter_by(id=job_id).first().__class__).filter_by(id=job_id).first()
            
            from app.models.report import ReportJob
            job = db.query(ReportJob).filter(ReportJob.id == job_id).first()
            
            if not job:
                return (job_id, False, "Job not found")
            
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now(timezone.utc)
            db.commit()
            
            # Generate report
            report_data = report_service.generate_report_data(
                user_id=job.user_id,
                frequency=job.report_type
            )
            
            if not report_data:
                job.status = JobStatus.FAILED
                job.error_message = "User not found"
                db.commit()
                return (job_id, False, "User not found")
            
            # Send email
            email_service.send_report(report_data)
            
            # Mark completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            
            return (job_id, True, None)
            
        except Exception as e:
            try:
                from app.models.report import ReportJob
                job = db.query(ReportJob).filter(ReportJob.id == job_id).first()
                if job:
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)[:500]
                    job.retry_count += 1
                    db.commit()
            except:
                pass
            return (job_id, False, str(e))
        finally:
            db.close()
    
    def process_pending_jobs(self, batch_size: int = BATCH_SIZE):
        """Process pending report jobs with concurrent workers"""
        db = SessionLocal()
        start_time = time.time()
        
        try:
            report_service = ReportService(db)
            jobs = report_service.get_pending_jobs(batch_size)
            
            if not jobs:
                return
            
            job_ids = [job.id for job in jobs]
            print(f"[Scheduler] Processing {len(job_ids)} jobs with {MAX_WORKERS} workers...")
            
            # Process concurrently
            success_count = 0
            fail_count = 0
            
            futures = {
                self.executor.submit(self._process_single_job, job_id): job_id 
                for job_id in job_ids
            }
            
            for future in as_completed(futures):
                job_id, success, error = future.result()
                if success:
                    success_count += 1
                else:
                    fail_count += 1
            
            elapsed = time.time() - start_time
            rate = len(job_ids) / elapsed if elapsed > 0 else 0
            
            print(f"[Scheduler] Completed: {success_count} ok, {fail_count} failed in {elapsed:.1f}s ({rate:.0f} jobs/sec)")
        
        except Exception as e:
            print(f"[Scheduler] Error processing jobs: {e}")
        finally:
            db.close()
    
    def retry_failed_jobs(self, batch_size: int = 100):
        """Retry failed jobs that are eligible for retry"""
        db = SessionLocal()
        try:
            report_service = ReportService(db)
            jobs = report_service.get_retry_jobs(batch_size)
            
            if not jobs:
                return
            
            print(f"[Scheduler] Retrying {len(jobs)} failed jobs")
            
            # Reset status to pending for retry
            for job in jobs:
                job.status = JobStatus.PENDING
            db.commit()
            
        except Exception as e:
            print(f"[Scheduler] Error retrying jobs: {e}")
        finally:
            db.close()
    
    def get_jobs_info(self) -> list:
        """Get info about scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None
            })
        return jobs
    
    def get_throughput_estimate(self, total_users: int) -> dict:
        """Estimate time to process all users"""
        jobs_per_minute = BATCH_SIZE  # With 1-minute interval
        jobs_per_hour = jobs_per_minute * 60
        hours_needed = total_users / jobs_per_hour
        
        return {
            "total_users": total_users,
            "batch_size": BATCH_SIZE,
            "workers": MAX_WORKERS,
            "jobs_per_hour": jobs_per_hour,
            "estimated_hours": round(hours_needed, 2),
            "estimated_time": f"{hours_needed:.1f} hours" if hours_needed < 24 else f"{hours_needed/24:.1f} days"
        }


# Global scheduler instance
scheduler = ReportScheduler.get_instance()
