"""
JWT Authentication Service with threading support.
"""
from PySide6.QtCore import QObject, Signal
from typing import Optional
from .api_client import APIClient
from .workers import LoginWorker, TokenValidationWorker
import logging

logger = logging.getLogger(__name__)


class AuthService(QObject):
    """Manages JWT authentication lifecycle with non-blocking threading."""

    login_success = Signal(dict)  # Emit user data on successful login
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

        Args:
            username: Username
            password: Password

        Emits:
            login_success: On success with user data
            auth_error: On failure with error message
        """
        logger.info(f"Login (threaded) initiated for user: {username}")

        worker = LoginWorker(self.api_client, username, password)
        worker.login_success.connect(self._on_login_success)
        worker.login_failed.connect(self._on_login_failed)
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

        Emits:
            token_validated: On success with user data
            auth_error: On failure with error message
        """
        logger.info("Token validation (threaded) initiated")

        worker = TokenValidationWorker(self.api_client)
        worker.validation_success.connect(self._on_token_validated)
        worker.validation_failed.connect(self._on_validation_failed)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def get_current_user_id(self) -> str:
        """Get current user ID."""
        if self.current_user:
            return self.current_user.get('username', 'UNKNOWN')
        return 'UNKNOWN'

    def _on_login_success(self, response: dict):
        """Handle successful login."""
        self.access_token = response['access_token']
        self.current_user = response.get('user', {})

        # Store token in API client
        self.api_client.set_token(self.access_token)

        logger.info(f"Login successful for user: {self.current_user.get('username')}")
        self.login_success.emit(self.current_user)

    def _on_login_failed(self, error_msg: str):
        """Handle login failure."""
        logger.error(f"Login failed: {error_msg}")
        self.auth_error.emit(f"로그인 실패: {error_msg}")

    def _on_token_validated(self, user: dict):
        """Handle successful token validation."""
        self.current_user = user
        logger.info("Token validated successfully")
        self.token_validated.emit(user)

    def _on_validation_failed(self, error_msg: str):
        """Handle token validation failure."""
        logger.error(f"Token validation failed: {error_msg}")
        self.auth_error.emit(f"토큰 검증 실패: {error_msg}")

    def _cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
        logger.debug(f"Worker cleaned up: {type(worker).__name__}")

    def cancel_all_operations(self):
        """Cancel all active operations and clean up workers."""
        logger.info(f"Cancelling {len(self._active_workers)} active auth workers")
        for worker in self._active_workers[:]:
            if hasattr(worker, 'cancel'):
                worker.cancel()
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)  # Wait up to 1 second
        self._active_workers.clear()
        logger.info("All auth workers cancelled")
