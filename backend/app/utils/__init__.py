"""
Utility modules for the application.

This package contains reusable utility functions and helpers used across
the application:

- logger: Structured logging with color output
- file_parsers: Document parsing (text, PDF)
- document_processing: Text chunking and prompt building
- llm_utils: LLM and embedding model initialization

The most commonly used logging utilities are exported for convenience.
"""

from app.utils.logger import get_logger, log_error, log_request, log_service_call, setup_logging

__all__ = [
    "get_logger",
    "setup_logging",
    "log_error",
    "log_request",
    "log_service_call"
]
