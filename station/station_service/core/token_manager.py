"""
Token Manager for Station Service.

Handles JWT token lifecycle management with reactive-only refresh.
Optimized for async operations with proper locking.

Key features:
- Reactive refresh only (triggered by 401 errors)
- No proactive refresh to reduce complexity
- Cooldown to prevent rapid refresh loops
- Single asyncio.Lock for thread-safety

This module provides a centralized way to manage authentication tokens
for Backend MES communication.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """
    Token information container.

    Attributes:
        access_token: JWT access token
        refresh_token: Refresh token for obtaining new access tokens
        expires_at: Token expiration timestamp
        user_id: Associated user ID
        username: Associated username
        station_api_key: Station API key for service-level calls
    """

    access_token: str
    refresh_token: str
    expires_at: Optional[datetime] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    station_api_key: Optional[str] = None

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """
        Check if token is expired or about to expire.

        Args:
            buffer_seconds: Buffer time before actual expiration to consider expired

        Returns:
            True if token is expired or will expire within buffer time
        """
        if self.expires_at is None:
            return False
        return datetime.now() >= (self.expires_at - timedelta(seconds=buffer_seconds))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "user_id": self.user_id,
            "username": self.username,
            "station_api_key": self.station_api_key,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenInfo":
        """Create TokenInfo from dictionary."""
        expires_at = None
        if data.get("expires_at"):
            expires_at = datetime.fromisoformat(data["expires_at"])
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=expires_at,
            user_id=data.get("user_id"),
            username=data.get("username"),
            station_api_key=data.get("station_api_key"),
        )


# Type alias for refresh callback
RefreshCallback = Callable[[str], Coroutine[Any, Any, Dict[str, Any]]]
TokenUpdateCallback = Callable[[str, str, Optional[datetime]], None]


class TokenManager:
    """
    Manages JWT token lifecycle with reactive-only refresh.

    This class provides token management with:
    - Simple sync getters (no proactive refresh)
    - Reactive refresh on 401 errors via handle_401_error()
    - Cooldown to prevent rapid refresh attempts
    - Callback notifications for token updates

    Usage:
        manager = TokenManager()
        manager.set_tokens(access_token, refresh_token, expires_in=1800)
        manager.set_refresh_callback(backend_client.refresh_access_token)

        # Get token (simple, no refresh)
        token = manager.get_access_token()

        # On 401 error
        if await manager.handle_401_error():
            # Retry the request
            pass
    """

    # Cooldown between refresh attempts (seconds)
    REFRESH_COOLDOWN_SECONDS: int = 5

    def __init__(self) -> None:
        """Initialize TokenManager."""
        self._token_info: Optional[TokenInfo] = None
        self._refresh_lock = asyncio.Lock()
        self._refresh_callback: Optional[RefreshCallback] = None
        self._token_update_callback: Optional[TokenUpdateCallback] = None
        self._last_refresh_attempt: Optional[datetime] = None

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: Optional[int] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        station_api_key: Optional[str] = None,
    ) -> None:
        """
        Set authentication tokens.

        Args:
            access_token: JWT access token
            refresh_token: Refresh token
            expires_in: Token expiration time in seconds
            user_id: Associated user ID
            username: Associated username
            station_api_key: Station API key for service-level calls
        """
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + timedelta(seconds=expires_in)

        self._token_info = TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_id=user_id,
            username=username,
            station_api_key=station_api_key,
        )
        # Reset cooldown on new tokens
        self._last_refresh_attempt = None

        logger.info(
            f"Tokens set for user {username or 'unknown'}, "
            f"expires_at: {expires_at.isoformat() if expires_at else 'unknown'}, "
            f"station_api_key: {'set' if station_api_key else 'not set'}"
        )

    def clear_tokens(self) -> None:
        """Clear all stored tokens."""
        self._token_info = None
        self._last_refresh_attempt = None
        logger.info("Tokens cleared")

    def get_access_token(self) -> Optional[str]:
        """
        Get current access token without refresh.

        This is a simple getter. Refresh is handled reactively
        via handle_401_error() when the backend rejects the token.

        Returns:
            Access token or None if not set
        """
        return self._token_info.access_token if self._token_info else None

    def get_refresh_token(self) -> Optional[str]:
        """
        Get current refresh token.

        Returns:
            Refresh token or None if not set
        """
        return self._token_info.refresh_token if self._token_info else None

    def get_station_api_key(self) -> Optional[str]:
        """
        Get current station API key.

        Returns:
            Station API key or None if not set
        """
        return self._token_info.station_api_key if self._token_info else None

    def get_token_info(self) -> Optional[TokenInfo]:
        """
        Get current token information.

        Returns:
            TokenInfo or None if not set
        """
        return self._token_info

    def has_valid_tokens(self) -> bool:
        """
        Check if tokens exist (basic check, not expiry-based).

        For UI hints only. Backend is the authority on token validity.

        Returns:
            True if tokens exist
        """
        return self._token_info is not None and bool(self._token_info.access_token)

    def is_token_expired(self) -> bool:
        """
        Check if token is likely expired (for UI hints).

        This is informational only. The backend decides actual validity.

        Returns:
            True if token appears expired based on local time
        """
        if not self._token_info:
            return True
        return self._token_info.is_expired()

    def set_refresh_callback(self, callback: RefreshCallback) -> None:
        """
        Set callback for refreshing tokens.

        The callback should accept a refresh token and return a dict with:
        - access_token: New access token
        - refresh_token: New or same refresh token
        - expires_in: Expiration time in seconds

        Args:
            callback: Async function to refresh tokens
        """
        self._refresh_callback = callback

    def set_token_update_callback(self, callback: TokenUpdateCallback) -> None:
        """
        Set callback for token update notifications.

        Called when tokens are refreshed, allowing external state updates.

        Args:
            callback: Function(access_token, refresh_token, expires_at)
        """
        self._token_update_callback = callback

    async def handle_401_error(self) -> bool:
        """
        Handle 401 Unauthorized error by refreshing token.

        This is the ONLY entry point for token refresh.
        Called by @with_auth decorator when 401 is received.

        Includes cooldown to prevent rapid refresh loops.

        Returns:
            True if refresh successful and request should be retried
        """
        # Check cooldown to prevent rapid refresh loops
        if self._last_refresh_attempt:
            elapsed = (datetime.now() - self._last_refresh_attempt).total_seconds()
            if elapsed < self.REFRESH_COOLDOWN_SECONDS:
                logger.warning(
                    f"Refresh cooldown active ({elapsed:.1f}s < {self.REFRESH_COOLDOWN_SECONDS}s)"
                )
                return False

        logger.info("Handling 401 error, attempting token refresh")
        return await self._do_refresh()

    async def _do_refresh(self) -> bool:
        """
        Perform token refresh with proper locking.

        Returns:
            True if refresh successful
        """
        async with self._refresh_lock:
            # Record attempt time (inside lock for accuracy)
            self._last_refresh_attempt = datetime.now()

            if not self._token_info:
                logger.warning("No token info available for refresh")
                return False

            if not self._refresh_callback:
                logger.warning("No refresh callback configured")
                return False

            refresh_token = self._token_info.refresh_token

            try:
                logger.info("Refreshing access token...")
                result = await self._refresh_callback(refresh_token)

                # Extract new tokens
                new_access_token = result.get("access_token")
                new_refresh_token = result.get("refresh_token", refresh_token)
                new_station_api_key = result.get("station_api_key")
                expires_in = result.get("expires_in")

                if not new_access_token:
                    logger.error("Refresh response missing access_token")
                    return False

                # Calculate expiration
                expires_at = None
                if expires_in:
                    expires_at = datetime.now() + timedelta(seconds=expires_in)

                # Update stored tokens
                self._token_info.access_token = new_access_token
                self._token_info.refresh_token = new_refresh_token
                self._token_info.expires_at = expires_at
                if new_station_api_key:
                    self._token_info.station_api_key = new_station_api_key

                logger.info(
                    f"Token refreshed successfully, "
                    f"expires_at: {expires_at.isoformat() if expires_at else 'unknown'}, "
                    f"station_api_key: {'updated' if new_station_api_key else 'unchanged'}"
                )

                # Notify callback
                if self._token_update_callback:
                    try:
                        self._token_update_callback(
                            new_access_token, new_refresh_token, expires_at
                        )
                    except Exception as e:
                        logger.warning(f"Token update callback failed: {e}")

                return True

            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                return False


# Global singleton instance
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    """
    Get the global TokenManager singleton.

    Thread-safe for single-threaded async apps (Python GIL protects simple reads).

    Returns:
        TokenManager instance
    """
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager


def reset_token_manager() -> None:
    """
    Reset the global TokenManager singleton.

    Useful for testing or when reinitializing the system.
    """
    global _token_manager
    if _token_manager:
        _token_manager.clear_tokens()
    _token_manager = None
