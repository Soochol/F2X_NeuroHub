"""
In-memory caching layer for F2X NeuroHub MES.

Provides a simple, thread-safe caching mechanism for expensive queries
like analytics and dashboard endpoints. This implementation uses an
in-memory cache with TTL (Time To Live) support.

For production environments with multiple workers, consider using Redis
or Memcached instead.

Features:
    - Thread-safe operations
    - TTL-based expiration
    - LRU eviction when max size is reached
    - Cache statistics
    - Decorator for easy endpoint caching
"""

import functools
import hashlib
import json
import logging
import time
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class CacheEntry:
    """A single cache entry with value and metadata."""
    value: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.expires_at


@dataclass
class CacheStats:
    """Cache statistics for monitoring."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    current_size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate, 2),
            "evictions": self.evictions,
            "expirations": self.expirations,
            "current_size": self.current_size,
            "max_size": self.max_size,
        }


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL and LRU eviction.

    This is a simple caching solution suitable for single-process deployments.
    For multi-worker production environments, use Redis or Memcached.

    Example:
        cache = InMemoryCache(default_ttl=300, max_size=1000)

        # Manual usage
        cache.set("key", {"data": "value"}, ttl=60)
        value = cache.get("key")

        # Decorator usage
        @cache.cached(ttl=300, key_prefix="analytics")
        def get_expensive_data():
            return compute_something()
    """

    _instance: Optional['InMemoryCache'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> 'InMemoryCache':
        """Singleton pattern for cache instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        default_ttl: int = 300,  # 5 minutes
        max_size: int = 1000,
        cleanup_interval: int = 60,  # 1 minute
    ):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds
            max_size: Maximum number of entries before LRU eviction
            cleanup_interval: Interval for expired entry cleanup (seconds)
        """
        if hasattr(self, '_initialized'):
            return

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._stats = CacheStats(max_size=max_size)
        self._data_lock = threading.RLock()
        self._initialized = True

        # Start background cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="cache-cleanup"
        )
        self._cleanup_thread.start()

        logger.info(
            f"Cache initialized (default_ttl={default_ttl}s, max_size={max_size})"
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._data_lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired:
                self._delete_entry(key)
                self._stats.misses += 1
                self._stats.expirations += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            entry.hits += 1
            self._stats.hits += 1
            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time.time() + ttl

        with self._data_lock:
            # Evict if at max size
            while len(self._cache) >= self._max_size:
                self._evict_oldest()

            self._cache[key] = CacheEntry(
                value=value,
                expires_at=expires_at,
            )
            self._cache.move_to_end(key)
            self._stats.current_size = len(self._cache)

    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        with self._data_lock:
            return self._delete_entry(key)

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        with self._data_lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats.current_size = 0
            logger.info(f"Cache cleared ({count} entries)")
            return count

    def invalidate_prefix(self, prefix: str) -> int:
        """
        Invalidate all entries with matching key prefix.

        Args:
            prefix: Key prefix to match

        Returns:
            Number of entries invalidated
        """
        with self._data_lock:
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                self._delete_entry(key)
            logger.debug(f"Invalidated {len(keys_to_delete)} entries with prefix '{prefix}'")
            return len(keys_to_delete)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._data_lock:
            self._stats.current_size = len(self._cache)
            return self._stats.to_dict()

    def _delete_entry(self, key: str) -> bool:
        """Delete entry without lock (internal use)."""
        if key in self._cache:
            del self._cache[key]
            self._stats.current_size = len(self._cache)
            return True
        return False

    def _evict_oldest(self) -> None:
        """Evict oldest entry (LRU)."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._delete_entry(oldest_key)
            self._stats.evictions += 1

    def _cleanup_loop(self) -> None:
        """Background thread for cleaning up expired entries."""
        while True:
            time.sleep(self._cleanup_interval)
            self._cleanup_expired()

    def _cleanup_expired(self) -> int:
        """Remove expired entries."""
        with self._data_lock:
            now = time.time()
            expired_keys = [
                k for k, v in self._cache.items()
                if now > v.expires_at
            ]
            for key in expired_keys:
                self._delete_entry(key)
                self._stats.expirations += 1

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

    def cached(
        self,
        ttl: Optional[int] = None,
        key_prefix: str = "",
        key_builder: Optional[Callable[..., str]] = None,
    ) -> Callable[[F], F]:
        """
        Decorator for caching function results.

        Args:
            ttl: Time-to-live in seconds
            key_prefix: Prefix for cache key
            key_builder: Custom function to build cache key from args/kwargs

        Returns:
            Decorated function with caching

        Example:
            @cache.cached(ttl=300, key_prefix="analytics")
            def get_dashboard_summary(db, target_date):
                return expensive_computation()
        """
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = self._build_cache_key(
                        func.__name__,
                        key_prefix,
                        args,
                        kwargs
                    )

                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result

            # Add cache control methods to wrapper
            wrapper.cache_clear = lambda: self.invalidate_prefix(  # type: ignore
                f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            )

            return cast(F, wrapper)
        return decorator

    def _build_cache_key(
        self,
        func_name: str,
        prefix: str,
        args: tuple,
        kwargs: dict,
    ) -> str:
        """Build cache key from function name and arguments."""
        # Skip first arg if it's a db session (common pattern)
        serializable_args = []
        for arg in args:
            if hasattr(arg, '__class__') and 'Session' in arg.__class__.__name__:
                continue
            if hasattr(arg, '__class__') and 'User' in arg.__class__.__name__:
                # Include user ID for user-specific caching if needed
                continue
            try:
                json.dumps(arg)
                serializable_args.append(arg)
            except (TypeError, ValueError):
                serializable_args.append(str(type(arg).__name__))

        # Filter out non-serializable kwargs
        serializable_kwargs = {}
        for k, v in kwargs.items():
            if k in ('db', 'current_user'):
                continue
            try:
                json.dumps(v)
                serializable_kwargs[k] = v
            except (TypeError, ValueError):
                serializable_kwargs[k] = str(type(v).__name__)

        # Create hash of args for key
        key_data = json.dumps({
            "args": serializable_args,
            "kwargs": serializable_kwargs,
        }, sort_keys=True, default=str)

        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]

        if prefix:
            return f"{prefix}:{func_name}:{key_hash}"
        return f"{func_name}:{key_hash}"


# Global cache instance
cache = InMemoryCache()


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None,
) -> Callable[[F], F]:
    """
    Convenience decorator using global cache instance.

    Args:
        ttl: Time-to-live in seconds (default: 300 = 5 minutes)
        key_prefix: Prefix for cache key
        key_builder: Custom function to build cache key

    Example:
        from app.core.cache import cached

        @cached(ttl=60, key_prefix="dashboard")
        def get_dashboard_summary(db: Session):
            return expensive_query(db)
    """
    return cache.cached(ttl=ttl, key_prefix=key_prefix, key_builder=key_builder)


def invalidate_cache(prefix: str) -> int:
    """
    Invalidate cache entries with prefix.

    Args:
        prefix: Key prefix to invalidate

    Returns:
        Number of entries invalidated
    """
    return cache.invalidate_prefix(prefix)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return cache.get_stats()


def clear_cache() -> int:
    """Clear all cache entries."""
    return cache.clear()
