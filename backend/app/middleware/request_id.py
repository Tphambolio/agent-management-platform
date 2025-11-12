"""Request ID middleware for tracking requests across logs"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.logging.json_logger import set_request_id, clear_request_id, get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and track request IDs.

    Features:
    - Generates unique UUID for each request
    - Accepts X-Request-ID header if provided
    - Adds request ID to response headers
    - Sets request ID in logging context
    - Logs request start/end with timing
    """

    async def dispatch(self, request: Request, call_next):
        """Process request with ID tracking"""
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set in logging context
        set_request_id(request_id)

        # Log request start
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query=str(request.url.query) if request.url.query else None,
            client=request.client.host if request.client else None,
        )

        try:
            # Process request
            response: Response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log request completion
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )

            return response

        except Exception as e:
            # Log request error
            logger.exception(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
            )
            raise

        finally:
            # Clear request ID from context
            clear_request_id()
