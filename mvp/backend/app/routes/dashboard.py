"""
Dashboard routes - statistics and analytics endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, cast, Date
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.openai_key import OpenAIKey
from app.models.agent import Agent
from app.models.interaction import Interaction
from app.schemas import DashboardStats
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Colors for charts (matching frontend)
CHART_COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']


def get_date_range(days: str) -> tuple:
    """Convert days string to date range (timezone-aware)"""
    now = datetime.now(timezone.utc)
    
    if days == '7d':
        start_date = now - timedelta(days=7)
    elif days == '30d':
        start_date = now - timedelta(days=30)
    elif days == '90d':
        start_date = now - timedelta(days=90)
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


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    days: str = Query(default="30d", regex="^(7d|30d|90d)$"),
    key_id: Optional[int] = Query(default=None, description="Filter by specific API key ID"),
    user_id: Optional[int] = Query(default=None, description="Filter by user ID (superadmin only)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics with optional filters
    
    - **days**: Time range filter (7d, 30d, 90d)
    - **key_id**: Optional API key ID filter (null = all keys)
    - **user_id**: Optional user ID filter (superadmin only, null = all users for superadmin)
    """
    try:
        start_date, end_date = get_date_range(days)
        prev_start, prev_end = get_previous_period_range(days)
        
        # Check if user is superadmin - handle both enum and string comparison
        is_superadmin = False
        if hasattr(current_user.role, 'value'):
            is_superadmin = current_user.role.value == UserRole.SUPERADMIN.value
        else:
            is_superadmin = str(current_user.role) == str(UserRole.SUPERADMIN.value) or current_user.role == UserRole.SUPERADMIN
        
        # Determine which user(s) to query for
        if is_superadmin:
            # Superadmin can see all users or filter by specific user
            if user_id:
                target_user_ids = [user_id]
            else:
                # Get all user IDs - handle empty result
                all_users = db.query(User).all()
                target_user_ids = [u.id for u in all_users] if all_users else []
        else:
            # Regular users can only see their own data
            target_user_ids = [current_user.id] if current_user.id else []
        
        # Handle empty user list
        if not target_user_ids:
            return DashboardStats(
                total_interactions=0,
                total_expenses=0.0,
                total_agents=0,
                active_keys=0,
                interactions_change=0.0,
                expenses_change=0.0,
                interactions_chart=[],
                expenses_chart=[],
                agents_per_key=[],
                available_keys=[]
            )
        
        # Get API keys for target users
        all_keys = db.query(OpenAIKey).filter(OpenAIKey.user_id.in_(target_user_ids)).all()
        
        # Filter keys if specific key_id provided
        if key_id:
            filtered_keys = [k for k in all_keys if k.id == key_id]
        else:
            filtered_keys = all_keys if all_keys else []
        
        key_ids = [k.id for k in filtered_keys] if filtered_keys else []
        
        # Build base query for interactions - handle empty key_ids
        def build_interaction_query(start, end, key_ids_list):
            query = db.query(Interaction).filter(
                Interaction.user_id.in_(target_user_ids),
                Interaction.started_at.isnot(None),
                Interaction.started_at >= start,
                Interaction.started_at <= end
            )
            if key_ids_list:
                query = query.filter(Interaction.openai_key_id.in_(key_ids_list))
            return query
        
        # Current period stats
        current_interactions = build_interaction_query(start_date, end_date, key_ids).all()
        total_interactions = len(current_interactions)
        total_expenses = sum((i.estimated_cost or 0) for i in current_interactions)
        
        # Previous period stats for comparison
        prev_interactions = build_interaction_query(prev_start, prev_end, key_ids).all()
        prev_total_interactions = len(prev_interactions)
        prev_total_expenses = sum((i.estimated_cost or 0) for i in prev_interactions)
        
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
        agents_query = db.query(Agent).filter(Agent.user_id.in_(target_user_ids))
        if key_ids:
            agents_query = agents_query.filter(Agent.openai_key_id.in_(key_ids))
        total_agents = agents_query.count()
        
        # Get active keys count
        active_keys = len([k for k in filtered_keys if k.is_active]) if filtered_keys else 0
        
        # Build interactions chart data (daily aggregation)
        interactions_chart = []
        expenses_chart = []
        
        # Determine number of days for chart
        if days == '7d':
            num_days = 7
        elif days == '30d':
            num_days = 30
        else:
            num_days = 90
        
        # Create a mapping of key_id to key_name - handle None key_name
        key_name_map = {k.id: (k.key_name or f"Key {k.id}") for k in all_keys if k.key_name is not None}
        
        for i in range(num_days):
            day = end_date - timedelta(days=num_days - 1 - i)
            day_date = day.date()  # Just the date part for comparison
            
            interaction_point = {'date': day_date.strftime('%Y-%m-%d')}
            expense_point = {'date': day_date.strftime('%Y-%m-%d')}
            
            # Handle empty filtered_keys
            if filtered_keys:
                for key in filtered_keys:
                    key_name = key.key_name or f"Key {key.id}"
                    # Compare by date part only to avoid timezone issues
                    key_interactions = [
                        inter for inter in current_interactions 
                        if inter.openai_key_id == key.id 
                        and inter.started_at is not None
                        and hasattr(inter.started_at, 'date')
                        and inter.started_at.date() == day_date
                    ]
                    interaction_point[key_name] = len(key_interactions)
                    expense_point[key_name] = round(sum((inter.estimated_cost or 0) for inter in key_interactions), 2)
            
            interactions_chart.append(interaction_point)
            expenses_chart.append(expense_point)
        
        # Build agents per key chart data
        agents_per_key = []
        if filtered_keys:
            for idx, key in enumerate(filtered_keys):
                key_name = key.key_name or f"Key {key.id}"
                agent_count = db.query(Agent).filter(
                    Agent.user_id.in_(target_user_ids),
                    Agent.openai_key_id == key.id
                ).count()
                agents_per_key.append({
                    'name': key_name,
                    'value': agent_count,
                    'color': CHART_COLORS[idx % len(CHART_COLORS)]
                })
        
        # Available keys for dropdown
        available_keys = [{'id': k.id, 'name': (k.key_name or f"Key {k.id}")} for k in all_keys]
        
        return DashboardStats(
            total_interactions=total_interactions,
            total_expenses=round(total_expenses, 2),
            total_agents=total_agents,
            active_keys=active_keys,
            interactions_change=round(interactions_change, 1),
            expenses_change=round(expenses_change, 1),
            interactions_chart=interactions_chart,
            expenses_chart=expenses_chart,
            agents_per_key=agents_per_key,
            available_keys=available_keys
        )
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Dashboard stats error: {e}")
        logging.error(traceback.format_exc())
        # Return empty stats instead of crashing
        return DashboardStats(
            total_interactions=0,
            total_expenses=0.0,
            total_agents=0,
            active_keys=0,
            interactions_change=0.0,
            expenses_change=0.0,
            interactions_chart=[],
            expenses_chart=[],
            agents_per_key=[],
            available_keys=[]
        )

