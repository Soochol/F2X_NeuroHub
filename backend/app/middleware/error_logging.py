"""
Error Logging Middleware for F2X NeuroHub MES.

This middleware automatically captures all 4xx and 5xx HTTP errors and logs them
to the error_logs table for monitoring, debugging, and analytics purposes.

The middleware integrates with the custom exception system, extracting trace_id
and error details from StandardErrorResponse to correlate frontend-backend errors.
"""

import json
import logging
from typing import Callable
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.database import SessionLocal
from app.crud import error_log as error_log_crud
from app.schemas.error_log import ErrorLogCreate

# Configure logger
logger = logging.getLogger(__name__)


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API errors to database.

    Captures 4xx and 5xx HTTP responses and stores them in the error_logs table
    with trace_id for frontend-backend correlation. Only logs errors that contain
    a StandardErrorResponse format (error_code, trace_id, message).

    Features:
        - Automatic error logging for all 4xx/5xx responses
        - Trace ID extraction for correlation
        - User tracking (when available from request.state)
        - Non-blocking (errors in logging don't affect API response)
        - Transaction isolation (uses independent database session)

    Usage:
        app.add_middleware(ErrorLoggingMiddleware)
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize the error logging middleware.

        Args:
            app: FastAPI application instance
        """
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request and log errors if response is 4xx or 5xx.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler in chain

        Returns:
            Response from next handler (unchanged)
        """
        # Call next middleware/route handler
        response = await call_next(request)

        # Only log 4xx and 5xx errors
        if response.status_code >= 400:
            await self._log_error(request, response)

        return response

    async def _log_error(self, request: Request, response: Response) -> None:
        """
        Log error details to database.

        Extracts error information from StandardErrorResponse and creates
        an error_logs entry. Handles errors gracefully to avoid affecting
        the API response.

        Args:
            request: FastAPI request object
            response: FastAPI response object with error details
        """
        db = None
        try:
            # Create independent database session
            db = SessionLocal()

            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Replace body iterator for client
            async def new_body_iterator():
                yield body

            response.body_iterator = new_body_iterator()

            # Parse error response
            try:
                error_data = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not a JSON response, skip logging
                logger.debug(
                    f"Skipping error log for non-JSON response: {response.status_code} {request.url.path}"
                )
                return

            # Verify StandardErrorResponse format
            if not all(key in error_data for key in ["error_code", "trace_id", "message"]):
                # Not a StandardErrorResponse, skip logging
                logger.debug(
                    f"Skipping error log for non-standard response: {response.status_code} {request.url.path}"
                )
                return

            # Extract user_id from request state (if authenticated)
            user_id = getattr(request.state, "user_id", None)

            # Parse trace_id
            try:
                trace_id = UUID(error_data["trace_id"])
            except (ValueError, TypeError):
                logger.warning(
                    f"Invalid trace_id format: {error_data.get('trace_id')}"
                )
                return

            # Create error log entry
            error_log_data = ErrorLogCreate(
                trace_id=trace_id,
                error_code=error_data["error_code"],
                message=error_data["message"],
                path=error_data.get("path") or str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                user_id=user_id,
                details=error_data.get("details"),
            )

            # Save to database
            error_log_crud.create(db, error_log_in=error_log_data)

            logger.debug(
                f"Logged error: {error_data['error_code']} - {error_data['message']} "
                f"(trace_id: {trace_id})"
            )

        except Exception as e:
            # Log middleware error but don't affect API response
            logger.error(
                f"Failed to log error to database: {str(e)}",
                exc_info=True
            )

        finally:
            # Always close database session
            if db is not None:
                try:
                    db.close()
                except Exception as e:
                    logger.error(f"Failed to close database session: {str(e)}")
