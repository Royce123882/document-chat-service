"""
Logging utility for the application.

Provides a centralized logging configuration with structured logging,
proper formatting, and consistent behavior across all modules.
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color-coded log levels for better readability"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record):
        """Format log record with colors"""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"

        # Format the message
        formatted = super().format(record)

        # Reset levelname for subsequent formatters
        record.levelname = levelname

        return formatted


def setup_logging(
    level: str = "INFO",
    log_format: Optional[str] = None,
    use_colors: bool = True,
    log_file: Optional[str] = None
) -> None:
    """
    Configure application-wide logging settings.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string. If None, uses default format.
        use_colors: Whether to use colored output for console logging
        log_file: Optional file path to write logs to
    """
    # Default format with timestamp, name, level, and message
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if use_colors and sys.stdout.isatty():
        console_formatter = ColoredFormatter(log_format)
    else:
        console_formatter = logging.Formatter(log_format)

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set root logger level
    root_logger.setLevel(numeric_level)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Application started")
    """
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, path: str, status_code: Optional[int] = None):
    """
    Log HTTP request information.

    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: Optional HTTP status code
    """
    if status_code:
        logger.info(f"{method} {path} - {status_code}")
    else:
        logger.info(f"{method} {path}")


def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None):
    """
    Log error with context and stack trace.

    Args:
        logger: Logger instance
        error: Exception object
        context: Optional context description
    """
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=True)
    else:
        logger.error(f"Error: {str(error)}", exc_info=True)


def log_service_call(
    logger: logging.Logger,
    service: str,
    operation: str,
    status: str = "started",
    details: Optional[dict] = None
):
    """
    Log service operation calls with structured information.

    Args:
        logger: Logger instance
        service: Service name
        operation: Operation being performed
        status: Operation status (started, completed, failed)
        details: Optional dictionary of additional details
    """
    msg = f"{service}.{operation} - {status}"
    if details:
        detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
        msg = f"{msg} ({detail_str})"

    if status == "failed":
        logger.error(msg)
    elif status == "completed":
        logger.info(msg)
    else:
        logger.debug(msg)
