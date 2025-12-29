"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.payment_token import PaymentToken
from app.models.subscription import Subscription, PaymentStatus
from app.schemas import UserCreate, UserLogin, UserResponse, Token, UserRegisterRequest, SetupPasswordRequest
from app.utils.auth import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user
from datetime import timedelta, datetime, timezone
from app.config import settings
from app.services.email_service import EmailService

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Plan pricing
PLAN_PRICES = {
    "starter": 100.0,
    "pro": 200.0,
    "enterprise": 0.0  # Custom pricing
}


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (legacy - requires password)"""
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user with default role
    hashed_password = get_password_hash(user_data.password) if user_data.password else None
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=UserRole.DEFAULT,
        is_active=bool(user_data.password),  # Active only if password provided
        password_set=bool(user_data.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/register-with-plan")
async def register_with_plan(register_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email and username only, send payment link via email"""
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == register_data.email) | (User.username == register_data.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Validate plan
    if register_data.plan.lower() not in PLAN_PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {list(PLAN_PRICES.keys())}"
        )
    
    plan = register_data.plan.lower()
    amount = PLAN_PRICES[plan]
    
    # Create new user without password (inactive)
    db_user = User(
        email=register_data.email,
        username=register_data.username,
        hashed_password=None,  # No password yet
        role=UserRole.DEFAULT,
        is_active=False,  # Inactive until password is set
        password_set=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate payment token
    payment_token = PaymentToken.generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # Token valid for 7 days
    
    db_token = PaymentToken(
        user_id=db_user.id,
        token=payment_token,
        plan_type=plan,
        amount=amount,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    # Generate payment link
    payment_link = f"{settings.api_base_url}/payment/{payment_token}"
    
    # Send email with payment link
    email_service = EmailService()
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15); max-width: 600px;">
                        <!-- Header with Gradient -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 50px 40px; text-align: center; position: relative; overflow: hidden;">
                                <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(255, 255, 255, 0.1); border-radius: 50%;"></div>
                                <div style="position: absolute; bottom: -30px; left: -30px; width: 150px; height: 150px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
                                <div style="position: relative; z-index: 1;">
                                    <div style="width: 80px; height: 80px; background: rgba(255, 255, 255, 0.2); border-radius: 20px; margin: 0 auto 20px; display: inline-block; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
                                        <div style="color: #ffffff; font-size: 40px; line-height: 80px;">🎙️</div>
                                    </div>
                                    <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">Welcome to VoiceAI!</h1>
                                    <p style="margin: 10px 0 0; color: rgba(255, 255, 255, 0.95); font-size: 16px; font-weight: 400;">Your journey begins here</p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin: 0 0 20px; color: #1a202c; font-size: 18px; font-weight: 500; line-height: 1.6;">
                                    Hello <strong style="color: #667eea; font-weight: 600;">{register_data.username}</strong>,
                                </p>
                                
                                <p style="margin: 0 0 30px; color: #4a5568; font-size: 16px; line-height: 1.8;">
                                    Thank you for registering with <strong style="color: #667eea;">VoiceAI Platform</strong>! We're excited to have you on board. To complete your registration and activate your account, please complete the payment for your selected plan.
                                </p>
                                
                                <!-- Plan Details Card -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #fdf4ff 0%, #f0f9ff 100%); border-radius: 16px; padding: 30px; margin: 30px 0; border: 2px solid rgba(102, 126, 234, 0.1);">
                                    <tr>
                                        <td>
                                            <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 8px 16px; margin-bottom: 20px;">
                                                <span style="color: #ffffff; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Plan Details</span>
                                            </div>
                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="padding: 12px 0; border-bottom: 1px solid rgba(102, 126, 234, 0.1);">
                                                        <span style="color: #718096; font-size: 14px; font-weight: 500;">Plan:</span>
                                                        <span style="color: #1a202c; font-size: 16px; font-weight: 700; float: right; text-transform: uppercase; letter-spacing: 0.5px;">{plan.upper()}</span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 12px 0; border-bottom: 1px solid rgba(102, 126, 234, 0.1);">
                                                        <span style="color: #718096; font-size: 14px; font-weight: 500;">Amount:</span>
                                                        <span style="color: #667eea; font-size: 20px; font-weight: 700; float: right;">${amount:.2f}<span style="font-size: 14px; color: #a0aec0;">/month</span></span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 12px 0; border-bottom: 1px solid rgba(102, 126, 234, 0.1);">
                                                        <span style="color: #718096; font-size: 14px; font-weight: 500;">Username:</span>
                                                        <span style="color: #1a202c; font-size: 16px; font-weight: 600; float: right;">{register_data.username}</span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 12px 0;">
                                                        <span style="color: #718096; font-size: 14px; font-weight: 500;">Email:</span>
                                                        <span style="color: #1a202c; font-size: 16px; font-weight: 600; float: right; word-break: break-all;">{register_data.email}</span>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin: 30px 0 25px; color: #4a5568; font-size: 16px; line-height: 1.8; text-align: center;">
                                    Click the button below to proceed with payment:
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="padding: 10px 0 30px;">
                                            <a href="{payment_link}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 18px 40px; border-radius: 12px; font-size: 16px; font-weight: 600; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); transition: all 0.3s ease; letter-spacing: 0.3px;">
                                                💳 Complete Payment
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Alternative Link -->
                                <div style="background: #f7fafc; border-radius: 12px; padding: 20px; margin: 30px 0; border: 1px solid #e2e8f0;">
                                    <p style="margin: 0 0 12px; color: #718096; font-size: 13px; font-weight: 500; text-align: center;">
                                        Or copy and paste this link into your browser:
                                    </p>
                                    <p style="margin: 0; text-align: center; word-break: break-all;">
                                        <a href="{payment_link}" style="color: #667eea; font-size: 13px; text-decoration: none; font-weight: 500; border-bottom: 1px dashed #667eea; padding-bottom: 2px;">{payment_link}</a>
                                    </p>
                                </div>
                                
                                <!-- Note -->
                                <div style="background: #fff5e6; border-left: 4px solid #f6ad55; border-radius: 8px; padding: 16px 20px; margin: 30px 0;">
                                    <p style="margin: 0; color: #744210; font-size: 13px; line-height: 1.6;">
                                        <strong style="color: #c05621;">⏰ Important:</strong> This payment link will expire in <strong>7 days</strong>. After successful payment, you'll be able to set your password and access your dashboard.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background: #f7fafc; padding: 30px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0 0 10px; color: #718096; font-size: 13px; line-height: 1.6;">
                                    © 2025 VoiceAI Platform. Built with ❤️ by <strong style="color: #667eea;">LDT Technologies</strong>.
                                </p>
                                <p style="margin: 0; color: #a0aec0; font-size: 12px;">
                                    If you didn't register for this account, please ignore this email.
                                </p>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                                    <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Privacy Policy</a>
                                    <span style="color: #cbd5e0;">•</span>
                                    <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Terms of Service</a>
                                    <span style="color: #cbd5e0;">•</span>
                                    <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Support</a>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    try:
        email_service.send_email(
            to_email=register_data.email,
            subject=f"Complete Your VoiceAI Registration - {plan.upper()} Plan",
            html_content=email_html
        )
    except Exception as e:
        print(f"[Register] Failed to send email: {e}")
        # Don't fail registration if email fails, but log it
    
    return {
        "message": "Registration successful. Please check your email for the payment link.",
        "user_id": db_user.id,
        "email_sent": True
    }


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/setup-password", response_model=Token)
async def setup_password_endpoint(
    password_data: SetupPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Set password after successful payment.
    Requires a valid payment token and verified payment status.
    """
    # Find payment token
    db_token = db.query(PaymentToken).filter(
        PaymentToken.token == password_data.token,
        PaymentToken.is_used == False
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired payment token"
        )
    
    # Check if token expired
    if datetime.now(timezone.utc) > db_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment token has expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify payment was successful
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.payment_status == PaymentStatus.SUCCESS
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment not completed. Please complete payment first."
        )
    
    # Check if password already set
    if user.password_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password has already been set. Please login instead."
        )
    
    # Set password
    user.hashed_password = get_password_hash(password_data.password)
    user.password_set = True
    user.is_active = True  # Activate user account
    
    # Mark payment token as used
    db_token.is_used = True
    db_token.used_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
    # Generate access token for auto-login
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Password set successfully"
    }

