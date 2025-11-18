"""JWT Authentication Service"""

from PySide6.QtCore import QObject, Signal, QTimer
from datetime import datetime, timedelta
from typing import Optional
from .api_client import APIClient


class AuthService(QObject):
    """Manages JWT authentication lifecycle"""

    token_refreshed = Signal(str)  # Emit when token refreshed
    auth_error = Signal(str)       # Emit on auth failure
    login_success = Signal(dict)   # Emit user data on successful login

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.current_user: Optional[dict] = None

        # Token refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_token)

    def login(self, username: str, password: str) -> bool:
        """Login and store JWT token"""
        try:
            # Login request (form-data format)
            response = self.api_client.post('/api/v1/auth/login', {
                'username': username,
                'password': password
            })

            self.access_token = response['access_token']
            expires_in = response.get('expires_in', 1800)  # 30 min default
            self.current_user = response.get('user')
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

            # Store token in API client
            self.api_client.set_token(self.access_token)

            # Schedule token refresh (5 min before expiry)
            refresh_time = max((expires_in - 300) * 1000, 60000)  # At least 1 min
            self.refresh_timer.start(refresh_time)

            self.login_success.emit(self.current_user)
            return True

        except Exception as e:
            self.auth_error.emit(f"로그인 실패: {str(e)}")
            return False

    def logout(self):
        """Clear authentication state"""
        self.access_token = None
        self.token_expiry = None
        self.current_user = None
        self.refresh_timer.stop()
        self.api_client.clear_token()

    def validate_token(self) -> bool:
        """Validate current token by calling /me endpoint"""
        try:
            user = self.api_client.get('/api/v1/auth/me')
            self.current_user = user
            return True
        except Exception:
            return False

    def _refresh_token(self):
        """Refresh JWT token before expiry"""
        try:
            response = self.api_client.post('/api/v1/auth/refresh', {})
            self.access_token = response['access_token']
            self.api_client.set_token(self.access_token)
            self.token_refreshed.emit(self.access_token)
        except Exception as e:
            self.auth_error.emit(f"토큰 갱신 실패: {str(e)}")
            self.logout()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.access_token is not None and self.current_user is not None