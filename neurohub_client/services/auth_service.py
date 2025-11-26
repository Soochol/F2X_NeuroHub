"""
JWT Authentication Service with threading support and automatic token refresh.

Features:
- Non-blocking JWT authentication
- Automatic token refresh (25-minute interval, 5 minutes before 30-minute expiration)
- Automatic re-login on refresh failure (for 24/7 production environments)
- Credentials stored in memory for seamless re-authentication
"""
import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, QTimer, Signal

from .api_client import APIClient
from .workers import APIWorker

logger = logging.getLogger(__name__)


class AuthService(QObject):
    """Manages JWT authentication lifecycle with non-blocking threading and auto-refresh."""

    login_success = Signal(dict)   # Emit user data on successful login
    auth_error = Signal(str)       # Emit on auth failure
    token_validated = Signal(dict) # Emit user data on token validation
    token_refreshed = Signal()     # Emit when token is auto-refreshed
    auto_relogin_success = Signal()  # Emit when auto re-login succeeds

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.access_token: Optional[str] = None
        self.current_user: Optional[Dict[str, Any]] = None
        self._active_workers: List[APIWorker] = []

        # Stored credentials for auto re-login (PySide app only, local use)
        self._saved_username: Optional[str] = None
        self._saved_password: Optional[str] = None

        # Auto-refresh timer (12 hours = 43,200,000 ms)
        # Refreshes halfway through 24-hour token expiration
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(12 * 60 * 60 * 1000)  # 12 hours in milliseconds
        self._refresh_timer.timeout.connect(self._auto_refresh_token)

        # Retry counter for refresh/re-login failures
        self._refresh_retry_count = 0
        self._max_refresh_retries = 3
        self._relogin_in_progress = False

    def login(self, username: str, password: str):
        """
        Login and store JWT token (non-blocking).

        Credentials are saved in memory for automatic re-login on token expiry.
        """
        logger.info(f"Login (threaded) initiated for user: {username}")

        # Save credentials for auto re-login (memory only, not persisted)
        self._saved_username = username
        self._saved_password = password

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

        # Clear saved credentials
        self._saved_username = None
        self._saved_password = None
        self._refresh_retry_count = 0
        self._relogin_in_progress = False

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
        """Get current user's full name for worker identification."""
        if self.current_user:
            # Use full_name for worker identification (e.g., "홍길동")
            # Falls back to username if full_name is not available
            return self.current_user.get('full_name') or self.current_user.get('username', 'UNKNOWN')
        return 'UNKNOWN'

    def get_current_username(self) -> str:
        """Get current user's username (login ID)."""
        if self.current_user:
            return self.current_user.get('username', 'UNKNOWN')
        return 'UNKNOWN'

    def _on_api_success(self, operation: str, result: Dict[str, Any]) -> None:
        """Handle successful API call based on operation type."""
        if operation == "login":
            self.access_token = result['access_token']
            self.current_user = result.get('user') or {}
            if self.access_token:
                self.api_client.set_token(self.access_token)
            logger.info(
                f"Login successful for user: {self.current_user.get('username')}"
            )

            # Start auto-refresh timer (25 minutes)
            self._refresh_retry_count = 0
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
            if self.access_token:
                self.api_client.set_token(self.access_token)
            self._refresh_retry_count = 0
            logger.info("Token auto-refreshed successfully")
            self.token_refreshed.emit()

        elif operation == "auto_relogin":
            # Auto re-login successful - restore session silently
            self.access_token = result['access_token']
            self.current_user = result.get('user') or {}
            if self.access_token:
                self.api_client.set_token(self.access_token)
            self._refresh_retry_count = 0
            self._relogin_in_progress = False
            self._refresh_timer.start()
            logger.info(
                f"Auto re-login successful for user: "
                f"{self.current_user.get('username')}"
            )
            self.auto_relogin_success.emit()

    def _on_api_error(self, operation: str, error_msg: str) -> None:
        """Handle API error based on operation type."""
        logger.error(f"Auth error [{operation}]: {error_msg}")

        if operation == "login":
            self.auth_error.emit(f"로그인 실패: {error_msg}")

        elif operation == "validate_token":
            self.auth_error.emit(f"토큰 검증 실패: {error_msg}")

        elif operation == "refresh_token":
            self._refresh_retry_count += 1
            logger.warning(
                f"Token refresh failed "
                f"(attempt {self._refresh_retry_count}/{self._max_refresh_retries}): "
                f"{error_msg}"
            )

            # Retry refresh if under max retries
            if self._refresh_retry_count < self._max_refresh_retries:
                logger.info("Retrying token refresh in 5 seconds...")
                QTimer.singleShot(5000, self._auto_refresh_token)
            else:
                # Refresh failed - try auto re-login with saved credentials
                logger.warning(
                    "Token refresh failed after max retries. "
                    "Attempting auto re-login..."
                )
                self._attempt_auto_relogin()

        elif operation == "auto_relogin":
            # Auto re-login also failed - now we must ask user to re-login
            self._relogin_in_progress = False
            self._refresh_timer.stop()
            logger.error(
                "Auto re-login failed. User must manually re-login."
            )
            self.auth_error.emit(
                "인증이 만료되었습니다. 다시 로그인해주세요.\n"
                "(자동 재인증 실패)"
            )

    def _cleanup_worker(self, worker: APIWorker) -> None:
        """Clean up finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
        logger.debug(f"Worker cleaned up: {worker.operation}")

    def _auto_refresh_token(self) -> None:
        """
        Automatically refresh JWT token (called by QTimer every 25 minutes).

        This method runs in the background to prevent 30-minute token expiration
        from interrupting 24/7 production operations.
        """
        if not self.access_token:
            logger.warning(
                "No access token to refresh. Stopping auto-refresh timer."
            )
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

    def _attempt_auto_relogin(self) -> None:
        """
        Attempt automatic re-login using saved credentials.

        Called when token refresh fails after max retries.
        This ensures 24/7 production operations continue without interruption.
        """
        # Prevent multiple concurrent re-login attempts
        if self._relogin_in_progress:
            logger.warning("Auto re-login already in progress, skipping...")
            return

        # Check if credentials are available
        if not self._saved_username or not self._saved_password:
            logger.error(
                "No saved credentials for auto re-login. "
                "User must manually re-login."
            )
            self._refresh_timer.stop()
            self.auth_error.emit(
                "인증이 만료되었습니다. 다시 로그인해주세요.\n"
                "(저장된 인증정보 없음)"
            )
            return

        self._relogin_in_progress = True
        self._refresh_retry_count = 0  # Reset for re-login attempts
        logger.info(
            f"Attempting auto re-login for user: {self._saved_username}"
        )

        worker = APIWorker(
            api_client=self.api_client,
            operation="auto_relogin",
            method="POST",
            endpoint="/api/v1/auth/login/json",
            data={
                "username": self._saved_username,
                "password": self._saved_password
            }
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def cancel_all_operations(self) -> None:
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
