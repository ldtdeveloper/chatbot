"""
Wallet utility functions
"""
from sqlalchemy.orm import Session
from app.models.wallet import Wallet
from app.models.agent import Agent


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
    Also reactivates all user's agents if wallet now has balance.
    Returns the updated wallet
    """
    wallet = get_or_create_wallet(user_id, db)
    wallet.balance = round((wallet.balance or 0.0) + amount, 6)
    db.commit()
    db.refresh(wallet)
    
    # Reactivate all user's agents if wallet now has balance
    if wallet.balance > 0:
        agents = db.query(Agent).filter(Agent.user_id == user_id).all()
        reactivated_count = 0
        for agent in agents:
            if not agent.is_active:
                agent.is_active = True
                reactivated_count += 1
        if reactivated_count > 0:
            db.commit()
            print(f"[Wallet] ✅ Reactivated {reactivated_count} agent(s) for user {user_id} (wallet balance: ${wallet.balance:.2f})")
    
    return wallet


def deduct_from_wallet(user_id: int, amount: float, db: Session) -> Wallet:
    """
    Deduct amount from user's wallet balance.
    If insufficient balance, sets balance to 0.
    Also deactivates all user's agents if balance becomes zero.
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
    
    # Deactivate all user's agents if balance is now zero
    if wallet.balance <= 0:
        agents = db.query(Agent).filter(Agent.user_id == user_id).all()
        deactivated_count = 0
        for agent in agents:
            if agent.is_active:
                agent.is_active = False
                deactivated_count += 1
        if deactivated_count > 0:
            db.commit()
            print(f"[Wallet] ❌ Deactivated {deactivated_count} agent(s) for user {user_id} (wallet balance: ${wallet.balance:.2f})")
    
    return wallet


def get_wallet_balance(user_id: int, db: Session) -> float:
    """
    Get user's wallet balance. Returns 0.0 if wallet doesn't exist.
    """
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    return wallet.balance if wallet else 0.0
