"""
Database Query Performance Monitoring Module

This module provides comprehensive monitoring for database query performance,
including execution time tracking, slow query detection, and query statistics.
"""

import functools
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, TypeVar, cast
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
import json
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs/monitoring")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configure file handler for slow queries
slow_query_handler = logging.FileHandler(LOGS_DIR / "slow_queries.log")
slow_query_handler.setLevel(logging.WARNING)
slow_query_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
slow_query_handler.setFormatter(slow_query_formatter)
logger.addHandler(slow_query_handler)

# Type variable for generic decorator
F = TypeVar('F', bound=Callable[..., Any])

@dataclass
class QueryMetrics:
    """Container for query performance metrics."""
    query: str
    execution_time_ms: float
    timestamp: datetime
    parameters: Optional[Dict[str, Any]] = None
    result_count: Optional[int] = None
    error: Optional[str] = None
    stack_trace: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            "query": self.query,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "parameters": self.parameters,
            "result_count": self.result_count,
            "error": self.error,
            "stack_trace": self.stack_trace,
        }


@dataclass
class QueryStatistics:
    """Aggregated statistics for a specific query pattern."""
    query_pattern: str
    total_executions: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    slow_executions: int = 0
    failed_executions: int = 0
    last_execution: Optional[datetime] = None
    recent_execution_times: List[float] = field(default_factory=lambda: deque(maxlen=100))

    def update(self, metrics: QueryMetrics, slow_threshold_ms: float = 100):
        """Update statistics with new query metrics."""
        self.total_executions += 1
        self.total_time_ms += metrics.execution_time_ms
        self.min_time_ms = min(self.min_time_ms, metrics.execution_time_ms)
        self.max_time_ms = max(self.max_time_ms, metrics.execution_time_ms)
        self.avg_time_ms = self.total_time_ms / self.total_executions
        self.last_execution = metrics.timestamp
        self.recent_execution_times.append(metrics.execution_time_ms)

        if metrics.execution_time_ms > slow_threshold_ms:
            self.slow_executions += 1

        if metrics.error:
            self.failed_executions += 1

    def get_p95(self) -> float:
        """Calculate 95th percentile of recent execution times."""
        if not self.recent_execution_times:
            return 0.0
        sorted_times = sorted(self.recent_execution_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary for reporting."""
        return {
            "query_pattern": self.query_pattern,
            "total_executions": self.total_executions,
            "total_time_ms": self.total_time_ms,
            "min_time_ms": self.min_time_ms,
            "max_time_ms": self.max_time_ms,
            "avg_time_ms": self.avg_time_ms,
            "p95_time_ms": self.get_p95(),
            "slow_executions": self.slow_executions,
            "failed_executions": self.failed_executions,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "slow_execution_rate": (self.slow_executions / self.total_executions * 100) if self.total_executions > 0 else 0,
            "failure_rate": (self.failed_executions / self.total_executions * 100) if self.total_executions > 0 else 0,
        }


class QueryMonitor:
    """
    Singleton class for monitoring database query performance.

    Features:
    - Tracks execution time for all queries
    - Detects and logs slow queries (>100ms by default)
    - Maintains query statistics
    - Thread-safe operations
    """

    _instance: Optional['QueryMonitor'] = None
    _lock = Lock()

    def __new__(cls) -> 'QueryMonitor':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.slow_query_threshold_ms = float(os.getenv('SLOW_QUERY_THRESHOLD_MS', '100'))
            self.max_query_log_size = int(os.getenv('MAX_QUERY_LOG_SIZE', '10000'))
            self.query_log: deque[QueryMetrics] = deque(maxlen=self.max_query_log_size)
            self.query_stats: Dict[str, QueryStatistics] = defaultdict(lambda: QueryStatistics(query_pattern=""))
            self.enabled = os.getenv('ENABLE_QUERY_MONITORING', 'true').lower() == 'true'
            self._initialized = True
            self._stats_lock = Lock()
            logger.info(f"Query Monitor initialized (enabled={self.enabled}, slow_threshold={self.slow_query_threshold_ms}ms)")

    def track_query(self, query: str, execution_time_ms: float,
                   parameters: Optional[Dict[str, Any]] = None,
                   result_count: Optional[int] = None,
                   error: Optional[str] = None) -> None:
        """
        Track a database query execution.

        Args:
            query: SQL query string or query identifier
            execution_time_ms: Query execution time in milliseconds
            parameters: Optional query parameters
            result_count: Optional number of results returned
            error: Optional error message if query failed
        """
        if not self.enabled:
            return

        metrics = QueryMetrics(
            query=query,
            execution_time_ms=execution_time_ms,
            timestamp=datetime.now(),
            parameters=parameters,
            result_count=result_count,
            error=error,
            stack_trace=traceback.format_stack() if error else None
        )

        # Add to query log
        self.query_log.append(metrics)

        # Update statistics
        query_pattern = self._extract_query_pattern(query)
        with self._stats_lock:
            if query_pattern not in self.query_stats:
                self.query_stats[query_pattern] = QueryStatistics(query_pattern=query_pattern)
            self.query_stats[query_pattern].update(metrics, self.slow_query_threshold_ms)

        # Log slow queries
        if execution_time_ms > self.slow_query_threshold_ms:
            self._log_slow_query(metrics)

    def _extract_query_pattern(self, query: str) -> str:
        """
        Extract a normalized pattern from a query for grouping similar queries.

        Args:
            query: SQL query string

        Returns:
            Normalized query pattern
        """
        # Simple pattern extraction - can be enhanced based on needs
        # Remove specific values to group similar queries
        import re

        # Remove numbers
        pattern = re.sub(r'\b\d+\b', '?', query)
        # Remove quoted strings
        pattern = re.sub(r"'[^']*'", '?', pattern)
        pattern = re.sub(r'"[^"]*"', '?', pattern)
        # Normalize whitespace
        pattern = ' '.join(pattern.split())
        # Truncate long queries
        if len(pattern) > 200:
            pattern = pattern[:200] + '...'

        return pattern

    def _log_slow_query(self, metrics: QueryMetrics) -> None:
        """Log slow query details for analysis."""
        log_message = {
            "type": "SLOW_QUERY",
            "query": metrics.query[:500],  # Truncate very long queries
            "execution_time_ms": metrics.execution_time_ms,
            "threshold_ms": self.slow_query_threshold_ms,
            "timestamp": metrics.timestamp.isoformat(),
            "parameters": metrics.parameters,
            "result_count": metrics.result_count,
        }

        logger.warning(f"Slow query detected: {json.dumps(log_message, indent=2)}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current query statistics.

        Returns:
            Dictionary containing query statistics
        """
        with self._stats_lock:
            stats = {
                "total_queries": sum(stat.total_executions for stat in self.query_stats.values()),
                "total_slow_queries": sum(stat.slow_executions for stat in self.query_stats.values()),
                "total_failed_queries": sum(stat.failed_executions for stat in self.query_stats.values()),
                "query_patterns": len(self.query_stats),
                "slowest_queries": self._get_slowest_queries(5),
                "most_frequent_queries": self._get_most_frequent_queries(5),
                "recent_slow_queries": self._get_recent_slow_queries(10),
                "statistics_by_pattern": {
                    pattern: stats.to_dict()
                    for pattern, stats in self.query_stats.items()
                }
            }
        return stats

    def _get_slowest_queries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the slowest query patterns by average execution time."""
        sorted_stats = sorted(
            self.query_stats.values(),
            key=lambda x: x.avg_time_ms,
            reverse=True
        )[:limit]

        return [
            {
                "pattern": stat.query_pattern,
                "avg_time_ms": stat.avg_time_ms,
                "max_time_ms": stat.max_time_ms,
                "executions": stat.total_executions
            }
            for stat in sorted_stats
        ]

    def _get_most_frequent_queries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequently executed query patterns."""
        sorted_stats = sorted(
            self.query_stats.values(),
            key=lambda x: x.total_executions,
            reverse=True
        )[:limit]

        return [
            {
                "pattern": stat.query_pattern,
                "executions": stat.total_executions,
                "avg_time_ms": stat.avg_time_ms,
                "total_time_ms": stat.total_time_ms
            }
            for stat in sorted_stats
        ]

    def _get_recent_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries from the query log."""
        slow_queries = [
            metrics for metrics in self.query_log
            if metrics.execution_time_ms > self.slow_query_threshold_ms
        ]

        # Sort by timestamp (most recent first)
        slow_queries.sort(key=lambda x: x.timestamp, reverse=True)

        return [
            {
                "query": metrics.query[:200],
                "execution_time_ms": metrics.execution_time_ms,
                "timestamp": metrics.timestamp.isoformat(),
                "parameters": metrics.parameters
            }
            for metrics in slow_queries[:limit]
        ]

    def reset_statistics(self) -> None:
        """Reset all collected statistics."""
        with self._stats_lock:
            self.query_log.clear()
            self.query_stats.clear()
            logger.info("Query statistics reset")

    def export_statistics(self, filepath: Optional[str] = None) -> str:
        """
        Export statistics to a JSON file.

        Args:
            filepath: Optional path for the export file

        Returns:
            Path to the exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = str(LOGS_DIR / f"query_stats_{timestamp}.json")

        stats = self.get_statistics()
        stats["exported_at"] = datetime.now().isoformat()

        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info(f"Query statistics exported to {filepath}")
        return filepath


# Decorator for monitoring database queries
def monitor_query(query_name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to monitor database query performance.

    Args:
        query_name: Optional name for the query (uses function name if not provided)

    Example:
        @monitor_query("get_user_by_id")
        async def get_user(db: Session, user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = QueryMonitor()
            name = query_name or func.__name__
            start_time = time.perf_counter()
            error = None
            result = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                execution_time_ms = (time.perf_counter() - start_time) * 1000
                result_count = None

                # Try to get result count if applicable
                if result is not None:
                    if hasattr(result, '__len__'):
                        result_count = len(result)
                    elif hasattr(result, 'count'):
                        try:
                            result_count = result.count()
                        except:
                            pass

                monitor.track_query(
                    query=name,
                    execution_time_ms=execution_time_ms,
                    parameters={**kwargs} if kwargs else None,
                    result_count=result_count,
                    error=error
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = QueryMonitor()
            name = query_name or func.__name__
            start_time = time.perf_counter()
            error = None
            result = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                execution_time_ms = (time.perf_counter() - start_time) * 1000
                result_count = None

                # Try to get result count if applicable
                if result is not None:
                    if hasattr(result, '__len__'):
                        result_count = len(result)
                    elif hasattr(result, 'count'):
                        try:
                            result_count = result.count()
                        except:
                            pass

                monitor.track_query(
                    query=name,
                    execution_time_ms=execution_time_ms,
                    parameters={**kwargs} if kwargs else None,
                    result_count=result_count,
                    error=error
                )

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator


# Convenience functions for global access
def get_query_stats() -> Dict[str, Any]:
    """Get current query statistics."""
    return QueryMonitor().get_statistics()


def reset_query_stats() -> None:
    """Reset query statistics."""
    QueryMonitor().reset_statistics()


def log_slow_queries(filepath: Optional[str] = None) -> str:
    """Export query statistics to a file."""
    return QueryMonitor().export_statistics(filepath)


# SQLAlchemy event listener for automatic query monitoring (optional)
def setup_sqlalchemy_monitoring(engine):
    """
    Set up automatic monitoring for SQLAlchemy queries.

    Args:
        engine: SQLAlchemy engine instance

    Example:
        from sqlalchemy import create_engine
        engine = create_engine("postgresql://...")
        setup_sqlalchemy_monitoring(engine)
    """
    from sqlalchemy import event

    monitor = QueryMonitor()

    @event.listens_for(engine, "before_execute")
    def receive_before_execute(conn, clauseelement, multiparams, params, execution_options):
        conn.info['query_start_time'] = time.perf_counter()
        conn.info['query_statement'] = str(clauseelement)

    @event.listens_for(engine, "after_execute")
    def receive_after_execute(conn, clauseelement, multiparams, params, execution_options, result):
        if 'query_start_time' in conn.info:
            execution_time_ms = (time.perf_counter() - conn.info['query_start_time']) * 1000
            query = conn.info.get('query_statement', str(clauseelement))

            monitor.track_query(
                query=query,
                execution_time_ms=execution_time_ms,
                parameters=dict(params) if params else None,
                result_count=result.rowcount if hasattr(result, 'rowcount') else None
            )

    logger.info("SQLAlchemy query monitoring enabled")