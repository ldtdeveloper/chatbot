"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import auth, openai_keys, prompts, assistant_config, widget

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Voice Assistant Platform API",
    description="Platform for managing OpenAI Realtime API voice assistants",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(openai_keys.router)
app.include_router(prompts.router)
app.include_router(assistant_config.router)
app.include_router(widget.router)


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

