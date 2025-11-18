"""Error handling middleware and custom exceptions"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import traceback
import logging
from typing import Union

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception for application errors"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: dict = None,
        error_code: str = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.error_code = error_code or "APP_ERROR"
        super().__init__(self.message)


class ValidationException(AppException):
    """Raised when data validation fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            error_code="VALIDATION_ERROR"
        )


class NotFoundException(AppException):
    """Raised when a resource is not found"""
    def __init__(self, resource: str, resource_id: str = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )


class AuthenticationException(AppException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_FAILED"
        )


class AuthorizationException(AppException):
    """Raised when user lacks permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class DatabaseException(AppException):
    """Raised when database operations fail"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="DATABASE_ERROR"
        )


class ExternalServiceException(AppException):
    """Raised when external service calls fail"""
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} service error: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions"""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details,
            "status_code": exc.status_code
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path
        }
    )


async def handle_validation_error(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(x) for x in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        f"Validation error on {request.url.path}",
        extra={"errors": errors, "method": request.method}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": {"errors": errors},
            "path": request.url.path
        }
    )


async def handle_database_error(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    logger.error(
        f"Database error on {request.url.path}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        },
        exc_info=True
    )

    # Check for specific error types
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Database constraint violation",
                "error_code": "CONSTRAINT_VIOLATION",
                "message": "The operation conflicts with existing data",
                "path": request.url.path
            }
        )

    # Generic database error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database operation failed",
            "error_code": "DATABASE_ERROR",
            "message": "An error occurred while accessing the database",
            "path": request.url.path
        }
    )


async def handle_generic_exception(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(
        f"Unexpected error on {request.url.path}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "path": request.url.path
        }
    )
