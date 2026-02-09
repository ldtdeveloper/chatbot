from app.models.subscription import Subscription,PaymentStatus
from app.models.plans import Plans
from sqlalchemy.orm import Session


def get_subscription_type(user, db: Session):
    '''Get subscription type of current user'''

    # Verify payment was successful
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user,
        Subscription.payment_status == PaymentStatus.SUCCESS,
        Subscription.is_active   
        ).first()
    
    return subscription.subscription_mode

    
        