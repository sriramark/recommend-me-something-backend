"""Custom exceptions and error handlers for the application."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RecommendationError(Exception):
    """Base exception for recommendation-related errors."""

    pass


class ExternalAPIError(RecommendationError):
    """Exception raised when external API calls fail."""

    def __init__(self, service: str, message: str):
        self.service = service
        self.message = message
        super().__init__(f"External API error ({service}): {message}")


class InvalidQueryError(RecommendationError):
    """Exception raised when user query is invalid or cannot be processed."""

    pass


class RateLimitExceededError(RecommendationError):
    """Exception raised when API rate limits are exceeded."""

    pass


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def recommendation_exception_handler(
    request: Request, exc: RecommendationError
) -> JSONResponse:
    """Handler for recommendation-related exceptions."""
    logger.warning(f"Recommendation error: {str(exc)}")

    status_code = 400
    if isinstance(exc, RateLimitExceededError):
        status_code = 429
    elif isinstance(exc, ExternalAPIError):
        status_code = 503

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def http_exception_handler_custom(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Custom HTTP exception handler with consistent error format."""
    # Log the exception
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
