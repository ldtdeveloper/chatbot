""" User Minutes Usage utility functions """

from sqlalchemy.orm import Session
from app.models.usage import UserMinuteBalance
from app.models.agent import Agent


def get_or_create_usage_minutes(
    user_id: int,
    db: Session,
    minutes: int = 0,
) -> UserMinuteBalance:
    """
    Get or create minute balance row for a user.
    If it doesn't exist, initialize with provided minutes.
    """
    usage = (
        db.query(UserMinuteBalance)
        .filter(UserMinuteBalance.user_id == user_id)
        .first()
    )

    if not usage:
        usage = UserMinuteBalance(
            user_id=user_id,
            total_minutes=minutes,
            used_minutes=0,
            remaining_minutes=minutes,
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)

    return usage


def add_to_usage_balance(
    user_id: int,
    minutes: int,
    db: Session,
) -> UserMinuteBalance:
    """
    Add minutes to user's balance.
    Reactivates agents if user now has remaining minutes.
    """
    if minutes <= 0:
        raise ValueError("Minutes must be greater than zero")

    usage = get_or_create_usage_minutes(user_id,minutes= minutes,db= db)

    usage.total_minutes += minutes
    usage.remaining_minutes = minutes

    db.commit()
    db.refresh(usage)

    # Reactivate agents if user now has minutes
    if usage.remaining_minutes > 0:
        agents = db.query(Agent).filter(Agent.user_id == user_id).all()
        for agent in agents:
            if not agent.is_active:
                agent.is_active = True
        db.commit()

    return usage


def deduct_from_usage_balance(
    user_id: int,
    minutes: int,
    db: Session,
) -> UserMinuteBalance:
    """
    Deduct minutes from user's balance.
    If remaining minutes become zero, deactivate all user's agents.
    """
    if minutes <= 0:
        raise ValueError("Minutes must be greater than zero")

    usage = get_or_create_usage_minutes(user_id, db)

    current_remaining = usage.remaining_minutes or 0

    if current_remaining >= minutes:
        usage.remaining_minutes -= minutes
        usage.used_minutes += minutes
    else:
        # Deduct whatever is left
        usage.used_minutes += current_remaining
        usage.remaining_minutes = 0

    db.commit()
    db.refresh(usage)

    # Deactivate agents if no minutes left
    if usage.remaining_minutes <= 0:
        agents = db.query(Agent).filter(Agent.user_id == user_id).all()
        for agent in agents:
            if agent.is_active:
                agent.is_active = False
        db.commit()

    return usage


def get_remaining_minutes(user_id: int, db: Session) -> int:
    """
    Get user's remaining minutes.
    Returns 0 if no record exists.
    """
    usage = (
        db.query(UserMinuteBalance)
        .filter(UserMinuteBalance.user_id == user_id)
        .first()
    )

    return usage.remaining_minutes if usage else 0
