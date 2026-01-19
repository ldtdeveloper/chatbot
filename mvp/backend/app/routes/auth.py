"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import case
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.payment_token import PaymentToken
from app.models.plans import Plans
from app.models.subscription import Subscription, PaymentStatus
from app.schemas.auth import  UserLogin, Token, SetupPasswordRequest, ChangePassword,ResetPassword, ForgetPasswordRequest,PreFetchDetails,ChangeEmail, AddToWalletRequest
from app.schemas.user import UserCreate,UserRegisterRequest,UserResponse
from app.utils.auth import verify_password, get_password_hash, create_access_token,decode_access_token
from app.utils.email_html import generate_email_html,generate_email_html_reset_password
from app.core.dependencies import get_current_user
from datetime import timedelta, datetime, timezone
from app.core.config import settings
from app.tasks.email_task import send_email_task

router = APIRouter(prefix="/api/auth", tags=["authentication"])

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
    
    plan = db.query(Plans).filter((Plans.id== register_data.plan_id)).first()

    # Validate plan
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Invalid plan"
        )
    
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
        plan_id=plan.id,
        amount=plan.price,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    # Generate payment link
    payment_link = f"{settings.api_base_url}/payment/{payment_token}"

    email_html = generate_email_html(db_user,payment_link=payment_link,plan=plan,amount = plan.price)
    try:
        send_email_task.delay(register_data.email,f"Complete Your VoiceAI Registration - {plan.name.upper()} Plan",email_html)
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
    print(user)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    # Check if user is superadmin - exempt from subscription requirement
    is_superadmin = user.role == UserRole.SUPERADMIN
    
    # Only check subscription for non-superadmin users
    if not is_superadmin:
        payment_details = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.payment_status== PaymentStatus.SUCCESS).order_by(Subscription.created_at.desc()).first()

        if not payment_details:
            raise HTTPException(status_code = 402, detail = "subscriptions required")
        
        # Compare with timezone-aware datetime
        now = datetime.now(timezone.utc)
        if payment_details.end_date < now:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Subscription Expired")
    
    if not user.password_set :        
        raise HTTPException(status_code = 409, detail = "PASSWORD_NOT_SET")
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    # Check wallet balance for low balance warning (only for non-superadmin users)
    from app.utils.wallet import get_wallet_balance
    low_balance = False
    wallet_balance = None
    if not is_superadmin:
        wallet_balance = get_wallet_balance(user.id, db)
        if wallet_balance <= 2.0:
            low_balance = True
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "low_balance": low_balance,
        "wallet_balance": wallet_balance
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    from app.utils.wallet import get_wallet_balance
    
    # Add wallet balance for non-superadmin users
    wallet_balance = None
    if current_user.role != UserRole.SUPERADMIN:
        wallet_balance = get_wallet_balance(current_user.id, db)
    
    # Create response dict
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "wallet_balance": wallet_balance
    }
    
    return user_dict




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
        PaymentToken.is_used== False
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired payment token"
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

@router.post("/change-password")
async def change_password(password_data: ChangePassword,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Change password and get access token '''
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

@router.post("/reset-password")
async def reset_password(request: ResetPassword,db: Session= Depends(get_db),authorization: str = Header(None) ):
    '''Reset password '''
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        try:
            token = authorization.split(" ")[1]
        except IndexError:
            raise HTTPException(status_code=401, detail="Invalid Authorization header")

        payload = decode_access_token(token)
        user_id = int(payload["sub"])
        user = db.query(User).get(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.hashed_password = get_password_hash(request.new_password)
        db.commit()

        return {"message": "Password reset successful"}
    except Exception as e:
        return {"status": 500, "message": str(e)}

@router.post("/forget-password")
async def forget_password(request: ForgetPasswordRequest,db: Session = Depends(get_db)):
    '''send reset password link to email '''
    db_user = db.query(User).filter(
        (User.email == request.email)).first()

    if not db_user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "Email not registered")
    
    # Generate reset token that expires in 15min
    reset_token = create_access_token(
        data={
            "sub": str(db_user.id)
        },
        expires_delta=timedelta(minutes=15)
    )

    #Reset password link
    reset_password_link = f"{settings.api_base_url}/reset-password?token={reset_token}"

    #Send email
    email_html = generate_email_html_reset_password(db_user,reset_password_link)
    send_email_task.delay(request.email,"Reset your Voice AI password ",email_html)
    return {
        "message": "Reset password link sent to your registered email.Please check your email for the reset password link.",
        "user_id": db_user.id,
    }

@router.post("/change-email")
async def change_email(request: ChangeEmail,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id==current_user.id).first()
        if not db_user:
            raise HTTPException(status_code =404, details = 'User not found')
        
        db_user.email = request.email
        db.commit()
        db.refresh(db_user)
        return {"message": "Email changed successfully"}
    except Exception as e:
        return {"status":"500","message": f"{str(e)}"}

@router.post("/prefetch")
async def prefetch_details(request: PreFetchDetails, db: Session = Depends(get_db)):
    '''Prefetch details of User in order to sent next action
    complete setup with subscription and payment/login/setup password'''

    db_user = db.query(User).filter(User.email == request.email).first()

    if not db_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "User not found")

    # Default response
    response = {
        "next_action": None,
        }

    if db_user.password_set:
        response["next_action"] = "LOGIN"
        return response

    # Validate plan
    if request.plan:
        plan = db.query(Plans).filter(Plans.id == request.plan.id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan"
            )

    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == db_user.id)
        .order_by(
            case((Subscription.payment_status == PaymentStatus.SUCCESS, 0), else_=1),
            Subscription.created_at.desc()
        )
        .first()
    )

    if not subscription or subscription.payment_status == PaymentStatus.PENDING:
        if not request.plan:
            response["next_action"]="CHOOSE_PLAN"
            return response
        payment_token_details = db.query(PaymentToken).filter(PaymentToken.user_id==db_user.id, PaymentToken.plan_type == request.plan,PaymentToken.is_used.is_(False)).order_by(PaymentToken.created_at.desc()).first()
        if payment_token_details and payment_token_details.expires_at>datetime.now(timezone.utc):
            payment_token = payment_token_details.token
        else:
            response["next_action"]="CHOOSE_PLAN"
            return response
        
        # Generate payment link
        payment_link = f"{settings.api_base_url}/payment/{payment_token}"

        # Send email with payment link
        email_html = generate_email_html(db_user,payment_link=payment_link,plan=request.plan,amount = plan.price)
        send_email_task.delay(request.email,f"Complete Your VoiceAI Registration - {plan.upper()} Plan",email_html)
        response["next_action"] = "COMPLETE_PAYMENT"
        return response

    # SUCCESS but password not set
    response["next_action"] = "SET_PASSWORD"
    return response
