"""
FastAPI main application for Bright Ideas backend - New Architecture
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from config import settings
from database import create_tables

# Import API routers
from api import ideas, refinement, plans

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Bright Ideas API (New Architecture)...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bright Ideas API...")


# Create FastAPI application
app = FastAPI(
    title="Bright Ideas API",
    description="AI-powered structured idea refinement and planning tool",
    version="2.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
logger.info(f"CORS origins configured: {settings.cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoints (both with and without API prefix)
@app.get("/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "structured_refinement",
        "environment": settings.environment,
        "cors_origins": settings.cors_origins,
        "features": [
            "ai_question_generation",
            "structured_refinement",
            "plan_generation",
            "plan_export"
        ]
    }

@app.get(f"{settings.api_prefix}/health")
async def health_check_api():
    """API health check endpoint with prefix."""
    return await health_check()


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Welcome to Bright Ideas API - Structured Refinement System",
        "version": "2.0.0",
        "architecture": "AI-powered idea refinement with structured planning",
        "docs": "/docs" if settings.debug else "Contact admin for API documentation",
        "workflow": {
            "1": "Capture idea (/ideas/)",
            "2": "Start refinement session (/refinement/sessions/)", 
            "3": "Answer AI-generated questions (/refinement/sessions/{id}/answers/)",
            "4": "Generate implementation plan (/plans/generate/)",
            "5": "Export plan (/plans/{id}/export/json or /plans/{id}/export/markdown)"
        }
    }


# Include API routers
app.include_router(ideas.router, prefix=settings.api_prefix)
app.include_router(refinement.router, prefix=settings.api_prefix)
app.include_router(plans.router, prefix=settings.api_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )