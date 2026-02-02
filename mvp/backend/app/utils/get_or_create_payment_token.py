from app.models.payment_token import PaymentToken
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone


def get_or_create_payment_token(
    db: Session,
    *,
    user_id: int,
    plan_id: int,
    amount: float,
    expiry_minutes: int = 30,
) -> str:
    now = datetime.now(timezone.utc)

    token = (
        db.query(PaymentToken)
        .filter(
            PaymentToken.user_id == user_id,
            PaymentToken.plan_id == plan_id,
            PaymentToken.is_used.is_(False),
            PaymentToken.expires_at > now,
        )
        .order_by(PaymentToken.created_at.desc())
        .first()
    )

    if token:
        return token.token

    new_token = PaymentToken(
        user_id=user_id,
        plan_id=plan_id,
        amount=amount,
        token=PaymentToken.generate_token(),
        expires_at=now + timedelta(minutes=expiry_minutes),
    )

    db.add(new_token)
    db.commit()
    return new_token.token
