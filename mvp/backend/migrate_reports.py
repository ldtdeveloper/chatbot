"""
Migration script to create report-related tables
Run this script to set up UserReportPreference and ReportJob tables
"""
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
import enum
from sqlalchemy import text  # lowercase!

from app.config import settings

# Create engine
engine = create_engine(settings.database_url)
metadata = MetaData()

# Define enum values for PostgreSQL
class ReportFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def create_tables():
    """Create the report tables"""
    
    # UserReportPreference table
    user_report_preferences = Table(
        'user_report_preferences',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False, unique=True),
        Column('is_subscribed', Boolean, default=True),
        Column('frequency', String(20), default='weekly'),
        Column('report_day', Integer, default=0),
        Column('report_hour', Integer, default=9),
        Column('last_report_sent_at', DateTime(timezone=True), nullable=True),
        Column('reports_sent_count', Integer, default=0),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    # ReportJob table
    report_jobs = Table(
        'report_jobs',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False, index=True),
        Column('report_type', String(20), default='weekly'),
        Column('status', String(20), default='pending', index=True),
        Column('priority', Integer, default=0),
        Column('scheduled_at', DateTime(timezone=True), nullable=False),
        Column('started_at', DateTime(timezone=True), nullable=True),
        Column('completed_at', DateTime(timezone=True), nullable=True),
        Column('period_start', DateTime(timezone=True), nullable=False),
        Column('period_end', DateTime(timezone=True), nullable=False),
        Column('retry_count', Integer, default=0),
        Column('max_retries', Integer, default=3),
        Column('next_retry_at', DateTime(timezone=True), nullable=True),
        Column('error_message', Text, nullable=True),
        Column('report_data', Text, nullable=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    # Create tables
    print("Creating report tables...")
    metadata.create_all(engine)
    print("✅ Tables created successfully!")
    
    # Verify
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name IN ('user_report_preferences', 'report_jobs')"))
         
        tables = [row[0] for row in result.fetchall()]
        print(f"Created tables: {tables}")


if __name__ == "__main__":
    create_tables()

