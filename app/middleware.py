"""Middleware for request tracking and additional functionality."""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track requests with unique IDs and timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with tracking."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started - {request.method} {request.url.path} "
            f"- Request ID: {request_id}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            # Log successful response
            logger.info(
                f"Request completed - {request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Time: {process_time:.3f}s "
                f"- Request ID: {request_id}"
            )

            return response

        except Exception as e:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time

            # Log error
            logger.error(
                f"Request failed - {request.method} {request.url.path} "
                f"- Error: {str(e)} "
                f"- Time: {process_time:.3f}s "
                f"- Request ID: {request_id}",
                exc_info=True,
            )

            # Re-raise the exception to be handled by exception handlers
            raise
