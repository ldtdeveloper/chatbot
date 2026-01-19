"""
Migration script to:
1. Ensure all existing users have wallets
2. Deactivate service account keys for users with zero wallet balance
3. Activate service account keys for users with positive wallet balance
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.wallet import Wallet
from app.models.service_account_key import ServiceAccountKey

def migrate_wallet_and_keys():
    """Migrate existing accounts: create wallets and sync key activation status"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Wallet and Service Account Key Sync")
        print("=" * 60)
        
        # Get all users
        users = db.query(User).all()
        print(f"\n[1/3] Found {len(users)} users in database")
        
        wallets_created = 0
        keys_deactivated = 0
        keys_activated = 0
        keys_already_correct = 0
        
        print("\n[2/3] Processing users...")
        for user in users:
            # Skip superadmin users
            if user.role == UserRole.SUPERADMIN:
                print(f"  ⏭️  Skipping superadmin user: {user.username} (ID: {user.id})")
                continue
            
            # Get or create wallet
            wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
            if not wallet:
                wallet = Wallet(user_id=user.id, balance=0.0)
                db.add(wallet)
                db.commit()
                db.refresh(wallet)
                wallets_created += 1
                print(f"  ✅ Created wallet for user {user.username} (ID: {user.id})")
            else:
                print(f"  ℹ️  Wallet exists for user {user.username} (ID: {user.id}), balance: ${wallet.balance:.2f}")
            
            # Get service account key for this user
            service_key = db.query(ServiceAccountKey).filter(
                ServiceAccountKey.user_id == user.id
            ).first()
            
            if service_key:
                wallet_balance = wallet.balance or 0.0
                
                if wallet_balance <= 0:
                    # Wallet balance is zero - deactivate key if it's active
                    if service_key.is_active:
                        service_key.is_active = False
                        db.commit()
                        keys_deactivated += 1
                        print(f"  ❌ Deactivated service account key for user {user.username} (wallet balance: ${wallet_balance:.2f})")
                    else:
                        keys_already_correct += 1
                        print(f"  ✓ Service account key already inactive for user {user.username}")
                else:
                    # Wallet balance is positive - activate key if it's inactive
                    if not service_key.is_active:
                        service_key.is_active = True
                        db.commit()
                        keys_activated += 1
                        print(f"  ✅ Activated service account key for user {user.username} (wallet balance: ${wallet_balance:.2f})")
                    else:
                        keys_already_correct += 1
                        print(f"  ✓ Service account key already active for user {user.username}")
            else:
                print(f"  ⚠️  No service account key found for user {user.username} (ID: {user.id})")
        
        # Verify the migration
        print("\n[3/3] Verifying migration...")
        total_wallets = db.query(Wallet).count()
        total_users = db.query(User).filter(User.role != UserRole.SUPERADMIN).count()
        active_keys = db.query(ServiceAccountKey).filter(ServiceAccountKey.is_active == True).count()
        inactive_keys = db.query(ServiceAccountKey).filter(ServiceAccountKey.is_active == False).count()
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print("=" * 60)
        print(f"Total users (non-superadmin): {total_users}")
        print(f"Total wallets: {total_wallets}")
        print(f"Active service account keys: {active_keys}")
        print(f"Inactive service account keys: {inactive_keys}")
        print("\nChanges Made:")
        print(f"  - Wallets created: {wallets_created}")
        print(f"  - Keys deactivated: {keys_deactivated}")
        print(f"  - Keys activated: {keys_activated}")
        print(f"  - Keys already correct: {keys_already_correct}")
        print("=" * 60)
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate_wallet_and_keys()
