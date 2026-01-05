"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import case
from app.database import get_db
from app.models.user import User, UserRole
from app.models.payment_token import PaymentToken
from app.models.subscription import Subscription, PaymentStatus
from app.schemas import UserCreate, UserLogin, UserResponse, Token, UserRegisterRequest, SetupPasswordRequest, ResetPasswordRequest, ForgetPasswordRequest,PreFetchDetails
from app.utils.auth import verify_password, get_password_hash, create_access_token
from app.utils.email_html import generate_email_html
from app.dependencies import get_current_user
from datetime import timedelta, datetime, timezone
from app.config import settings
from app.services.email_service import EmailService
from fastapi.responses import HTMLResponse
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Plan pricing
PLAN_PRICES = {
    "pro": 29.0,
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
    email_html = generate_email_html(db_user,payment_link=payment_link,plan=plan,amount = amount)

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
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    if user.password_set and not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    payment_details = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.payment_status=="SUCCESS")
    if not user.password_set and payment_details:
        token = None
        # Password setup form
        html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Setup Password - VoiceAI Platform</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
                    .container {{ background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 450px; width: 100%; padding: 40px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .header h1 {{ color: #667eea; margin-bottom: 10px; }}
                    .header p {{ color: #666; }}
                    .form-group {{ margin-bottom: 20px; }}
                    .form-group label {{ display: block; margin-bottom: 8px; color: #333; font-weight: 600; }}
                    .form-group input {{ width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.3s; }}
                    .form-group input:focus {{ outline: none; border-color: #667eea; }}
                    .button {{ width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
                    .button:hover {{ transform: translateY(-2px); }}
                    .button:disabled {{ opacity: 0.6; cursor: not-allowed; }}
                    .error {{ color: #ef4444; text-align: center; margin-top: 15px; display: none; }}
                    .success {{ color: #10b981; text-align: center; margin-top: 15px; display: none; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Setup Your Password</h1>
                        <p>Complete your account setup</p>
                    </div>
                    
                    <form id="passwordForm" onsubmit="setupPassword(event)">
                        <div class="form-group">
                            <label>New Password</label>
                            <input type="password" id="password" required minlength="6" placeholder="Enter your password (min 6 characters)">
                        </div>
                        
                        <div class="form-group">
                            <label>Confirm Password</label>
                            <input type="password" id="confirmPassword" required minlength="6" placeholder="Confirm your password">
                        </div>
                        
                        <button type="submit" class="button" id="submitBtn">Set Password</button>
                        
                        <div id="error" class="error"></div>
                        <div id="success" class="success"></div>
                    </form>
                </div>
                
                <script>
                    const API_BASE = '{settings.api_base_url}';
                    const token = '{token}';
                    
                    async function setupPassword(e) {{
                        e.preventDefault();
                        
                        const password = document.getElementById('password').value;
                        const confirmPassword = document.getElementById('confirmPassword').value;
                        const errorDiv = document.getElementById('error');
                        const successDiv = document.getElementById('success');
                        const submitBtn = document.getElementById('submitBtn');
                        
                        // Clear previous messages
                        errorDiv.style.display = 'none';
                        successDiv.style.display = 'none';
                        
                        // Validate passwords match
                        if (password !== confirmPassword) {{
                            errorDiv.textContent = 'Passwords do not match';
                            errorDiv.style.display = 'block';
                            return;
                        }}
                        
                        if (password.length < 6) {{
                            errorDiv.textContent = 'Password must be at least 6 characters';
                            errorDiv.style.display = 'block';
                            return;
                        }}
                        
                        submitBtn.disabled = true;
                        submitBtn.textContent = 'Setting up...';
                        
                        try {{
                            const response = await fetch(`${{API_BASE}}/api/auth/setup-password`, {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{
                                    token: token,
                                    password: password
                                }})
                            }});
                            
                            if (!response.ok) {{
                                const errorData = await response.json();
                                throw new Error(errorData.detail || 'Failed to setup password');
                            }}
                            
                            const data = await response.json();
                            
                            successDiv.textContent = 'Password set successfully! Redirecting to dashboard...';
                            successDiv.style.display = 'block';
                            
                            // Store token for auto-login
                            localStorage.setItem('token', data.access_token);
                            
                            // Redirect to dashboard (adjust URL based on your frontend)
                            setTimeout(() => {{
                                // If frontend is on different port, adjust this
                                window.location.href = 'http://localhost:3000/';
                            }}, 2000);
                            
                        }} catch (err) {{
                            errorDiv.textContent = err.message || 'Failed to setup password';
                            errorDiv.style.display = 'block';
                            submitBtn.disabled = false;
                            submitBtn.textContent = 'Set Password';
                        }}
                    }}
                </script>
            </body>
            </html>
            """

        return HTMLResponse(content=html_content)
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
    now = datetime.now(ZoneInfo("UTC"))
    expires_at = db_token.expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
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

@router.post("/reset-password")
async def reset_password(password_data: ResetPasswordRequest,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Reset password and get access token '''
    password_verification = False

    if password_data.old_password:
        password_verification = verify_password(password_data.old_password,current_user.hashed_password)

    if not password_verification:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = "Incorrect old password")

    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    db.refresh(current_user)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.id},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Reset Password successfully"
    }

@router.post("/forget-password")
def forget_password(request: ForgetPasswordRequest,db: Session = Depends(get_db)):
    '''Forget password and send setup password link to email '''
    db_user = db.query(User).filter(
        (User.email == request.email)).first()

    if not db_user:
        raise HTTPException(status = status.HTTP_404_NOT_FOUND, detail = "Email not registered")

     # Verify payment was successful
    subscription = db.query(Subscription).filter(
        Subscription.user_id == db_user.id,
        Subscription.payment_status == PaymentStatus.SUCCESS
    ).first()
    subscription_plan = db.query(Subscription).filter(Subscription.user_id == db_user.id).order_by(Subscription.created_at.desc()).first()
    if not subscription:
        payment_token = PaymentToken.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # Token valid for 7 days

        db_token = PaymentToken(
            user_id=db_user.id,
            token=payment_token,
            plan_type=subscription_plan.plan_type,
            amount=subscription_plan.amount,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()

        # Generate payment link
        payment_link = f"{settings.api_base_url}/payment/{payment_token}"

        # Send email with payment link
        email_service = EmailService()
        email_html = generate_email_html(db_user,payment_link=payment_link,plan=subscription_plan.plan_type,amount = subscription_plan.amount)
        try:
            email_service.send_email(
                to_email=request.email,
                subject=f"Complete Your VoiceAI Registration - {Subscription.plan_type.upper()} Plan",
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

    return {
        "status" : "200",
        "message" : "Password setup link sent successfully"
    }

@router.post("/change-email")
def change_email(current_user: User = Depends(get_current_user)):
    # To do
    pass

@router.post("/prefetch")
def prefetch_details(request: PreFetchDetails, db: Session = Depends(get_db)):
    '''Prefetch details of User in order to sent next action
    complete setup with subscription and payment/login/setup password'''

    db_user = db.query(User).filter(User.email == request.email).first()

    if not db_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "User not found")

    # Default response
    response = {
        "user_exists": True,
        "password_set": db_user.password_set,
        "subscription": {
            "exists": False,
            "status": None,
            "expired": False
        },
        "next_action": None,
        "message": None
    }

    if db_user.password_set:
        response["next_action"] = "LOGIN"
        response["message"] = "Proceed to login"
        return response

    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == db_user.id)
        .order_by(
            case((Subscription.payment_status == PaymentStatus.SUCCESS, 0), else_=1),
            Subscription.created_at.desc()
        )
        .first()
    )

    # Validate plan
    if request.plan and request.plan.lower() not in PLAN_PRICES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan. Must be one of: {list(PLAN_PRICES.keys())}"
            )

    if request.plan:
        plan = request.plan.lower()
        amount = PLAN_PRICES[plan]

    if not subscription or subscription.payment_status == PaymentStatus.PENDING:
        payment_token_details = db.query(PaymentToken).filter(PaymentToken.user_id==db_user.id, PaymentToken.plan_type == plan,PaymentToken.is_used.is_(False)).order_by(PaymentToken.created_at.desc()).first()
        if payment_token_details and payment_token_details.expires_at>datetime.now(timezone.utc):
            payment_token = payment_token_details.token
        else:
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
        email_html = generate_email_html(db_user,payment_link=payment_link,plan=plan,amount = amount)

        try:
            email_service.send_email(
                to_email=request.email,
                subject=f"Complete Your VoiceAI Registration - {plan.upper()} Plan",
                html_content=email_html
            )
        except Exception as e:
            print(f"[Register] Failed to send email: {e}")
        response["next_action"] = "COMPLETE_PAYMENT"
        response["message"] = "Complete your payment"
        return response

    response["subscription"]["exists"] = True
    response["subscription"]["status"] = subscription.payment_status

    if (subscription.payment_status == PaymentStatus.SUCCESS and subscription.end_date and subscription.end_date > datetime.utcnow()):
        response["subscription"]["expired"] = True
        response["next_action"] = "COMPLETE_PAYMENT"
        response["message"] = "Subscription expired"
        return response

    # SUCCESS but password not set
    response["next_action"] = "SET_PASSWORD"
    response["message"] = "Set your password to continue"
    return response
