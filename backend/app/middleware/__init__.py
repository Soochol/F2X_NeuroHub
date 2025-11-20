"""
Middleware for F2X NeuroHub MES.

This package contains all FastAPI middleware components.

Usage:
    from app.middleware.error_logging import ErrorLoggingMiddleware
"""

from app.middleware.error_logging import ErrorLoggingMiddleware

__all__ = [
    "ErrorLoggingMiddleware",
]
