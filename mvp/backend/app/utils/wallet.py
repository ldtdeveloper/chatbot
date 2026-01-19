"""
Wallet utility functions
"""
from sqlalchemy.orm import Session
from app.models.wallet import Wallet
from app.models.service_account_key import ServiceAccountKey


def get_or_create_wallet(user_id: int, db: Session) -> Wallet:
    """
    Get or create a wallet for a user.
    If wallet doesn't exist, creates one with balance 0.0
    """
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


def add_to_wallet(user_id: int, amount: float, db: Session) -> Wallet:
    """
    Add amount to user's wallet balance.
    Also reactivates service account key if it was deactivated.
    Returns the updated wallet
    """
    wallet = get_or_create_wallet(user_id, db)
    wallet.balance = round((wallet.balance or 0.0) + amount, 6)
    db.commit()
    db.refresh(wallet)
    
    # Reactivate service account key if wallet now has balance
    if wallet.balance > 0:
        service_key = db.query(ServiceAccountKey).filter(
            ServiceAccountKey.user_id == user_id
        ).first()
        if service_key and not service_key.is_active:
            service_key.is_active = True
            db.commit()
            print(f"[Wallet] ✅ Reactivated service account key for user {user_id} (wallet balance: ${wallet.balance:.2f})")
    
    return wallet


def deduct_from_wallet(user_id: int, amount: float, db: Session) -> Wallet:
    """
    Deduct amount from user's wallet balance.
    If insufficient balance, sets balance to 0.
    Also deactivates service account key if balance becomes zero.
    Returns the updated wallet
    """
    wallet = get_or_create_wallet(user_id, db)
    current_balance = wallet.balance or 0.0
    
    if current_balance >= amount:
        wallet.balance = round(current_balance - amount, 6)
    else:
        # Insufficient balance - set to 0
        wallet.balance = 0.0
    
    db.commit()
    db.refresh(wallet)
    
    # Deactivate service account key if balance is now zero
    if wallet.balance <= 0:
        service_key = db.query(ServiceAccountKey).filter(
            ServiceAccountKey.user_id == user_id
        ).first()
        if service_key and service_key.is_active:
            service_key.is_active = False
            db.commit()
            print(f"[Wallet] ❌ Deactivated service account key for user {user_id} (wallet balance: ${wallet.balance:.2f})")
    
    return wallet


def get_wallet_balance(user_id: int, db: Session) -> float:
    """
    Get user's wallet balance. Returns 0.0 if wallet doesn't exist.
    """
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    return wallet.balance if wallet else 0.0
