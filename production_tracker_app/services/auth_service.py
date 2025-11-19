"""
JWT Authentication Service with threading support.

Refactored to use single APIWorker instead of multiple specific workers.
"""
from PySide6.QtCore import QObject, Signal
from typing import Optional
from .api_client import APIClient
from .workers import APIWorker
import logging

logger = logging.getLogger(__name__)


class AuthService(QObject):
    """Manages JWT authentication lifecycle with non-blocking threading."""

    login_success = Signal(dict)   # Emit user data on successful login
    auth_error = Signal(str)       # Emit on auth failure
    token_validated = Signal(dict) # Emit user data on token validation

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.access_token: Optional[str] = None
        self.current_user: Optional[dict] = None
        self._active_workers = []

    def login(self, username: str, password: str):
        """
        Login and store JWT token (non-blocking).
        """
        logger.info(f"Login (threaded) initiated for user: {username}")

        worker = APIWorker(
            api_client=self.api_client,
            operation="login",
            method="POST",
            endpoint="/api/v1/auth/login",
            data={"username": username, "password": password}
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def logout(self):
        """Clear authentication state and cancel active operations."""
        self.access_token = None
        self.current_user = None
        self.api_client.clear_token()
        self.cancel_all_operations()
        logger.info("User logged out")

    def validate_token(self):
        """
        Validate current token by calling /me endpoint (non-blocking).
        """
        logger.info("Token validation (threaded) initiated")

        worker = APIWorker(
            api_client=self.api_client,
            operation="validate_token",
            method="GET",
            endpoint="/api/v1/auth/me"
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def get_current_user_id(self) -> str:
        """Get current user ID."""
        if self.current_user:
            return self.current_user.get('username', 'UNKNOWN')
        return 'UNKNOWN'

    def _on_api_success(self, operation: str, result: dict):
        """Handle successful API call based on operation type."""
        if operation == "login":
            self.access_token = result['access_token']
            self.current_user = result.get('user', {})
            self.api_client.set_token(self.access_token)
            logger.info(f"Login successful for user: {self.current_user.get('username')}")
            self.login_success.emit(self.current_user)

        elif operation == "validate_token":
            self.current_user = result
            logger.info("Token validated successfully")
            self.token_validated.emit(result)

    def _on_api_error(self, operation: str, error_msg: str):
        """Handle API error based on operation type."""
        logger.error(f"Auth error [{operation}]: {error_msg}")

        if operation == "login":
            self.auth_error.emit(f"로그인 실패: {error_msg}")
        elif operation == "validate_token":
            self.auth_error.emit(f"토큰 검증 실패: {error_msg}")

    def _cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
        logger.debug(f"Worker cleaned up: {worker.operation}")

    def cancel_all_operations(self):
        """Cancel all active operations and clean up workers."""
        logger.info(f"Cancelling {len(self._active_workers)} active auth workers")
        for worker in self._active_workers[:]:
            if hasattr(worker, 'cancel'):
                worker.cancel()
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)
        self._active_workers.clear()
        logger.info("All auth workers cancelled")
