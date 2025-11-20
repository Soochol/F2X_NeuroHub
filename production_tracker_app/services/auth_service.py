"""
JWT Authentication Service with threading support and automatic token refresh.

Features:
- Non-blocking JWT authentication
- Automatic token refresh (25-minute interval, 5 minutes before 30-minute expiration)
- Retry logic for refresh failures (3 attempts)
- Prevents production interruptions from token expiration
"""
from PySide6.QtCore import QObject, Signal, QTimer
from typing import Optional
from .api_client import APIClient
from .workers import APIWorker
import logging

logger = logging.getLogger(__name__)


class AuthService(QObject):
    """Manages JWT authentication lifecycle with non-blocking threading and auto-refresh."""

    login_success = Signal(dict)   # Emit user data on successful login
    auth_error = Signal(str)       # Emit on auth failure
    token_validated = Signal(dict) # Emit user data on token validation
    token_refreshed = Signal()     # Emit when token is auto-refreshed

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.access_token: Optional[str] = None
        self.current_user: Optional[dict] = None
        self._active_workers = []

        # Auto-refresh timer (25 minutes = 1,500,000 ms)
        # Refreshes 5 minutes before 30-minute expiration
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(25 * 60 * 1000)  # 25 minutes in milliseconds
        self._refresh_timer.timeout.connect(self._auto_refresh_token)

        # Retry counter for refresh failures
        self._refresh_retry_count = 0
        self._max_refresh_retries = 3

    def login(self, username: str, password: str):
        """
        Login and store JWT token (non-blocking).
        """
        logger.info(f"Login (threaded) initiated for user: {username}")

        worker = APIWorker(
            api_client=self.api_client,
            operation="login",
            method="POST",
            endpoint="/api/v1/auth/login/json",
            data={"username": username, "password": password}
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def logout(self):
        """Clear authentication state, stop auto-refresh, and cancel active operations."""
        # Stop auto-refresh timer
        if self._refresh_timer.isActive():
            self._refresh_timer.stop()
            logger.info("Auto-refresh timer stopped")

        self.access_token = None
        self.current_user = None
        self.api_client.clear_token()
        self.cancel_all_operations()
        self._refresh_retry_count = 0  # Reset retry counter
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

            # Start auto-refresh timer (25 minutes)
            self._refresh_retry_count = 0  # Reset retry counter
            self._refresh_timer.start()
            logger.info("Auto-refresh timer started (25-minute interval)")

            self.login_success.emit(self.current_user)

        elif operation == "validate_token":
            self.current_user = result
            logger.info("Token validated successfully")
            self.token_validated.emit(result)

        elif operation == "refresh_token":
            # Update access token from refresh response
            self.access_token = result['access_token']
            self.api_client.set_token(self.access_token)
            self._refresh_retry_count = 0  # Reset retry counter on success
            logger.info("Token auto-refreshed successfully")
            self.token_refreshed.emit()

    def _on_api_error(self, operation: str, error_msg: str):
        """Handle API error based on operation type."""
        logger.error(f"Auth error [{operation}]: {error_msg}")

        if operation == "login":
            self.auth_error.emit(f"로그인 실패: {error_msg}")

        elif operation == "validate_token":
            self.auth_error.emit(f"토큰 검증 실패: {error_msg}")

        elif operation == "refresh_token":
            self._refresh_retry_count += 1
            logger.warning(
                f"Token refresh failed (attempt {self._refresh_retry_count}/{self._max_refresh_retries}): "
                f"{error_msg}"
            )

            # Retry if under max retries
            if self._refresh_retry_count < self._max_refresh_retries:
                logger.info(f"Retrying token refresh in 5 seconds...")
                QTimer.singleShot(5000, self._auto_refresh_token)  # Retry after 5 seconds
            else:
                # Max retries exceeded - stop timer and require re-login
                self._refresh_timer.stop()
                logger.error("Token refresh failed after max retries. User must re-login.")
                self.auth_error.emit(
                    "인증이 만료되었습니다. 다시 로그인해주세요.\n"
                    "(자동 갱신 실패)"
                )

    def _cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
        logger.debug(f"Worker cleaned up: {worker.operation}")

    def _auto_refresh_token(self):
        """
        Automatically refresh JWT token (called by QTimer every 25 minutes).

        This method runs in the background to prevent 30-minute token expiration
        from interrupting 24/7 production operations.
        """
        if not self.access_token:
            logger.warning("No access token to refresh. Stopping auto-refresh timer.")
            self._refresh_timer.stop()
            return

        logger.info("Auto-refreshing JWT token...")

        worker = APIWorker(
            api_client=self.api_client,
            operation="refresh_token",
            method="POST",
            endpoint="/api/v1/auth/refresh"
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

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
