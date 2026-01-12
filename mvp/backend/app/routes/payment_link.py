"""
Payment Link routes - for handling payment via email link
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.payment_token import PaymentToken
from app.models.user import User
from app.models.subscription import Subscription, PaymentStatus
from app.core.config import settings
from app.utils.email_html import payment_page_html,setup_password_page_html

router = APIRouter(prefix="/payment", tags=["payment-link"])

# Templates directory (create if needed)
try:
    templates = Jinja2Templates(directory="templates")
except:
    templates = None

@router.get("/{token}")
async def payment_page(token: str, request: Request, db: Session = Depends(get_db)):
    """Display payment page with Razorpay integration"""
    # Get payment token
    db_token = db.query(PaymentToken).filter(
        PaymentToken.token == token,
        PaymentToken.is_used == False
    ).first()

    if not db_token:
      
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invalid Payment Link</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #ef4444; }
            </style>
        </head>
        <body>
            <h1 class="error">Invalid or Expired Payment Link</h1>
            <p>This payment link is invalid or has already been used.</p>
            <p>Please contact support if you need assistance.</p>
        </body>
        </html>
        """, status_code=404)
    
    # Check if token expired
    
    expires_at = db_token.expires_at.replace(tzinfo=timezone.utc)  
    if datetime.now(timezone.utc) > expires_at:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Expired Payment Link</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #ef4444; }
            </style>
        </head>
        <body>
            <h1 class="error">Payment Link Expired</h1>
            <p>This payment link has expired. Please request a new payment link.</p>
        </body>
        </html>
        """, status_code=410)
    
    # Get user
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already paid
    active_subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.payment_status == PaymentStatus.SUCCESS,
        Subscription.is_active 
    ).first()
    
    if active_subscription:
        # Already paid, redirect to password setup
        return RedirectResponse(url=f"/setup-password/{token}", status_code=302)
    
    # Generate payment page HTML
    plan_name = db_token.plan_type.upper()
    amount_cents = int(db_token.amount * 100)
    
    html_content = payment_page_html(user=user,plan_name=plan_name,settings=settings,db_token=db_token,token=token, amount_cents=amount_cents)
    return HTMLResponse(content=html_content)

@router.get("/setup-password/{token}")
async def setup_password_page(token: str, request: Request, db: Session = Depends(get_db)):
    """Display password setup page"""
    # Verify token and check payment status
    db_token = db.query(PaymentToken).filter(PaymentToken.token == token).first()
    
    if not db_token:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Invalid Link</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #ef4444;">Invalid Link</h1>
            <p>This link is invalid.</p>
        </body>
        </html>
        """, status_code=404)
    
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if payment completed
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.payment_status == PaymentStatus.SUCCESS
    ).first()
    
    if not subscription:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Payment Required</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #ef4444;">Payment Required</h1>
            <p>Please complete payment first.</p>
            <a href="/payment/{}" style="color: #667eea;">Go to Payment</a>
        </body>
        </html>
        """.format(token), status_code=400)
    
    # Check if password already set
    if user.password_set:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Password Already Set</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>Password Already Set</h1>
            <p>Your password has already been set. You can now login.</p>
            <a href="/login" style="color: #667eea;">Go to Login</a>
        </body>
        </html>
        """)
    
    # Password setup form
    html_content = setup_password_page_html(settings=settings,token=token)
    return HTMLResponse(content=html_content)



