"""
Migration script to:
1. Ensure all existing users have wallets
2. Deactivate agents for users with zero wallet balance
3. Activate agents for users with positive wallet balance
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.wallet import Wallet
from app.models.agent import Agent

def migrate_wallet_and_keys():
    """Migrate existing accounts: create wallets and sync agent activation status"""
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
        agents_deactivated = 0
        agents_activated = 0
        agents_already_correct = 0
        
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
            
            # Get all agents for this user
            user_agents = db.query(Agent).filter(Agent.user_id == user.id).all()
            wallet_balance = wallet.balance or 0.0
            
            if user_agents:
                for agent in user_agents:
                    if wallet_balance <= 0:
                        # Wallet balance is zero - deactivate agent if it's active
                        if agent.is_active:
                            agent.is_active = False
                            db.commit()
                            agents_deactivated += 1
                            print(f"  ❌ Deactivated agent {agent.id} '{agent.name}' for user {user.username} (wallet balance: ${wallet_balance:.2f})")
                        else:
                            agents_already_correct += 1
                    else:
                        # Wallet balance is positive - activate agent if it's inactive
                        if not agent.is_active:
                            agent.is_active = True
                            db.commit()
                            agents_activated += 1
                            print(f"  ✅ Activated agent {agent.id} '{agent.name}' for user {user.username} (wallet balance: ${wallet_balance:.2f})")
                        else:
                            agents_already_correct += 1
            else:
                print(f"  ℹ️  No agents found for user {user.username} (ID: {user.id})")
        
        # Verify the migration
        print("\n[3/3] Verifying migration...")
        total_wallets = db.query(Wallet).count()
        total_users = db.query(User).filter(User.role != UserRole.SUPERADMIN).count()
        active_agents = db.query(Agent).filter(Agent.is_active == True).count()
        inactive_agents = db.query(Agent).filter(Agent.is_active == False).count()
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print("=" * 60)
        print(f"Total users (non-superadmin): {total_users}")
        print(f"Total wallets: {total_wallets}")
        print(f"Active agents: {active_agents}")
        print(f"Inactive agents: {inactive_agents}")
        print("\nChanges Made:")
        print(f"  - Wallets created: {wallets_created}")
        print(f"  - Agents deactivated: {agents_deactivated}")
        print(f"  - Agents activated: {agents_activated}")
        print(f"  - Agents already correct: {agents_already_correct}")
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
