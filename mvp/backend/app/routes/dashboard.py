"""
Dashboard routes - statistics and analytics endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.service_account_key import ServiceAccountKey
from app.models.agent import Agent
from app.models.interaction import Interaction
from app.schemas.dashboard import DashboardStats
from app.core.dependencies import  require_active_subscription

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


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    days: str = Query(default="30d", regex="^(7d|30d|90d)$"),
    key_id: Optional[int] = Query(default=None, description="Filter by specific API key ID"),
    user_id: Optional[int] = Query(default=None, description="Filter by user ID (superadmin only)"),
    current_user: User = Depends(require_active_subscription),
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
                print(f"this is target user id {target_user_ids}")
            else:
                # Get all user IDs - handle empty result
                all_users = db.query(User).all()
                print(all_users)
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
        all_keys = db.query(ServiceAccountKey).filter(ServiceAccountKey.user_id.in_(target_user_ids)).all()
        
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


@router.get("/expenses-per-user")
async def get_expenses_per_user(
    days: str = Query(default="30d", regex="^(7d|30d|90d|today|this_week|this_month|this_year|till_now|all)$"),
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Get expenses breakdown per user (Superadmin only)
    
    Returns a list of users with their total expenses and interaction counts
    """
    # Check if user is superadmin
    is_superadmin = False
    if hasattr(current_user.role, 'value'):
        is_superadmin = current_user.role.value == UserRole.SUPERADMIN.value
    else:
        is_superadmin = str(current_user.role) == str(UserRole.SUPERADMIN.value) or current_user.role == UserRole.SUPERADMIN
    
    if not is_superadmin:
        raise HTTPException(
            status_code=403,
            detail="Only superadmin can access expenses per user"
        )
    
    try:
        start_date, end_date = get_date_range(days)
        
        # Get all users
        all_users = db.query(User).all()
        
        # Get all interactions in the date range
        interactions = db.query(Interaction).filter(
            Interaction.started_at.isnot(None),
            Interaction.started_at >= start_date,
            Interaction.started_at <= end_date
        ).all()
        
        # Calculate expenses per user
        user_expenses = {}
        for user in all_users:
            user_interactions = [i for i in interactions if i.user_id == user.id]
            total_expenses = sum((i.estimated_cost or 0) for i in user_interactions)
            total_interactions = len(user_interactions)
            
            if total_expenses > 0 or total_interactions > 0:  # Only include users with activity
                user_expenses[user.id] = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'total_expenses': round(total_expenses, 2),
                    'total_interactions': total_interactions
                }
        
        # Convert to list and sort by expenses (descending)
        expenses_list = list(user_expenses.values())
        expenses_list.sort(key=lambda x: x['total_expenses'], reverse=True)
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'users': expenses_list,
            'total_users': len(expenses_list),
            'grand_total_expenses': round(sum(u['total_expenses'] for u in expenses_list), 2)
        }
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Expenses per user error: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching expenses per user: {str(e)}")


@router.post("/expenses-per-user/send-email")
async def send_expenses_report_email(
    days: str = Query(default="30d", regex="^(7d|30d|90d|today|this_week|this_month|this_year|till_now|all)$"),
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Send expenses per user report via email to superadmin (Superadmin only)
    """
    # Check if user is superadmin
    is_superadmin = False
    if hasattr(current_user.role, 'value'):
        is_superadmin = current_user.role.value == UserRole.SUPERADMIN.value
    else:
        is_superadmin = str(current_user.role) == str(UserRole.SUPERADMIN.value) or current_user.role == UserRole.SUPERADMIN
    
    if not is_superadmin:
        raise HTTPException(
            status_code=403,
            detail="Only superadmin can send expenses report"
        )
    
    try:
        start_date, end_date = get_date_range(days)
        
        # Get all users
        all_users = db.query(User).all()
        
        # Get all interactions in the date range
        interactions = db.query(Interaction).filter(
            Interaction.started_at.isnot(None),
            Interaction.started_at >= start_date,
            Interaction.started_at <= end_date
        ).all()
        
        # Calculate expenses per user
        user_expenses = {}
        for user in all_users:
            user_interactions = [i for i in interactions if i.user_id == user.id]
            total_expenses = sum((i.estimated_cost or 0) for i in user_interactions)
            total_interactions = len(user_interactions)
            
            if total_expenses > 0 or total_interactions > 0:
                user_expenses[user.id] = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'total_expenses': round(total_expenses, 2),
                    'total_interactions': total_interactions
                }
        
        # Convert to list and sort by expenses (descending)
        expenses_list = list(user_expenses.values())
        expenses_list.sort(key=lambda x: x['total_expenses'], reverse=True)
        
        # Get period label
        period_labels = {
            'today': 'Today',
            'this_week': 'This Week',
            'this_month': 'This Month',
            'this_year': 'This Year',
            'till_now': 'Till Now',
            'all': 'Till Now',
            '7d': 'Last 7 days',
            '30d': 'Last 30 days',
            '90d': 'Last 90 days'
        }
        period_label = period_labels.get(days, 'Last 30 days')
        
        # Generate HTML email
        from app.services.email_service import EmailService
        email_service = EmailService()
        
        # Build HTML table
        table_rows = ""
        for idx, user_expense in enumerate(expenses_list, 1):
            # Alternate row colors for better readability
            row_bg = "#ffffff" if idx % 2 == 0 else "#fafbfc"
            table_rows += f"""
            <tr style="background:{row_bg};transition:background 0.2s;">
                <td style="padding:14px 16px;text-align:center;font-weight:700;color:#667eea;font-size:13px;border-bottom:1px solid #f1f5f9;">#{idx}</td>
                <td style="padding:14px 16px;font-weight:600;color:#333;font-size:14px;border-bottom:1px solid #f1f5f9;">{user_expense['username']}</td>
                <td style="padding:14px 16px;color:#6b7280;font-size:13px;border-bottom:1px solid #f1f5f9;">{user_expense['email']}</td>
                <td style="padding:14px 16px;text-align:center;color:#333;font-size:14px;font-weight:500;border-bottom:1px solid #f1f5f9;">{user_expense['total_interactions']}</td>
                <td style="padding:14px 16px;text-align:right;font-weight:700;color:#667eea;font-size:14px;border-bottom:1px solid #f1f5f9;">${user_expense['total_expenses']:.2f}</td>
            </tr>
            """
        
        grand_total = sum(u['total_expenses'] for u in expenses_list)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @media only screen and (max-width: 600px) {{
            .email-container {{
                padding: 10px !important;
            }}
            .summary-cards {{
                flex-direction: column !important;
            }}
            .summary-card {{
                min-width: 100% !important;
            }}
            table {{
                font-size: 12px !important;
            }}
            th, td {{
                padding: 8px 6px !important;
            }}
        }}
    </style>
</head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
    <div style="max-width:800px;margin:0 auto;padding:20px;" class="email-container">
        <!-- Header -->
        <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:16px 16px 0 0;padding:30px 25px;text-align:center;box-shadow:0 4px 12px rgba(102,126,234,0.2);">
            <h1 style="margin:0 0 8px 0;color:white;font-size:24px;font-weight:600;letter-spacing:-0.5px;">📊 Per User Expenses Report</h1>
            <p style="margin:0;color:rgba(255,255,255,0.95);font-size:14px;font-weight:400;">Detailed breakdown of expenses by user</p>
            <div style="margin-top:12px;padding:8px 16px;background:rgba(255,255,255,0.15);border-radius:8px;display:inline-block;">
                <span style="color:white;font-size:13px;font-weight:500;">Period: {period_label}</span>
            </div>
        </div>
        
        <!-- Content -->
        <div style="background:white;padding:30px 25px;border-radius:0 0 16px 16px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <!-- Summary Cards -->
            <div style="display:flex;gap:15px;margin-bottom:30px;flex-wrap:wrap;" class="summary-cards">
                <div style="flex:1;min-width:180px;background:#f9fafb;padding:20px;border-radius:12px;border-left:4px solid #667eea;box-shadow:0 2px 6px rgba(0,0,0,0.06);" class="summary-card">
                    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                        <div style="width:40px;height:40px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">👥</div>
                        <div>
                            <p style="margin:0;color:#6b7280;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;font-weight:500;">Total Users</p>
                            <p style="margin:4px 0 0 0;font-size:28px;font-weight:700;color:#333;line-height:1;">{len(expenses_list)}</p>
                        </div>
                    </div>
                </div>
                <div style="flex:1;min-width:180px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:20px;border-radius:12px;box-shadow:0 4px 12px rgba(102,126,234,0.3);color:white;" class="summary-card">
                    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                        <div style="width:40px;height:40px;background:rgba(255,255,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">💰</div>
                        <div>
                            <p style="margin:0;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;font-weight:500;opacity:0.95;">Grand Total</p>
                            <p style="margin:4px 0 0 0;font-size:28px;font-weight:700;line-height:1;">${grand_total:.2f}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- User Breakdown Section -->
            <div style="margin-top:25px;">
                <h3 style="color:#333;font-size:18px;font-weight:600;margin:0 0 20px 0;padding-bottom:12px;border-bottom:2px solid #e5e7eb;">User Breakdown</h3>
                <div style="background:#f9fafb;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">
                    <table style="width:100%;border-collapse:collapse;background:white;">
                        <thead>
                            <tr style="background:linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);">
                                <th style="padding:14px 16px;text-align:left;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Rank</th>
                                <th style="padding:14px 16px;text-align:left;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Username</th>
                                <th style="padding:14px 16px;text-align:left;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Email</th>
                                <th style="padding:14px 16px;text-align:center;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Interactions</th>
                                <th style="padding:14px 16px;text-align:right;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;border-bottom:2px solid #e5e7eb;">Expenses</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows if table_rows else '<tr><td colspan="5" style="padding:40px 20px;text-align:center;color:#6b7280;font-size:14px;">No expenses data available for this period</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="border-top:1px solid #e5e7eb;padding-top:20px;margin-top:30px;text-align:center;">
                <p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.6;">
                    Generated on <strong>{datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M:%S UTC')}</strong>
                </p>
                <p style="margin:8px 0 0 0;color:#cbd5e1;font-size:11px;">
                    Voice Assistant Platform - Expenses Report
                </p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Send email
        subject = f"Per User Expenses Report - {period_label}"
        email_service.send_email(
            to_email=current_user.email,
            subject=subject,
            html_content=html_content
        )
        
        return {
            "message": f"Expenses report sent to {current_user.email}",
            "period": period_label,
            "total_users": len(expenses_list),
            "grand_total": round(grand_total, 2)
        }
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Error sending expenses report: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error sending expenses report: {str(e)}")

