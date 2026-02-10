from app.core.database import SessionLocal
from app.models.subscription import Subscription
from app.models.user import User

db = SessionLocal()
user_id = 59

subs = db.query(Subscription).filter(
    Subscription.user_id == user_id
).order_by(Subscription.created_at.desc()).all()

print(f"--- Subscriptions for User {user_id} ---")
for sub in subs:
    print(f"ID: {sub.id}, Mode: '{sub.subscription_mode}', Active: {sub.is_active}, Plan: {sub.plan_type}, Status: {sub.payment_status}, Created: {sub.created_at}")
