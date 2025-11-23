"""
Performance Metrics Collection and Analysis Module

This module provides comprehensive performance monitoring for API endpoints,
database operations, and system resources including memory and CPU usage.
"""

import functools
import time
import psutil
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, TypeVar
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from threading import Lock, Thread
from pathlib import Path
import os
import statistics

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs/monitoring")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configure performance metrics handler
perf_handler = logging.FileHandler(LOGS_DIR / "performance_metrics.log")
perf_handler.setLevel(logging.INFO)
perf_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
perf_handler.setFormatter(perf_formatter)
logger.addHandler(perf_handler)

# Type variable for generic decorator
F = TypeVar('F', bound=Callable[..., Any])

@dataclass
class EndpointMetrics:
    """Container for API endpoint performance metrics."""
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    timestamp: datetime
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    user_id: Optional[str] = None
    error: Optional[str] = None
    memory_used_mb: Optional[float] = None
    cpu_percent: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "response_time_ms": self.response_time_ms,
            "status_code": self.status_code,
            "timestamp": self.timestamp.isoformat(),
            "request_size_bytes": self.request_size_bytes,
            "response_size_bytes": self.response_size_bytes,
            "user_id": self.user_id,
            "error": self.error,
            "memory_used_mb": self.memory_used_mb,
            "cpu_percent": self.cpu_percent,
        }


@dataclass
class DatabaseOperationMetrics:
    """Container for database operation metrics."""
    operation: str
    table: str
    duration_ms: float
    rows_affected: Optional[int]
    timestamp: datetime
    connection_pool_size: Optional[int] = None
    active_connections: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class SystemMetrics:
    """Container for system resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    open_connections: int
    thread_count: int
    process_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb,
            "memory_available_mb": self.memory_available_mb,
            "disk_io_read_mb": self.disk_io_read_mb,
            "disk_io_write_mb": self.disk_io_write_mb,
            "network_sent_mb": self.network_sent_mb,
            "network_recv_mb": self.network_recv_mb,
            "open_connections": self.open_connections,
            "thread_count": self.thread_count,
            "process_count": self.process_count,
        }


@dataclass
class EndpointStatistics:
    """Aggregated statistics for an API endpoint."""
    endpoint: str
    method: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time_ms: float = 0.0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    recent_response_times: List[float] = field(default_factory=lambda: deque(maxlen=100))
    status_codes: Dict[int, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=lambda: deque(maxlen=50))
    last_request: Optional[datetime] = None

    def update(self, metrics: EndpointMetrics):
        """Update statistics with new endpoint metrics."""
        self.total_requests += 1
        self.total_response_time_ms += metrics.response_time_ms
        self.min_response_time_ms = min(self.min_response_time_ms, metrics.response_time_ms)
        self.max_response_time_ms = max(self.max_response_time_ms, metrics.response_time_ms)
        self.avg_response_time_ms = self.total_response_time_ms / self.total_requests
        self.recent_response_times.append(metrics.response_time_ms)
        self.last_request = metrics.timestamp

        # Track status codes
        self.status_codes[metrics.status_code] = self.status_codes.get(metrics.status_code, 0) + 1

        # Track success/failure
        if 200 <= metrics.status_code < 400:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        # Track errors
        if metrics.error:
            self.errors.append(f"{metrics.timestamp.isoformat()}: {metrics.error}")

    def get_percentiles(self) -> Dict[str, float]:
        """Calculate percentiles for response times."""
        if not self.recent_response_times:
            return {"p50": 0, "p75": 0, "p90": 0, "p95": 0, "p99": 0}

        sorted_times = sorted(self.recent_response_times)
        return {
            "p50": statistics.median(sorted_times),
            "p75": sorted_times[int(len(sorted_times) * 0.75)],
            "p90": sorted_times[int(len(sorted_times) * 0.90)],
            "p95": sorted_times[int(len(sorted_times) * 0.95)],
            "p99": sorted_times[min(int(len(sorted_times) * 0.99), len(sorted_times) - 1)],
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        percentiles = self.get_percentiles()
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
            "min_response_time_ms": self.min_response_time_ms,
            "max_response_time_ms": self.max_response_time_ms,
            "avg_response_time_ms": self.avg_response_time_ms,
            "percentiles": percentiles,
            "status_codes": self.status_codes,
            "recent_errors": list(self.errors)[-10:],  # Last 10 errors
            "last_request": self.last_request.isoformat() if self.last_request else None,
        }


class PerformanceTracker:
    """
    Singleton class for tracking application performance metrics.

    Features:
    - API endpoint performance monitoring
    - Database operation tracking
    - System resource monitoring
    - Real-time metrics collection
    - Performance alerts
    """

    _instance: Optional['PerformanceTracker'] = None
    _lock = Lock()

    def __new__(cls) -> 'PerformanceTracker':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.enabled = os.getenv('ENABLE_PERFORMANCE_MONITORING', 'true').lower() == 'true'
            self.max_metrics_log_size = int(os.getenv('MAX_METRICS_LOG_SIZE', '10000'))

            # Metrics storage
            self.endpoint_metrics_log: deque[EndpointMetrics] = deque(maxlen=self.max_metrics_log_size)
            self.db_metrics_log: deque[DatabaseOperationMetrics] = deque(maxlen=self.max_metrics_log_size)
            self.system_metrics_log: deque[SystemMetrics] = deque(maxlen=1000)

            # Statistics
            self.endpoint_stats: Dict[str, EndpointStatistics] = defaultdict(lambda: EndpointStatistics("", ""))

            # Alert thresholds
            self.response_time_alert_ms = float(os.getenv('RESPONSE_TIME_ALERT_MS', '1000'))
            self.memory_alert_percent = float(os.getenv('MEMORY_ALERT_PERCENT', '80'))
            self.cpu_alert_percent = float(os.getenv('CPU_ALERT_PERCENT', '80'))
            self.error_rate_alert_percent = float(os.getenv('ERROR_RATE_ALERT_PERCENT', '5'))

            # Resource monitoring
            self._monitoring_thread: Optional[Thread] = None
            self._monitoring_active = False
            self._stats_lock = Lock()

            # Initialize process for resource monitoring
            self.process = psutil.Process()

            # Network and disk I/O baseline
            self._last_net_io = psutil.net_io_counters()
            self._last_disk_io = psutil.disk_io_counters()
            self._last_check_time = time.time()

            self._initialized = True

            if self.enabled:
                self.start_resource_monitoring()

            logger.info(f"Performance Tracker initialized (enabled={self.enabled})")

    def track_endpoint(self, endpoint: str, method: str, response_time_ms: float,
                      status_code: int, request_size: Optional[int] = None,
                      response_size: Optional[int] = None, user_id: Optional[str] = None,
                      error: Optional[str] = None) -> None:
        """
        Track API endpoint performance metrics.

        Args:
            endpoint: API endpoint path
            method: HTTP method
            response_time_ms: Response time in milliseconds
            status_code: HTTP status code
            request_size: Request body size in bytes
            response_size: Response body size in bytes
            user_id: User identifier
            error: Error message if request failed
        """
        if not self.enabled:
            return

        # Capture current resource usage
        memory_info = self.process.memory_info()
        memory_used_mb = memory_info.rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent()

        metrics = EndpointMetrics(
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            status_code=status_code,
            timestamp=datetime.now(),
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            user_id=user_id,
            error=error,
            memory_used_mb=memory_used_mb,
            cpu_percent=cpu_percent
        )

        # Add to log
        self.endpoint_metrics_log.append(metrics)

        # Update statistics
        key = f"{method}:{endpoint}"
        with self._stats_lock:
            if key not in self.endpoint_stats:
                self.endpoint_stats[key] = EndpointStatistics(endpoint=endpoint, method=method)
            self.endpoint_stats[key].update(metrics)

        # Check for alerts
        self._check_endpoint_alerts(metrics)

    def track_database_operation(self, operation: str, table: str, duration_ms: float,
                                rows_affected: Optional[int] = None,
                                connection_pool_size: Optional[int] = None,
                                active_connections: Optional[int] = None,
                                error: Optional[str] = None) -> None:
        """
        Track database operation metrics.

        Args:
            operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
            table: Database table name
            duration_ms: Operation duration in milliseconds
            rows_affected: Number of rows affected
            connection_pool_size: Total connections in pool
            active_connections: Number of active connections
            error: Error message if operation failed
        """
        if not self.enabled:
            return

        metrics = DatabaseOperationMetrics(
            operation=operation,
            table=table,
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            timestamp=datetime.now(),
            connection_pool_size=connection_pool_size,
            active_connections=active_connections,
            error=error
        )

        self.db_metrics_log.append(metrics)

    def _check_endpoint_alerts(self, metrics: EndpointMetrics) -> None:
        """Check and trigger alerts based on metrics."""
        # Response time alert
        if metrics.response_time_ms > self.response_time_alert_ms:
            logger.warning(f"SLOW_ENDPOINT: {metrics.method} {metrics.endpoint} "
                         f"took {metrics.response_time_ms}ms (threshold: {self.response_time_alert_ms}ms)")

        # Error alert
        if metrics.status_code >= 500:
            logger.error(f"ENDPOINT_ERROR: {metrics.method} {metrics.endpoint} "
                        f"returned {metrics.status_code}: {metrics.error}")

        # Memory alert
        if metrics.memory_used_mb:
            memory_percent = (metrics.memory_used_mb / psutil.virtual_memory().total * 1024 * 1024) * 100
            if memory_percent > self.memory_alert_percent:
                logger.warning(f"HIGH_MEMORY: {memory_percent:.1f}% memory used "
                             f"(threshold: {self.memory_alert_percent}%)")

    def start_resource_monitoring(self, interval_seconds: int = 60) -> None:
        """
        Start background thread for system resource monitoring.

        Args:
            interval_seconds: Monitoring interval in seconds
        """
        if self._monitoring_active:
            return

        def monitor_resources():
            self._monitoring_active = True
            logger.info(f"Resource monitoring started (interval={interval_seconds}s)")

            while self._monitoring_active:
                try:
                    metrics = self._collect_system_metrics()
                    self.system_metrics_log.append(metrics)

                    # Check resource alerts
                    if metrics.cpu_percent > self.cpu_alert_percent:
                        logger.warning(f"HIGH_CPU: {metrics.cpu_percent:.1f}% CPU usage")

                    if metrics.memory_percent > self.memory_alert_percent:
                        logger.warning(f"HIGH_MEMORY: {metrics.memory_percent:.1f}% memory usage")

                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")

                time.sleep(interval_seconds)

        self._monitoring_thread = Thread(target=monitor_resources, daemon=True)
        self._monitoring_thread.start()

    def stop_resource_monitoring(self) -> None:
        """Stop background resource monitoring."""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
            self._monitoring_thread = None
        logger.info("Resource monitoring stopped")

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system resource metrics."""
        current_time = time.time()
        time_delta = current_time - self._last_check_time

        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # Network I/O
        net_io = psutil.net_io_counters()
        net_sent_mb = (net_io.bytes_sent - self._last_net_io.bytes_sent) / 1024 / 1024 / time_delta
        net_recv_mb = (net_io.bytes_recv - self._last_net_io.bytes_recv) / 1024 / 1024 / time_delta
        self._last_net_io = net_io

        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = (disk_io.read_bytes - self._last_disk_io.read_bytes) / 1024 / 1024 / time_delta
        disk_write_mb = (disk_io.write_bytes - self._last_disk_io.write_bytes) / 1024 / 1024 / time_delta
        self._last_disk_io = disk_io

        # Process info
        open_connections = len(psutil.net_connections())
        thread_count = self.process.num_threads()
        process_count = len(psutil.pids())

        self._last_check_time = current_time

        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=net_sent_mb,
            network_recv_mb=net_recv_mb,
            open_connections=open_connections,
            thread_count=thread_count,
            process_count=process_count
        )

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.

        Returns:
            Dictionary containing performance metrics summary
        """
        with self._stats_lock:
            # Endpoint summary
            total_requests = sum(stat.total_requests for stat in self.endpoint_stats.values())
            total_errors = sum(stat.failed_requests for stat in self.endpoint_stats.values())

            # Response time analysis
            all_response_times = []
            for stat in self.endpoint_stats.values():
                all_response_times.extend(list(stat.recent_response_times))

            response_time_stats = {}
            if all_response_times:
                response_time_stats = {
                    "min": min(all_response_times),
                    "max": max(all_response_times),
                    "avg": statistics.mean(all_response_times),
                    "median": statistics.median(all_response_times),
                    "stdev": statistics.stdev(all_response_times) if len(all_response_times) > 1 else 0,
                }

            # Recent system metrics
            recent_system_metrics = None
            if self.system_metrics_log:
                latest = self.system_metrics_log[-1]
                recent_system_metrics = latest.to_dict()

            # Database operation summary
            db_operations = defaultdict(lambda: {"count": 0, "total_time_ms": 0})
            for metric in self.db_metrics_log:
                key = f"{metric.operation}:{metric.table}"
                db_operations[key]["count"] += 1
                db_operations[key]["total_time_ms"] += metric.duration_ms

            summary = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_enabled": self.enabled,
                "endpoint_metrics": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "error_rate_percent": (total_errors / total_requests * 100) if total_requests > 0 else 0,
                    "response_time_stats": response_time_stats,
                    "endpoints": {
                        key: stat.to_dict()
                        for key, stat in self.endpoint_stats.items()
                    }
                },
                "database_metrics": {
                    "operations": dict(db_operations),
                    "total_operations": len(self.db_metrics_log),
                },
                "system_metrics": recent_system_metrics,
                "alerts": {
                    "response_time_threshold_ms": self.response_time_alert_ms,
                    "memory_threshold_percent": self.memory_alert_percent,
                    "cpu_threshold_percent": self.cpu_alert_percent,
                    "error_rate_threshold_percent": self.error_rate_alert_percent,
                }
            }

        return summary

    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """
        Export performance metrics to JSON file.

        Args:
            filepath: Optional path for export file

        Returns:
            Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = str(LOGS_DIR / f"performance_metrics_{timestamp}.json")

        summary = self.get_performance_summary()

        # Add detailed logs
        summary["detailed_logs"] = {
            "recent_endpoint_metrics": [
                m.to_dict() for m in list(self.endpoint_metrics_log)[-100:]
            ],
            "recent_db_metrics": [
                m.to_dict() for m in list(self.db_metrics_log)[-100:]
            ],
            "recent_system_metrics": [
                m.to_dict() for m in list(self.system_metrics_log)[-50:]
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Performance metrics exported to {filepath}")
        return filepath

    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        with self._stats_lock:
            self.endpoint_metrics_log.clear()
            self.db_metrics_log.clear()
            self.system_metrics_log.clear()
            self.endpoint_stats.clear()
            logger.info("Performance metrics reset")


# Decorator for monitoring API endpoints
def monitor_endpoint(endpoint_name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to monitor API endpoint performance.

    Args:
        endpoint_name: Optional endpoint name (uses function name if not provided)

    Example:
        @monitor_endpoint("/api/users/{id}")
        async def get_user(user_id: int):
            return await fetch_user(user_id)
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracker = PerformanceTracker()
            name = endpoint_name or func.__name__
            start_time = time.perf_counter()
            error = None
            status_code = 200

            try:
                result = await func(*args, **kwargs)

                # Try to extract status code from result
                if hasattr(result, 'status_code'):
                    status_code = result.status_code

                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                response_time_ms = (time.perf_counter() - start_time) * 1000

                tracker.track_endpoint(
                    endpoint=name,
                    method="UNKNOWN",  # Would be set by framework integration
                    response_time_ms=response_time_ms,
                    status_code=status_code,
                    error=error
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracker = PerformanceTracker()
            name = endpoint_name or func.__name__
            start_time = time.perf_counter()
            error = None
            status_code = 200

            try:
                result = func(*args, **kwargs)

                # Try to extract status code from result
                if hasattr(result, 'status_code'):
                    status_code = result.status_code

                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                response_time_ms = (time.perf_counter() - start_time) * 1000

                tracker.track_endpoint(
                    endpoint=name,
                    method="UNKNOWN",  # Would be set by framework integration
                    response_time_ms=response_time_ms,
                    status_code=status_code,
                    error=error
                )

        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Convenience functions
def export_metrics(filepath: Optional[str] = None) -> str:
    """Export performance metrics to file."""
    return PerformanceTracker().export_metrics(filepath)


def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary."""
    return PerformanceTracker().get_performance_summary()


def monitor_memory() -> Dict[str, float]:
    """Get current memory usage metrics."""
    process = psutil.Process()
    memory_info = process.memory_info()
    system_memory = psutil.virtual_memory()

    return {
        "process_memory_mb": memory_info.rss / 1024 / 1024,
        "process_memory_percent": process.memory_percent(),
        "system_memory_percent": system_memory.percent,
        "system_memory_available_mb": system_memory.available / 1024 / 1024,
    }


# FastAPI integration middleware
class PerformanceMonitoringMiddleware:
    """
    Middleware for automatic performance monitoring in FastAPI.

    Example:
        from fastapi import FastAPI
        app = FastAPI()
        app.add_middleware(PerformanceMonitoringMiddleware)
    """

    def __init__(self, app):
        self.app = app
        self.tracker = PerformanceTracker()

    async def __call__(self, request, call_next):
        start_time = time.perf_counter()
        error = None
        status_code = 200

        # Get request size
        request_size = int(request.headers.get('content-length', 0))

        # Get user ID if available
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = getattr(request.state.user, 'id', None)

        try:
            response = await call_next(request)
            status_code = response.status_code

            # Get response size
            response_size = int(response.headers.get('content-length', 0))

            return response
        except Exception as e:
            error = str(e)
            status_code = 500
            raise
        finally:
            response_time_ms = (time.perf_counter() - start_time) * 1000

            self.tracker.track_endpoint(
                endpoint=str(request.url.path),
                method=request.method,
                response_time_ms=response_time_ms,
                status_code=status_code,
                request_size=request_size,
                response_size=response_size if 'response_size' in locals() else None,
                user_id=user_id,
                error=error
            )