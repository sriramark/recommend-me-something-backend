"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import yaml

from app.config import settings
from app.logging_config import setup_logging
from app.middleware import RequestTrackingMiddleware
from app.exceptions import (
    global_exception_handler,
    recommendation_exception_handler,
    http_exception_handler_custom,
    RecommendationError,
)
from app.routers import books, movies


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging("INFO" if not settings.debug else "DEBUG")
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Load CORS configuration
def load_cors_config():
    """Load CORS configuration from config.yml."""
    try:
        with open("config.yml", "r") as f:
            config = yaml.safe_load(f)
            return {
                "allow_origins": config.get("origins", ["*"]),
                "allow_methods": config.get("methods", ["GET"]),
                "allow_credentials": config.get("credentials", True),
            }
    except FileNotFoundError:
        # Fallback to default settings
        return {
            "allow_origins": settings.cors_origins,
            "allow_methods": settings.cors_methods,
            "allow_credentials": settings.cors_allow_credentials,
        }


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A recommendation API for books and movies powered by AI",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Load and apply CORS configuration
cors_config = load_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"],
)

# Add request tracking middleware
app.add_middleware(RequestTrackingMiddleware)

# Register exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RecommendationError, recommendation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler_custom)

# Include routers
app.include_router(books.router)
app.include_router(movies.router)


@app.get("/", tags=["root"])
async def read_root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "API for Recommend Me Something - Get personalized book and movie recommendations",
        "docs_url": "/docs"
        if settings.debug
        else "Documentation disabled in production",
        "endpoints": {"books": "/books", "movies": "/movies"},
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}
