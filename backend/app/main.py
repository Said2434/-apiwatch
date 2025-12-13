"""
APIWatch - FastAPI main application.

This is the entry point for the FastAPI backend server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import Base, async_engine
from app.api import auth, monitors
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Create database tables (in production, use Alembic migrations instead)
        - Initialize background workers (will add later)

    Shutdown:
        - Clean up resources
        - Close database connections
    """
    # Startup
    logger.info("Starting APIWatch backend...")

    # Create database tables (for development)
    # In production, use: alembic upgrade head
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    logger.info("APIWatch backend started successfully!")

    yield  # Application runs

    # Shutdown
    logger.info("Shutting down APIWatch backend...")
    await async_engine.dispose()
    logger.info("APIWatch backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="API Monitoring and Uptime Tracking Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc",  # ReDoc
)

# CORS middleware - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "APIWatch API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns 200 if the API is healthy.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


# API version endpoint
@app.get("/api/v1/info")
async def api_info():
    """Get API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "debug_mode": settings.DEBUG,
        "documentation": "/api/docs"
    }


# Register API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(monitors.router, prefix="/api/v1/monitors", tags=["Monitors"])
# app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])  # Will add later

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG  # Auto-reload in debug mode
    )
