"""
Migration script to:
1. Add is_active column to agents table
2. Set is_active based on wallet balance for existing agents
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.wallet import Wallet
from app.models.agent import Agent

def migrate_agent_is_active():
    """Add is_active column to agents and sync with wallet balance"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Adding is_active column to agents table")
        print("=" * 60)
        
        if is_postgres:
            # PostgreSQL
            print("\n[1/3] Checking if is_active column exists...")
            check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='agents' AND column_name='is_active'
            """)
            result = db.execute(check_column).fetchone()
            
            if result:
                print("⚠️  Column 'is_active' already exists. Skipping column creation.")
            else:
                print("\n[2/3] Adding is_active column...")
                add_column = text("""
                    ALTER TABLE agents 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE
                """)
                db.execute(add_column)
                db.commit()
                print("✅ Column 'is_active' added successfully")
        else:
            # SQLite
            print("\n[1/3] Checking if is_active column exists...")
            check_column = text("""
                PRAGMA table_info(agents)
            """)
            result = db.execute(check_column).fetchall()
            columns = [row[1] for row in result]
            
            if 'is_active' in columns:
                print("⚠️  Column 'is_active' already exists. Skipping column creation.")
            else:
                print("\n[2/3] Adding is_active column...")
                add_column = text("""
                    ALTER TABLE agents 
                    ADD COLUMN is_active BOOLEAN DEFAULT 1
                """)
                try:
                    db.execute(add_column)
                    db.commit()
                    print("✅ Column 'is_active' added successfully")
                except Exception as e:
                    print(f"❌ Error adding column: {e}")
                    raise
        
        # Sync agent is_active status with wallet balance
        print("\n[3/3] Syncing agent is_active status with wallet balance...")
        agents_updated = 0
        agents_activated = 0
        agents_deactivated = 0
        
        all_agents = db.query(Agent).all()
        for agent in all_agents:
            user = db.query(User).filter(User.id == agent.user_id).first()
            
            # Skip superadmin users - their agents are always active
            if user and user.role == UserRole.SUPERADMIN:
                if not agent.is_active:
                    agent.is_active = True
                    db.commit()
                    agents_activated += 1
                    print(f"  ✅ Activated agent {agent.id} for superadmin user {user.username}")
                continue
            
            # Get wallet balance
            wallet = db.query(Wallet).filter(Wallet.user_id == agent.user_id).first()
            wallet_balance = wallet.balance if wallet else 0.0
            
            # Update agent is_active based on wallet balance
            if wallet_balance <= 0:
                if agent.is_active:
                    agent.is_active = False
                    db.commit()
                    agents_deactivated += 1
                    agents_updated += 1
                    print(f"  ❌ Deactivated agent {agent.id} '{agent.name}' for user {user.username if user else agent.user_id} (wallet balance: ${wallet_balance:.2f})")
            else:
                if not agent.is_active:
                    agent.is_active = True
                    db.commit()
                    agents_activated += 1
                    agents_updated += 1
                    print(f"  ✅ Activated agent {agent.id} '{agent.name}' for user {user.username if user else agent.user_id} (wallet balance: ${wallet_balance:.2f})")
        
        # Verify the migration
        total_agents = db.query(Agent).count()
        active_agents = db.query(Agent).filter(Agent.is_active == True).count()
        inactive_agents = db.query(Agent).filter(Agent.is_active == False).count()
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print("=" * 60)
        print(f"Total agents: {total_agents}")
        print(f"Active agents: {active_agents}")
        print(f"Inactive agents: {inactive_agents}")
        print("\nChanges Made:")
        print(f"  - Agents activated: {agents_activated}")
        print(f"  - Agents deactivated: {agents_deactivated}")
        print(f"  - Total agents updated: {agents_updated}")
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
    migrate_agent_is_active()
