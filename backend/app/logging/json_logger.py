"""Structured JSON logging with request ID tracking"""
import json
import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
import traceback

# Context variable for request ID tracking
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format for production use.

    Features:
    - Structured JSON output
    - ISO 8601 timestamps
    - Request ID tracking
    - Exception stack traces
    - Additional context fields
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request ID if available
        request_id = request_id_context.get()
        if request_id:
            log_data["request_id"] = request_id

        # Add location information
        log_data["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add any extra fields from the log call
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "taskName"
            ]
        }
        if extra_fields:
            log_data["extra"] = extra_fields

        return json.dumps(log_data)


class HumanReadableFormatter(logging.Formatter):
    """
    Human-readable formatter for development.

    Features:
    - Colored output (if terminal supports it)
    - Readable timestamps
    - Request ID display
    """

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record in human-readable format"""
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        # Build message parts
        parts = [timestamp]

        # Add request ID if available
        request_id = request_id_context.get()
        if request_id:
            parts.append(f"[{request_id[:8]}]")

        # Add level with color
        level = record.levelname
        if self.use_colors:
            color = self.COLORS.get(level, '')
            level = f"{color}{level}{self.RESET}"
        parts.append(f"[{level}]")

        # Add logger name
        parts.append(f"{record.name}:")

        # Add message
        parts.append(record.getMessage())

        message = " ".join(parts)

        # Add exception if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        return message


class StructuredLogger:
    """
    Structured logger wrapper with convenience methods.

    Usage:
        logger = StructuredLogger("my_module")
        logger.info("User logged in", user_id="123", action="login")
        logger.error("Database error", error=str(e), query="SELECT ...")
    """

    def __init__(self, name: str):
        """Initialize structured logger"""
        self.logger = logging.getLogger(name)

    def _log(self, level: int, message: str, **kwargs):
        """Internal log method with extra fields"""
        self.logger.log(level, message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with extra fields"""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with extra fields"""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with extra fields"""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with stack trace"""
        self.logger.exception(message, extra=kwargs)


def setup_logging(
    level: str = "INFO",
    use_json: bool = None,
    include_uvicorn: bool = True
):
    """
    Configure application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Use JSON formatter (auto-detected from env if None)
        include_uvicorn: Include uvicorn access logs
    """
    # Auto-detect JSON mode from environment
    if use_json is None:
        env = os.getenv("ENVIRONMENT", "development").lower()
        use_json = env in ["production", "staging"]

    # Get log level from environment or parameter
    log_level = os.getenv("LOG_LEVEL", level).upper()

    # Create formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = HumanReadableFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure uvicorn loggers
    if include_uvicorn:
        for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
            uvicorn_logger = logging.getLogger(logger_name)
            uvicorn_logger.handlers.clear()
            uvicorn_logger.addHandler(console_handler)
            uvicorn_logger.propagate = False

    # Configure third-party loggers to be less verbose
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

    # Log startup message
    root_logger.info(
        "Logging configured",
        extra={
            "level": log_level,
            "format": "json" if use_json else "human",
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
    )


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


def set_request_id(request_id: str):
    """Set request ID in context for current request"""
    request_id_context.set(request_id)


def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return request_id_context.get()


def clear_request_id():
    """Clear request ID from context"""
    request_id_context.set(None)
