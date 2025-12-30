"""
Rate Limiting Middleware for F2X NeuroHub MES.

Implements a sliding window rate limiter to prevent API abuse and
ensure fair resource allocation across clients.

Features:
    - Per-IP rate limiting
    - Per-user rate limiting (when authenticated)
    - Configurable limits per endpoint pattern
    - Sliding window algorithm for smooth limiting
    - Standard rate limit headers (X-RateLimit-*)
    - Bypass for health check and internal endpoints
"""

import logging
import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
import re

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit rule."""
    requests: int  # Number of requests allowed
    window_seconds: int  # Time window in seconds
    burst: Optional[int] = None  # Optional burst allowance

    @property
    def effective_burst(self) -> int:
        """Get effective burst limit."""
        return self.burst if self.burst is not None else self.requests


@dataclass
class RateLimitState:
    """State for tracking rate limits per client."""
    request_times: List[float] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def cleanup(self, window_seconds: int) -> None:
        """Remove request times outside the window."""
        now = time.time()
        cutoff = now - window_seconds
        self.request_times = [t for t in self.request_times if t > cutoff]

    def add_request(self) -> None:
        """Record a new request."""
        self.request_times.append(time.time())

    @property
    def request_count(self) -> int:
        """Current number of requests in window."""
        return len(self.request_times)


class RateLimiter:
    """
    Sliding window rate limiter with per-client tracking.

    Uses a sliding window algorithm that provides smoother rate limiting
    compared to fixed window approaches.
    """

    def __init__(
        self,
        default_limit: int = 100,
        default_window: int = 60,
        cleanup_interval: int = 300,
    ):
        """
        Initialize rate limiter.

        Args:
            default_limit: Default requests per window
            default_window: Default window size in seconds
            cleanup_interval: Interval for cleaning up old entries
        """
        self.default_config = RateLimitConfig(
            requests=default_limit,
            window_seconds=default_window,
        )
        self.endpoint_configs: Dict[str, RateLimitConfig] = {}
        self.client_states: Dict[str, RateLimitState] = defaultdict(RateLimitState)
        self._lock = threading.Lock()
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()

    def configure_endpoint(
        self,
        pattern: str,
        requests: int,
        window_seconds: int,
        burst: Optional[int] = None,
    ) -> None:
        """
        Configure rate limit for endpoint pattern.

        Args:
            pattern: Regex pattern for matching endpoints
            requests: Number of requests allowed
            window_seconds: Time window in seconds
            burst: Optional burst allowance
        """
        self.endpoint_configs[pattern] = RateLimitConfig(
            requests=requests,
            window_seconds=window_seconds,
            burst=burst,
        )

    def get_config_for_path(self, path: str) -> RateLimitConfig:
        """Get rate limit config for a given path."""
        for pattern, config in self.endpoint_configs.items():
            if re.match(pattern, path):
                return config
        return self.default_config

    def check_rate_limit(
        self,
        client_id: str,
        path: str,
    ) -> Tuple[bool, int, int, int]:
        """
        Check if request is within rate limit.

        Args:
            client_id: Unique client identifier (IP or user ID)
            path: Request path

        Returns:
            Tuple of (allowed, remaining, limit, reset_time)
        """
        config = self.get_config_for_path(path)

        # Create composite key for client + endpoint pattern
        key = f"{client_id}:{self._get_pattern_key(path)}"

        with self._lock:
            # Periodic cleanup
            self._maybe_cleanup()

            state = self.client_states[key]

        with state.lock:
            state.cleanup(config.window_seconds)
            current_count = state.request_count

            if current_count < config.requests:
                state.add_request()
                remaining = config.requests - current_count - 1
                reset_time = int(time.time() + config.window_seconds)
                return True, max(0, remaining), config.requests, reset_time
            else:
                # Calculate when the oldest request will expire
                if state.request_times:
                    oldest = min(state.request_times)
                    reset_time = int(oldest + config.window_seconds)
                else:
                    reset_time = int(time.time() + config.window_seconds)
                return False, 0, config.requests, reset_time

    def _get_pattern_key(self, path: str) -> str:
        """Get pattern key for a path."""
        for pattern in self.endpoint_configs.keys():
            if re.match(pattern, path):
                return pattern
        return "default"

    def _maybe_cleanup(self) -> None:
        """Cleanup old entries if interval has passed."""
        now = time.time()
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries()
            self._last_cleanup = now

    def _cleanup_old_entries(self) -> None:
        """Remove entries with no recent requests."""
        now = time.time()
        max_window = max(
            (c.window_seconds for c in self.endpoint_configs.values()),
            default=self.default_config.window_seconds
        )
        cutoff = now - max_window * 2  # Keep 2x window for safety

        keys_to_remove = []
        for key, state in self.client_states.items():
            with state.lock:
                if not state.request_times or max(state.request_times) < cutoff:
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.client_states[key]

        if keys_to_remove:
            logger.debug(f"Cleaned up {len(keys_to_remove)} rate limit entries")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.

    Applies rate limits based on client IP or user ID (when authenticated).
    Adds standard rate limit headers to responses.

    Usage:
        app.add_middleware(
            RateLimitMiddleware,
            default_limit=100,
            default_window=60,
        )

    Headers added to responses:
        - X-RateLimit-Limit: Maximum requests allowed
        - X-RateLimit-Remaining: Requests remaining in window
        - X-RateLimit-Reset: Unix timestamp when limit resets
        - Retry-After: Seconds until retry (only on 429)
    """

    # Paths to bypass rate limiting
    BYPASS_PATHS = {
        "/health",
        "/",
        "/api/v1/docs",
        "/api/v1/redoc",
        "/api/v1/openapi.json",
    }

    # Paths with relaxed limits (WebSocket, metrics)
    RELAXED_PATHS = {
        r"^/api/v1/analytics/ws/.*": RateLimitConfig(requests=10, window_seconds=60),
    }

    def __init__(
        self,
        app: ASGIApp,
        default_limit: int = 100,
        default_window: int = 60,
        auth_user_multiplier: float = 2.0,
        enabled: bool = True,
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application
            default_limit: Default requests per window (per IP)
            default_window: Default window size in seconds
            auth_user_multiplier: Multiplier for authenticated users
            enabled: Whether rate limiting is enabled
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(
            default_limit=default_limit,
            default_window=default_window,
        )
        self.auth_user_multiplier = auth_user_multiplier
        self.enabled = enabled

        # Configure endpoint-specific limits
        self._configure_endpoint_limits()

        logger.info(
            f"Rate limiting initialized (enabled={enabled}, "
            f"default={default_limit} req/{default_window}s)"
        )

    def _configure_endpoint_limits(self) -> None:
        """Configure rate limits for specific endpoints."""
        # Stricter limits for auth endpoints (prevent brute force)
        self.rate_limiter.configure_endpoint(
            pattern=r"^/api/v1/auth/login",
            requests=10,
            window_seconds=60,
        )
        self.rate_limiter.configure_endpoint(
            pattern=r"^/api/v1/auth/.*",
            requests=30,
            window_seconds=60,
        )

        # Relaxed limits for read-heavy analytics
        self.rate_limiter.configure_endpoint(
            pattern=r"^/api/v1/analytics/.*",
            requests=200,
            window_seconds=60,
        )
        self.rate_limiter.configure_endpoint(
            pattern=r"^/api/v1/dashboard/.*",
            requests=200,
            window_seconds=60,
        )

        # Standard limits for write operations
        self.rate_limiter.configure_endpoint(
            pattern=r"^/api/v1/lots$",
            requests=50,
            window_seconds=60,
        )
        self.rate_limiter.configure_endpoint(
            pattern=r"^/api/v1/serials$",
            requests=100,
            window_seconds=60,
        )

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request with rate limiting."""
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)

        # Bypass certain paths
        path = request.url.path
        if path in self.BYPASS_PATHS:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        allowed, remaining, limit, reset_time = self.rate_limiter.check_rate_limit(
            client_id=client_id,
            path=path,
        )

        if not allowed:
            # Rate limit exceeded
            retry_after = max(1, reset_time - int(time.time()))
            return self._create_rate_limit_response(
                limit=limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier.

        Uses user ID if authenticated, otherwise falls back to IP address.
        Handles X-Forwarded-For for proxied requests.
        """
        # Try to get authenticated user ID from request state
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP in chain (original client)
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    def _create_rate_limit_response(
        self,
        limit: int,
        remaining: int,
        reset_time: int,
        retry_after: int,
    ) -> JSONResponse:
        """Create 429 Too Many Requests response."""
        logger.warning(
            f"Rate limit exceeded (limit={limit}, reset={reset_time})"
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
                "retry_after": retry_after,
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(retry_after),
            },
        )
