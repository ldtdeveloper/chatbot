"""
Main FastAPI application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import engine, Base
from app.routes import auth, openai_keys, agents, assistant_config, widget, users, dashboard, reports, integration_config, payments
from app.routes import payment_link

# Configure logging for OpenAI requests logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create database tables
Base.metadata.create_all(bind=engine)


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
cors_origins = settings.cors_origins.copy() if settings.cors_origins else []
if settings.is_local or settings.is_dev:
    # For development, allow common local origins
    additional_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:5500",  # Live Server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5500",
        "http://localhost",
        "http://127.0.0.1",
        "null",  # file:// protocol
    ]
    cors_origins = list(set(cors_origins + additional_origins))  # Remove duplicates
    print(f"[CORS] Allowed origins: {cors_origins}")

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
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(openai_keys.router)
app.include_router(agents.router)
app.include_router(assistant_config.router)  # Now handles multiple assistants
app.include_router(widget.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(integration_config.router)
app.include_router(payments.router)
app.include_router(payment_link.router)


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

