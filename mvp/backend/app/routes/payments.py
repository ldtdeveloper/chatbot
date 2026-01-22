"""
Payment routes for Razorpay integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.subscription import Subscription, PaymentStatus
from app.models.plans import Plans
from app.core.dependencies import get_current_user
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.services.service_account import create_service_account
import hmac
import hashlib
from app.schemas.payment import (
    CreateOrderRequest, PaymentOrderResponse, PaymentVerifyResponse, VerifyPaymentRequest,
    WalletTopUpRequest, WalletTopUpOrderResponse, WalletTopUpVerifyRequest, WalletTopUpVerifyResponse
)

# Try to import razorpay - make it optional
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    print("razorpay not avilable")
    RAZORPAY_AVAILABLE = False
    razorpay = None
print(f"razor pay {RAZORPAY_AVAILABLE}")

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Initialize Razorpay client
razorpay_client = None
TEST_MODE = False  # Set to True to enable test mode without real Razorpay

if RAZORPAY_AVAILABLE and settings.razorpay_key_id and settings.razorpay_key_secret:
    try:
        razorpay_client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        print("[Payments] Razorpay client initialized successfully")
    except Exception as e:
        print(f"[Payments] Warning: Failed to initialize Razorpay client: {e}")
        razorpay_client = None
        TEST_MODE = True  # Enable test mode if Razorpay fails
elif settings.is_local or settings.is_dev:
    # Enable test mode in development if Razorpay not configured
    TEST_MODE = True
    print("[Payments] TEST MODE ENABLED - Using mock payment gateway (no real payments)")


@router.post("/create-order-from-token", response_model=PaymentOrderResponse)
async def create_order_from_token(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Create payment order from payment token (for email link)"""
    from app.models.payment_token import PaymentToken
    from datetime import datetime, timezone
    
    token = request_data.get("token")
    user_id = request_data.get("user_id")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )
    
    # Get payment token
    db_token = db.query(PaymentToken).filter(
        PaymentToken.token == token,
        PaymentToken.is_used == False
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired payment token"
        )
    expires_at = db_token.expires_at.replace(tzinfo=timezone.utc)

    # Check expiration
    if datetime.now(timezone.utc) >expires_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Payment token has expired"
        )
    
    # Verify user matches
    if db_token.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not match user"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate plan
    try:
        plan_type = db.get(Plans, db_token.plan_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    # Convert amount to cents
    amount_cents = int(db_token.amount * 100)
    
    # Create subscription record
    subscription = Subscription(
        user_id=user.id,
        plan_type=plan_type.id,
        amount=db_token.amount,
        payment_status=PaymentStatus.PENDING
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Check if Razorpay is not configured
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay payment gateway is not configured. Please add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to your .env file. See RAZORPAY_SETUP_INSTRUCTIONS.md for details."
        )
    
    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': amount_cents,
            'currency': 'USD',
            'receipt': f'sub_{subscription.id}',
            'notes': {
                'user_id': user.id,
                'plan': db_token.plan.name,
                'subscription_id': subscription.id,
                'payment_token': token
            }
        })
        
        subscription.razorpay_order_id = razorpay_order['id']
        db.commit()
        
        return {
            "razorpay_key_id": settings.razorpay_key_id,
            "razorpay_order_id": razorpay_order['id'],
            "amount": amount_cents,
            "currency": "USD",
            "order_id": subscription.id
        }
    
    except Exception as e:
        db.delete(subscription)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}"
        )


@router.post("/create-order", response_model=PaymentOrderResponse)
async def create_order(
    order_data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Razorpay order for payment"""
    # Check if in test mode
    try:
        plan_type = db.query(Plans).filter(Plans.id == order_data.plan_id).first()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    if TEST_MODE and not razorpay_client:
        # Mock payment order for testing
        amount_cents = int(order_data.amount * 100)
        
        subscription = Subscription(
            user_id=current_user.id,
            plan_type=plan_type.id,
            amount=order_data.amount,
            payment_status=PaymentStatus.PENDING
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # Generate mock order ID
        import uuid
        mock_order_id = f"order_test_{uuid.uuid4().hex[:16]}"
        subscription.razorpay_order_id = mock_order_id
        db.commit()
        
        return {
            "razorpay_key_id": "rzp_test_MOCK_KEY",  # Mock key for test mode
            "razorpay_order_id": mock_order_id,
            "amount": amount_cents,
            "currency": "USD",
            "order_id": subscription.id
        }
    
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay payment gateway is not configured. Please add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to your .env file. See QUICK_RAZORPAY_SETUP.md for details."
        )
    
    # Validate user
    if current_user.id != order_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create orders for your own account"
        )
    
    # Convert amount to paise (Razorpay uses smallest currency unit)
    # Note: For USD, we'll use cents (1 USD = 100 cents)
    amount_cents = int(order_data.amount * 100)
    
    # Create subscription record
    subscription = Subscription(
        user_id=current_user.id,
        plan_type=plan_type.id,
        amount=order_data.amount,  # Store in USD
        payment_status=PaymentStatus.PENDING
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': amount_cents,
            'currency': 'USD',
            'receipt': f'sub_{subscription.id}',
            'notes': {
                'user_id': current_user.id,
                'plan': plan_type.name,
                'subscription_id': subscription.id
            }
        })
        
        # Update subscription with Razorpay order ID
        subscription.razorpay_order_id = razorpay_order['id']
        db.commit()
        
        return {
            "razorpay_key_id": settings.razorpay_key_id,
            "razorpay_order_id": razorpay_order['id'],
            "amount": amount_cents,
            "currency": "USD",
            "order_id": subscription.id
        }
    
    except Exception as e:
        # Delete subscription if order creation fails
        db.delete(subscription)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}"
        )
    
@router.post("/verify-from-token", response_model=PaymentVerifyResponse)
async def verify_payment_from_token(
    payment_data: dict,
    db: Session = Depends(get_db)
):
    """Verify payment from payment token (no auth required)"""
    from app.models.payment_token import PaymentToken
    
    token = payment_data.get("token")
    razorpay_order_id = payment_data.get("razorpay_order_id")
    razorpay_payment_id = payment_data.get("razorpay_payment_id")
    razorpay_signature = payment_data.get("razorpay_signature")
    order_id = payment_data.get("order_id")
    
    if not token:
        raise HTTPException(status_code=400, detail="Payment token is required")
    
    db_token = db.query(PaymentToken).filter(
        PaymentToken.token == token,
        PaymentToken.is_used == False
    ).first()
    
    if not db_token:
        raise HTTPException(status_code=404, detail="Invalid or expired payment token")
    
    subscription = db.query(Subscription).filter(
        Subscription.id == order_id,
        Subscription.user_id == db_token.user_id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get user for service account creation
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Test mode handling
    if TEST_MODE and not razorpay_client:
        subscription.razorpay_payment_id = razorpay_payment_id or f"pay_test_{order_id}"
        subscription.razorpay_signature = razorpay_signature or "test_signature"
        subscription.payment_status = PaymentStatus.SUCCESS
        subscription.is_active = True
        subscription.start_date = datetime.now(timezone.utc)
        subscription.end_date = datetime.now(timezone.utc) + timedelta(days=30)
        db.commit()
        
        # === ADD WALLET CREDITS (from plan.wallet_credits for non-superadmin users) ===
        if user.role != UserRole.SUPERADMIN:
            plan = db.query(Plans).filter(Plans.id == db_token.plan_id).first()
            if plan:
                from app.utils.wallet import add_to_wallet
                wallet_credits = plan.wallet_credits
                wallet = add_to_wallet(user.id, wallet_credits, db)
                print(f"===== Added ${wallet_credits:.2f} to wallet for user {user.id} (plan wallet_credits: {plan.wallet_credits}). New balance: ${wallet.balance:.2f} =====")
    else:
        if not razorpay_client:
            raise HTTPException(status_code=503, detail="Razorpay not configured...")
        
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            settings.razorpay_key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            subscription.payment_status = PaymentStatus.FAILED
            db.commit()
            return {"success": False, "message": "Invalid signature"}
        
        subscription.razorpay_payment_id = razorpay_payment_id
        subscription.razorpay_signature = razorpay_signature
        subscription.payment_status = PaymentStatus.SUCCESS
        subscription.is_active = True
        subscription.start_date = datetime.now(timezone.utc)
        subscription.end_date = datetime.now(timezone.utc) + timedelta(days=30)
        db.commit()
    
    # === ADD WALLET CREDITS (from plan.wallet_credits for non-superadmin users) ===
    if user.role != UserRole.SUPERADMIN:
        from app.utils.wallet import add_to_wallet
        plan = db.query(Plans).filter(Plans.id == db_token.plan_id).first()
        if plan:
            wallet_credits = plan.wallet_credits
            wallet = add_to_wallet(user.id, wallet_credits, db)
            print(f"===== Added ${wallet_credits:.2f} to wallet for user {user.id} (plan wallet_credits: {plan.wallet_credits}). New balance: ${wallet.balance:.2f} =====")
    
    # === CALL OpenAI SERVICE ACCOUNT CREATION ===
    print(f"===== Starting OpenAI service account creation for user {user.id} ({user.email}) =====")
    
    try:
        result = create_service_account(name_prefix=f"voiceai-{user.id}",user=user,db=db)
        print("===== OpenAI SERVICE ACCOUNT CREATED SUCCESSFULLY =====")
        print("Result:", result)
        # TODO: Save result to DB as discussed earlier
    except Exception as e:
        print("===== OpenAI ACCOUNT CREATION FAILED =====")
        print("Error details:", str(e))
    
    print("===== DEBUG: Payment flow completed =====")
    
    return {
        "success": True,
        "message": "Payment verified successfully",
        "subscription_id": subscription.id
    }

@router.post("/verify", response_model=PaymentVerifyResponse)
async def verify_payment(
    payment_data: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Razorpay payment signature and update subscription"""
    
    print(f"===== DEBUG: /verify called for user {current_user.id} =====")
    
    subscription = None
    
    # Test mode handling (mock payment)
    if TEST_MODE and not razorpay_client:
        print("===== DEBUG: Running in TEST MODE =====")
        
        subscription = db.query(Subscription).filter(
            Subscription.id == payment_data.order_id,
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        subscription.razorpay_payment_id = payment_data.razorpay_payment_id or f"pay_test_{payment_data.order_id}"
        subscription.razorpay_signature = payment_data.razorpay_signature or "test_signature"
        subscription.payment_status = PaymentStatus.SUCCESS
        subscription.is_active = True
        subscription.start_date = datetime.utcnow()
        subscription.end_date = datetime.utcnow() + timedelta(days=30)
        db.commit()
        
        # === ADD WALLET CREDITS (from plan.wallet_credits for non-superadmin users) ===
        if current_user.role != UserRole.SUPERADMIN:
            from app.utils.wallet import add_to_wallet
            plan = db.query(Plans).filter(Plans.id == subscription.plan_id).first()
            if plan:
                wallet_credits = plan.wallet_credits
                wallet = add_to_wallet(current_user.id, wallet_credits, db)
                print(f"===== Added ${wallet_credits:.2f} to wallet for user {current_user.id} (plan wallet_credits: {plan.wallet_credits}). New balance: ${wallet.balance:.2f} =====")
        
        print("===== DEBUG: TEST MODE - Subscription updated =====")
        
    else:
        # Real Razorpay mode
        print("===== DEBUG: Running in REAL payment mode =====")
        
        if not razorpay_client:
            raise HTTPException(503, "Razorpay not configured...")
        
        subscription = db.query(Subscription).filter(
            Subscription.id == payment_data.order_id,
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(404, "Subscription not found")
        
        message = f"{payment_data.razorpay_order_id}|{payment_data.razorpay_payment_id}"
        generated_signature = hmac.new(
            settings.razorpay_key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != payment_data.razorpay_signature:
            subscription.payment_status = PaymentStatus.FAILED
            db.commit()
            return {"success": False, "message": "Invalid signature"}
        
        subscription.razorpay_payment_id = payment_data.razorpay_payment_id
        subscription.razorpay_signature = payment_data.razorpay_signature
        subscription.payment_status = PaymentStatus.SUCCESS
        subscription.is_active = True
        subscription.start_date = datetime.utcnow()
        subscription.end_date = datetime.utcnow() + timedelta(days=30)
        db.commit()
        
        print("===== DEBUG: REAL payment - Subscription updated =====")
    
    # === ADD WALLET CREDITS (from plan.wallet_credits for non-superadmin users) ===
    if current_user.role != UserRole.SUPERADMIN:
        from app.utils.wallet import add_to_wallet
        # Get the plan from subscription
        plan = db.query(Plans).filter(Plans.id == subscription.plan_id).first()
        if plan:
            wallet_credits = plan.wallet_credits
            wallet = add_to_wallet(current_user.id, wallet_credits, db)
            print(f"===== Added ${wallet_credits:.2f} to wallet for user {current_user.id} (plan wallet_credits: {plan.wallet_credits}). New balance: ${wallet.balance:.2f} =====")
    
    # === NOW CALL OpenAI IN BOTH MODES ===
    print(f"===== Starting OpenAI service account creation for user {current_user.id} =====")
    
    try:
        
        user = db.query(User).filter(User.id == current_user.id).first()
        result = create_service_account(user=user,db=db)
        print("===== OpenAI SERVICE ACCOUNT CREATED SUCCESSFULLY =====")
        print("Result:", result)
        # TODO: Save result['user_api_key'] encrypted in DB
    except Exception as e:
        print("===== OpenAI ACCOUNT CREATION FAILED =====")
        print("Error details:", str(e))
        # Payment is already done - don't crash
    
    print("===== DEBUG: Payment flow completed =====")
    
    return {
        "success": True,
        "message": "Payment verified successfully" + (" (TEST MODE)" if TEST_MODE else ""),
        "subscription_id": subscription.id
    }


@router.post("/wallet-topup/create-order", response_model=WalletTopUpOrderResponse)
async def create_wallet_topup_order(
    topup_data: WalletTopUpRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Razorpay order for wallet top-up"""
    from app.models.user import UserRole
    from app.models.wallet_transaction import WalletTransaction, TransactionStatus
    
    # Only allow non-superadmin users
    if current_user.role == UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin users cannot add money to wallet"
        )
    
    # Validate amount
    if topup_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )
    
    if topup_data.amount < 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum amount is $1.00"
        )
    
    # Create wallet transaction record
    transaction = WalletTransaction(
        user_id=current_user.id,
        amount=topup_data.amount,
        status=TransactionStatus.PENDING
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Convert amount to cents
    amount_cents = int(topup_data.amount * 100)
    
    if TEST_MODE and not razorpay_client:
        # Mock payment order for testing
        import uuid
        mock_order_id = f"order_wallet_{uuid.uuid4().hex[:16]}"
        transaction.razorpay_order_id = mock_order_id
        db.commit()
        
        return {
            "razorpay_key_id": "rzp_test_MOCK_KEY",
            "razorpay_order_id": mock_order_id,
            "amount": amount_cents,
            "currency": "USD",
            "transaction_id": transaction.id
        }
    
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay payment gateway is not configured"
        )
    
    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': amount_cents,
            'currency': 'USD',
            'receipt': f'wallet_{transaction.id}',
            'notes': {
                'user_id': current_user.id,
                'transaction_id': transaction.id,
                'type': 'wallet_topup'
            }
        })
        
        transaction.razorpay_order_id = razorpay_order['id']
        db.commit()
        
        return {
            "razorpay_key_id": settings.razorpay_key_id,
            "razorpay_order_id": razorpay_order['id'],
            "amount": amount_cents,
            "currency": "USD",
            "transaction_id": transaction.id
        }
    except Exception as e:
        db.delete(transaction)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}"
        )


@router.post("/wallet-topup/verify", response_model=WalletTopUpVerifyResponse)
async def verify_wallet_topup(
    verify_data: WalletTopUpVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Razorpay payment for wallet top-up and add money to wallet"""
    from app.models.wallet_transaction import WalletTransaction, TransactionStatus
    from app.utils.wallet import add_to_wallet
    from app.models.wallet import Wallet
    
    # Get transaction
    transaction = db.query(WalletTransaction).filter(
        WalletTransaction.id == verify_data.transaction_id,
        WalletTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status == TransactionStatus.SUCCESS:
        # Already processed
        wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
        return {
            "success": True,
            "message": "Transaction already processed",
            "new_balance": wallet.balance if wallet else 0.0,
            "transaction_id": transaction.id
        }
    
    # Test mode handling
    if TEST_MODE and not razorpay_client:
        transaction.razorpay_payment_id = verify_data.razorpay_payment_id or f"pay_wallet_test_{transaction.id}"
        transaction.razorpay_signature = verify_data.razorpay_signature or "test_signature"
        transaction.status = TransactionStatus.SUCCESS
        db.commit()
        
        # Add money to wallet (updates existing wallet)
        from app.models.wallet import Wallet
        old_wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
        old_balance = old_wallet.balance if old_wallet else 0.0
        
        wallet = add_to_wallet(current_user.id, transaction.amount, db)
        
        print(f"[Wallet Top-up] ✅ TEST MODE - User {current_user.id}: Added ${transaction.amount:.2f} to wallet. Old balance: ${old_balance:.2f}, New balance: ${wallet.balance:.2f}")
        
        return {
            "success": True,
            "message": "Wallet top-up successful (TEST MODE)",
            "new_balance": round(wallet.balance, 2),
            "transaction_id": transaction.id
        }
    
    # Real Razorpay verification
    if not razorpay_client:
        raise HTTPException(status_code=503, detail="Razorpay not configured")
    
    # Verify signature
    message = f"{verify_data.razorpay_order_id}|{verify_data.razorpay_payment_id}"
    generated_signature = hmac.new(
        settings.razorpay_key_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if generated_signature != verify_data.razorpay_signature:
        transaction.status = TransactionStatus.FAILED
        db.commit()
        return {
            "success": False,
            "message": "Invalid payment signature"
        }
    
    # Update transaction
    transaction.razorpay_payment_id = verify_data.razorpay_payment_id
    transaction.razorpay_signature = verify_data.razorpay_signature
    transaction.status = TransactionStatus.SUCCESS
    db.commit()
    
    # Add money to wallet (updates existing wallet, not creates new)
    from app.models.wallet import Wallet
    old_wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    old_balance = old_wallet.balance if old_wallet else 0.0
    
    wallet = add_to_wallet(current_user.id, transaction.amount, db)
    
    print(f"[Wallet Top-up] ✅ User {current_user.id}: Added ${transaction.amount:.2f} to wallet. Old balance: ${old_balance:.2f}, New balance: ${wallet.balance:.2f}")
    
    # Verify wallet was updated
    db.refresh(wallet)
    if wallet.balance != round(old_balance + transaction.amount, 6):
        print(f"[Wallet Top-up] ⚠️ WARNING: Wallet balance mismatch! Expected: ${round(old_balance + transaction.amount, 6):.2f}, Actual: ${wallet.balance:.2f}")
    
    return {
        "success": True,
        "message": "Wallet top-up successful",
        "new_balance": round(wallet.balance, 2),
        "transaction_id": transaction.id
    }