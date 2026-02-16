"""
Dashboard routes - statistics and analytics endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.usage import UserMinuteBalance
from app.models.service_account_key import ServiceAccountKey
from app.core.dependencies import get_current_user
from app.models.agent import Agent
from app.models.interaction import Interaction
from app.schemas.dashboard import DashboardStats
from app.core.dependencies import  require_active_subscription
from app.utils.date_range import get_date_range,get_previous_period_range
from app.utils.email_html import expense_report_html
from app.tasks.email_task import send_email_task

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Colors for charts (matching frontend)
CHART_COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    days: str = Query(default="30d", regex="^(7d|30d|90d)$"),
    key_id: Optional[int] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    try:
    
        usage = db.query(UserMinuteBalance).filter_by(
            user_id=current_user.id
        ).first()

        total_minutes = 0
        used_minutes = 0
        remaining_minutes = 0

        if usage:
            total_minutes = round(
                usage.used_seconds / 60
                if hasattr(usage, "total_seconds") and usage.total_seconds is not None
                else usage.total_minutes or 0
            )

            used_minutes = round(
                usage.used_seconds / 60
                if hasattr(usage, "used_seconds") and usage.used_seconds is not None
                else usage.used_minutes or 0
            )

            remaining_minutes = round(
                usage.remaining_seconds / 60
                if hasattr(usage, "remaining_seconds") and usage.remaining_seconds is not None
                else usage.remaining_minutes or 0
            )

     
        is_superadmin = False
        if hasattr(current_user.role, "value"):
            is_superadmin = current_user.role.value == UserRole.SUPERADMIN.value
        else:
            is_superadmin = current_user.role == UserRole.SUPERADMIN

  
        if is_superadmin:
            if user_id:
                target_user_ids = [user_id]
            else:
                target_user_ids = [u.id for u in db.query(User).all()]
        else:
            target_user_ids = [current_user.id]

        if not target_user_ids:
            return DashboardStats(
                total_interactions=0,
                total_expenses=0.0,
                total_minutes=total_minutes,
                total_agents=0,
                active_keys=0,
                total_charging=None,
                profit=None,
                charging_change=None,
                interactions_change=0.0,
                expenses_change=0.0,
                interactions_chart=[],
                expenses_chart=[],
                agents_per_key=[],
                available_keys=[]
            )

        all_keys = db.query(ServiceAccountKey).filter(
            ServiceAccountKey.user_id.in_(target_user_ids)
        ).all()

        filtered_keys = (
            [k for k in all_keys if k.id == key_id]
            if key_id else all_keys
        )

        key_ids = [k.id for k in filtered_keys]
        active_keys = len([k for k in filtered_keys if k.is_active])

        agents_query = db.query(Agent).filter(
            Agent.user_id.in_(target_user_ids),
            Agent.is_active == True
        )

        if key_ids:
            agents_query = agents_query.filter(
                Agent.openai_key_id.in_(key_ids)
            )

        total_agents = agents_query.count()

        agents_per_key = [
            {
                "name": key.key_name or f"Key {key.id}",
                "value": db.query(Agent).filter(
                    Agent.user_id.in_(target_user_ids),
                    Agent.openai_key_id == key.id,
                    Agent.is_active == True
                ).count(),
                "color": CHART_COLORS[idx % len(CHART_COLORS)]
            }
            for idx, key in enumerate(filtered_keys)
        ] if filtered_keys else []


        available_keys = [
            {"id": k.id, "name": k.key_name or f"Key {k.id}"}
            for k in all_keys
        ]

        total_interactions = 0
        total_expenses = 0.0
        interactions_change = 0.0
        expenses_change = 0.0

        return DashboardStats(
            total_interactions=total_interactions,
            total_expenses=round(total_expenses, 2),
            total_minutes=total_minutes,
            total_agents=total_agents,
            total_minutes = used_minutes,
            active_keys=active_keys,
            total_charging=None,
            profit=None,
            charging_change=None,
            interactions_change=round(interactions_change, 1),
            expenses_change=round(expenses_change, 1),
            interactions_chart=[],
            expenses_chart=[],
            agents_per_key=agents_per_key,
            available_keys=available_keys
        )

    except Exception as e:
        import logging, traceback
        logging.error(f"Dashboard stats error: {e}")
        logging.error(traceback.format_exc())

        return DashboardStats(
            total_interactions=0,
            total_expenses=0.0,
            total_minutes=total_minutes,
            total_agents=0,
            active_keys=0,
            total_charging=None,
            profit=None,
            charging_change=None,
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
            total_expenses = sum((i.total_cost or 0) for i in user_interactions)
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
        
        response= {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'users': expenses_list,
            'total_users': len(expenses_list),
            'grand_total_expenses': round(sum(u['total_expenses'] for u in expenses_list), 2)
        }
        return response
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
            total_expenses = sum((i.total_cost or 0) for i in user_interactions)
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
        
        html_content = expense_report_html(period_label=period_label,expenses_list=expenses_list,table_rows=table_rows,grand_total=grand_total)
        
        # Send email
        subject = f"Per User Expenses Report - {period_label}"
        send_email_task.delay(current_user.email,subject,html_content) 
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

