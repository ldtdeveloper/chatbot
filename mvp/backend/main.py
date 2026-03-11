"""
Main FastAPI application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.database import engine, Base
from app.routes import whatsapp_dashboard
from app.routes import human_agent_auth
from fastapi.staticfiles import StaticFiles
from app.routes import auth, service_account,agents, assistant_config, widget, users, dashboard, reports, integration_config, payments, plans,whatsapp, whatsapp_handoff, human_agents
from app.routes import payment_link
from sqlalchemy import text

# Configure logging for OpenAI requests logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def create_enum_types():
    """Create PostgreSQL enum types if they don't exist"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    if not is_postgres:
        # SQLite doesn't need enum types
        return
    
    try:
        with engine.connect() as conn:
            # Create agenttype enum if it doesn't exist
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE agenttype AS ENUM ('WEB', 'PHONE');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Create noisereductionmode enum if it doesn't exist
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE noisereductionmode AS ENUM ('near_field', 'far_field');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            conn.commit()
    except Exception as e:
        # Enum types may already exist, which is fine
        pass


def migrate_agent_foreign_key():
    """Fix agents table foreign key constraint to reference service_account_key instead of openai_keys"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    if not is_postgres:
        return
    
    try:
        with engine.begin() as conn:  # Use begin() for automatic transaction
            # Check if agents table exists
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'agents'
                )
            """)
            result = conn.execute(check_table)
            if not result.scalar():
                return  # Table doesn't exist yet, will be created with correct constraint
            
            # Check what the current constraint references
            check_constraint = text("""
                SELECT 
                    tc.constraint_name,
                    ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_name = 'agents' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'openai_key_id'
            """)
            result = conn.execute(check_constraint)
            constraint_info = result.fetchone()
            
            if constraint_info:
                constraint_name, foreign_table = constraint_info
                if foreign_table == 'openai_keys':
                    # Need to fix the constraint
                    print(f"[Migration] Fixing agents foreign key constraint: {constraint_name}")
                    # Drop old constraint
                    conn.execute(text(f"""
                        ALTER TABLE agents 
                        DROP CONSTRAINT IF EXISTS {constraint_name}
                    """))
                    # Add new constraint
                    conn.execute(text("""
                        ALTER TABLE agents 
                        ADD CONSTRAINT agents_openai_key_id_fkey 
                        FOREIGN KEY (openai_key_id) 
                        REFERENCES service_account_key(id)
                    """))
                    print("[Migration] ✅ Fixed agents foreign key constraint")
                elif foreign_table == 'service_account_key':
                    # Already correct
                    pass
            else:
                # Constraint doesn't exist, add it
                conn.execute(text("""
                    ALTER TABLE agents 
                    ADD CONSTRAINT agents_openai_key_id_fkey 
                    FOREIGN KEY (openai_key_id) 
                    REFERENCES service_account_key(id)
                """))
                print("[Migration] ✅ Added agents foreign key constraint")
    except Exception as e:
        # Don't fail startup if migration fails - log and continue
        print(f"[Migration] ⚠️ Warning: Could not migrate agents foreign key: {e}")


def migrate_interactions_foreign_key():
    """Fix interactions table foreign key constraint to reference service_account_key instead of openai_keys"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    if not is_postgres:
        return
    
    try:
        with engine.begin() as conn:  # Use begin() for automatic transaction
            # Check if interactions table exists
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'interactions'
                )
            """)
            result = conn.execute(check_table)
            if not result.scalar():
                return  # Table doesn't exist yet, will be created with correct constraint
            
            # Check what the current constraint references
            check_constraint = text("""
                SELECT 
                    tc.constraint_name,
                    ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_name = 'interactions' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'openai_key_id'
            """)
            result = conn.execute(check_constraint)
            constraint_info = result.fetchone()
            
            if constraint_info:
                constraint_name, foreign_table = constraint_info
                if foreign_table == 'openai_keys':
                    # Need to fix the constraint
                    print(f"[Migration] Fixing interactions foreign key constraint: {constraint_name}")
                    # Drop old constraint
                    conn.execute(text(f"""
                        ALTER TABLE interactions 
                        DROP CONSTRAINT IF EXISTS {constraint_name}
                    """))
                    # Add new constraint
                    conn.execute(text("""
                        ALTER TABLE interactions 
                        ADD CONSTRAINT interactions_openai_key_id_fkey 
                        FOREIGN KEY (openai_key_id) 
                        REFERENCES service_account_key(id)
                    """))
                    print("[Migration] ✅ Fixed interactions foreign key constraint")
                elif foreign_table == 'service_account_key':
                    # Already correct
                    pass
            else:
                # Constraint doesn't exist, add it
                conn.execute(text("""
                    ALTER TABLE interactions 
                    ADD CONSTRAINT interactions_openai_key_id_fkey 
                    FOREIGN KEY (openai_key_id) 
                    REFERENCES service_account_key(id)
                """))
                print("[Migration] ✅ Added interactions foreign key constraint")
    except Exception as e:
        # Don't fail startup if migration fails - log and continue
        print(f"[Migration] ⚠️ Warning: Could not migrate interactions foreign key: {e}")


def migrate_text_agents_company_id():
    """Add company_id column to text_agents table if it doesn't exist"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    if not is_postgres:
        return
    
    try:
        with engine.begin() as conn:
            # Check if company_id column exists in text_agents table
            check_column = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'text_agents' AND column_name = 'company_id'
                )
            """)
            result = conn.execute(check_column)
            if not result.scalar():
                print("[Migration] Adding company_id column to text_agents")
                conn.execute(text("""
                    ALTER TABLE text_agents 
                    ADD COLUMN company_id INTEGER REFERENCES companies(id)
                """))
                print("[Migration] ✅ Added company_id column to text_agents")
    except Exception as e:
        print(f"[Migration] ⚠️ Warning: Could not add company_id to text_agents: {e}")


# def backfill_text_agents_company_id():
#     \"\"\"Backfill company_id in text_agents from the associated user's company_id\"\"\"
#     db_url = settings.database_url
#     is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
#     
#     if not is_postgres:
#         return
#     
#     try:
#         with engine.begin() as conn:
#             # Check if text_agents table exists
#             check_table = text(\"\"\"
#                 SELECT EXISTS (
#                     SELECT FROM information_schema.tables 
#                     WHERE table_name = 'text_agents'
#                 )
#             \"\"\")
#             result = conn.execute(check_table)
#             if not result.scalar():
#                 return
#                 
#             print(\"[Migration] Backfilling company_id in text_agents\")
#             conn.execute(text(\"\"\"
#                 UPDATE text_agents 
#                 SET company_id = users.company_id 
#                 FROM users 
#                 WHERE text_agents.user_id = users.id 
#                 AND text_agents.company_id IS NULL 
#                 AND users.company_id IS NOT NULL
#             \"\"\"))
#             print(\"[Migration] ✅ Backfilled company_id in text_agents\")
#     except Exception as e:
#         print(f\"[Migration] ⚠️ Warning: Could not backfill company_id in text_agents: {e}\")


# Create enum types before creating tables (required for PostgreSQL)
create_enum_types()

# Create database tables
Base.metadata.create_all(bind=engine)

# Fix foreign key constraints (migrations)
migrate_agent_foreign_key()
migrate_interactions_foreign_key()
migrate_text_agents_company_id()
# backfill_text_agents_company_id()

# Lifespan handler for scheduler startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the report scheduler
    from app.services.scheduler import scheduler
    scheduler.start()
    print("[Main] Report scheduler started")
    
    yield
    
    # Shutdown: Stop the report scheduler
    scheduler.stop()
    print("[Main] Report scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="Voice Assistant Platform API",
    description="Platform for managing OpenAI Realtime API voice assistants",
    version="1.0.0",
    lifespan=lifespan
)



# More permissive CORS for development
# In production, use specific origins
cors_origins = [
        "https://voicequik.com",
        "https://app.voicequik.com",
        "http://localhost:3000",
        "http://localhost:5173", # Standard Vite port
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",  # file:// protocol
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers - CORS middleware will automatically add headers to these responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - CORS middleware will add headers automatically"""
    import traceback
    print(f"[Global Exception Handler] {type(exc).__name__}: {str(exc)}")
    if settings.debug:
        traceback.print_exc()
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc) if settings.debug else "Internal server error"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors - CORS middleware will add headers automatically"""
    print(f"[Validation Error] {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Log HTTPException errors"""
    print(f"[HTTP Exception] {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(service_account.router)
app.include_router(agents.router)
app.include_router(assistant_config.router)  # Now handles multiple assistants
app.include_router(widget.router)
app.include_router(dashboard.router)
app.include_router(whatsapp_dashboard.router)
app.include_router(reports.router)
app.include_router(integration_config.router)
app.include_router(human_agent_auth.router)
app.include_router(payments.router)
app.include_router(payment_link.router)
app.include_router(plans.router)
app.include_router(whatsapp.router)
app.include_router(whatsapp_handoff.router)
app.include_router(human_agents.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/landing", StaticFiles(directory="../landing_site", html=True), name="landing")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Voice Assistant Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

