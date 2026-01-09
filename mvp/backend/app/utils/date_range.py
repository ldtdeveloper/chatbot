from datetime import datetime, timedelta, timezone


def get_date_range(days: str) -> tuple:
    """Convert days string to date range (timezone-aware)"""
    now = datetime.now(timezone.utc)
    
    if days == '7d':
        start_date = now - timedelta(days=7)
    elif days == '30d':
        start_date = now - timedelta(days=30)
    elif days == '90d':
        start_date = now - timedelta(days=90)
    elif days == 'today':
        # Start of today
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif days == 'this_week':
        # Start of this week (Monday)
        days_since_monday = now.weekday()
        start_date = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif days == 'this_month':
        # Start of this month
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif days == 'this_year':
        # Start of this year
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif days == 'till_now' or days == 'all':
        # All time - use a very old date
        start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
    else:
        # Default to 30 days
        start_date = now - timedelta(days=30)
    
    return start_date, now


def get_previous_period_range(days: str) -> tuple:
    """Get the previous period range for comparison (timezone-aware)"""
    now = datetime.now(timezone.utc)
    
    if days == '7d':
        period_days = 7
    elif days == '30d':
        period_days = 30
    elif days == '90d':
        period_days = 90
    else:
        period_days = 30
    
    current_start = now - timedelta(days=period_days)
    previous_start = current_start - timedelta(days=period_days)
    previous_end = current_start
    
    return previous_start, previous_end

