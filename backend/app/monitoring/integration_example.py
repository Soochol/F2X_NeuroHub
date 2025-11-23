"""
Integration Example for Performance Monitoring System

This module demonstrates how to integrate the monitoring system with your
existing FastAPI application and SQLAlchemy database operations.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app.monitoring import (
    monitor_query,
    monitor_endpoint,
    PerformanceTracker,
    QueryMonitor,
    get_query_stats,
    get_performance_summary,
    export_metrics,
)
from app.monitoring.performance_metrics import PerformanceMonitoringMiddleware
from app.monitoring.query_monitor import setup_sqlalchemy_monitoring

# Example 1: FastAPI Application Setup
def setup_monitoring(app: FastAPI, engine):
    """
    Set up comprehensive monitoring for a FastAPI application.

    Args:
        app: FastAPI application instance
        engine: SQLAlchemy engine instance
    """
    # Add performance monitoring middleware
    app.add_middleware(PerformanceMonitoringMiddleware)

    # Enable SQLAlchemy query monitoring
    setup_sqlalchemy_monitoring(engine)

    # Initialize performance tracker
    tracker = PerformanceTracker()
    tracker.start_resource_monitoring(interval_seconds=60)

    # Add monitoring endpoints
    from fastapi import APIRouter

    monitoring_router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

    @monitoring_router.get("/metrics")
    async def get_metrics():
        """Get current performance metrics."""
        return get_performance_summary()

    @monitoring_router.get("/queries")
    async def get_query_stats_endpoint():
        """Get database query statistics."""
        return get_query_stats()

    @monitoring_router.post("/export")
    async def export_metrics_endpoint():
        """Export metrics to JSON files."""
        perf_file = export_metrics()
        query_file = QueryMonitor().export_statistics()
        return {
            "performance_metrics": perf_file,
            "query_statistics": query_file
        }

    @monitoring_router.post("/reset")
    async def reset_metrics():
        """Reset all monitoring metrics."""
        QueryMonitor().reset_statistics()
        PerformanceTracker().reset_metrics()
        return {"status": "metrics reset successfully"}

    app.include_router(monitoring_router)

    return app


# Example 2: Database Query Monitoring
class UserService:
    """Example service with monitored database operations."""

    @monitor_query("get_user_by_id")
    async def get_user_by_id(self, db: Session, user_id: int):
        """Get user by ID with query monitoring."""
        from app.models import User
        return db.query(User).filter(User.id == user_id).first()

    @monitor_query("get_users_paginated")
    async def get_users(self, db: Session, skip: int = 0, limit: int = 100):
        """Get paginated users with query monitoring."""
        from app.models import User
        return db.query(User).offset(skip).limit(limit).all()

    @monitor_query("create_user")
    async def create_user(self, db: Session, user_data: dict):
        """Create a new user with query monitoring."""
        from app.models import User

        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @monitor_query("update_user")
    async def update_user(self, db: Session, user_id: int, user_data: dict):
        """Update user with query monitoring."""
        from app.models import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        for key, value in user_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user


# Example 3: Manual Performance Tracking
class ProcessService:
    """Example service with manual performance tracking."""

    def __init__(self):
        self.tracker = PerformanceTracker()
        self.query_monitor = QueryMonitor()

    async def complex_process_operation(self, db: Session, process_id: int):
        """
        Complex operation with detailed performance tracking.
        """
        start_time = time.perf_counter()

        try:
            # Track database query
            query_start = time.perf_counter()
            process = await self._get_process(db, process_id)
            query_time = (time.perf_counter() - query_start) * 1000

            self.query_monitor.track_query(
                query=f"SELECT process WHERE id={process_id}",
                execution_time_ms=query_time,
                result_count=1 if process else 0
            )

            # Simulate processing
            await self._process_data(process)

            # Track another database operation
            update_start = time.perf_counter()
            await self._update_process_status(db, process_id, "completed")
            update_time = (time.perf_counter() - update_start) * 1000

            self.tracker.track_database_operation(
                operation="UPDATE",
                table="processes",
                duration_ms=update_time,
                rows_affected=1
            )

            return {"status": "success", "process_id": process_id}

        except Exception as e:
            # Track failed operation
            self.tracker.track_database_operation(
                operation="PROCESS",
                table="processes",
                duration_ms=(time.perf_counter() - start_time) * 1000,
                error=str(e)
            )
            raise

    async def _get_process(self, db: Session, process_id: int):
        """Get process from database."""
        from app.models import Process
        return db.query(Process).filter(Process.id == process_id).first()

    async def _process_data(self, process):
        """Simulate data processing."""
        import asyncio
        await asyncio.sleep(0.1)  # Simulate processing time

    async def _update_process_status(self, db: Session, process_id: int, status: str):
        """Update process status."""
        from app.models import Process

        process = db.query(Process).filter(Process.id == process_id).first()
        if process:
            process.status = status
            db.commit()


# Example 4: API Endpoint Monitoring
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/example", tags=["example"])


@router.get("/users/{user_id}")
@monitor_endpoint("/api/v1/users/{id}")
async def get_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Get user endpoint with automatic monitoring.
    """
    # Manual tracking for more control
    tracker = PerformanceTracker()
    start_time = time.perf_counter()

    try:
        service = UserService()
        user = await service.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        response_time = (time.perf_counter() - start_time) * 1000

        # Track with additional context
        tracker.track_endpoint(
            endpoint=f"/api/v1/users/{user_id}",
            method="GET",
            response_time_ms=response_time,
            status_code=200,
            user_id=str(user_id)
        )

        return user

    except HTTPException as e:
        response_time = (time.perf_counter() - start_time) * 1000
        tracker.track_endpoint(
            endpoint=f"/api/v1/users/{user_id}",
            method="GET",
            response_time_ms=response_time,
            status_code=e.status_code,
            error=e.detail
        )
        raise


# Example 5: Batch Operation Monitoring
class BatchProcessor:
    """Example batch processor with monitoring."""

    def __init__(self):
        self.tracker = PerformanceTracker()
        self.query_monitor = QueryMonitor()

    async def process_batch(self, db: Session, batch_size: int = 100):
        """
        Process batch of items with detailed monitoring.
        """
        batch_start = time.perf_counter()
        processed = 0
        failed = 0

        try:
            # Get items to process
            query_start = time.perf_counter()
            items = await self._get_batch_items(db, batch_size)
            query_time = (time.perf_counter() - query_start) * 1000

            self.query_monitor.track_query(
                query=f"SELECT items LIMIT {batch_size}",
                execution_time_ms=query_time,
                result_count=len(items)
            )

            # Process each item
            for item in items:
                try:
                    await self._process_item(db, item)
                    processed += 1
                except Exception as e:
                    failed += 1
                    logger.error(f"Failed to process item {item.id}: {e}")

            # Track batch completion
            batch_time = (time.perf_counter() - batch_start) * 1000

            self.tracker.track_database_operation(
                operation="BATCH_PROCESS",
                table="items",
                duration_ms=batch_time,
                rows_affected=processed
            )

            # Log summary
            logger.info(f"Batch processed: {processed} successful, {failed} failed, {batch_time:.2f}ms")

            return {
                "processed": processed,
                "failed": failed,
                "duration_ms": batch_time
            }

        except Exception as e:
            batch_time = (time.perf_counter() - batch_start) * 1000
            self.tracker.track_database_operation(
                operation="BATCH_PROCESS",
                table="items",
                duration_ms=batch_time,
                rows_affected=processed,
                error=str(e)
            )
            raise

    async def _get_batch_items(self, db: Session, limit: int):
        """Get batch of items to process."""
        from app.models import Item
        return db.query(Item).filter(Item.status == "pending").limit(limit).all()

    async def _process_item(self, db: Session, item):
        """Process individual item."""
        # Simulate processing
        import asyncio
        await asyncio.sleep(0.01)

        item.status = "processed"
        db.commit()


# Example 6: Custom Metrics Collection
class CustomMetricsCollector:
    """Custom metrics collection for specific business logic."""

    def __init__(self):
        self.tracker = PerformanceTracker()

    async def collect_business_metrics(self):
        """
        Collect custom business metrics.
        """
        metrics = {
            "timestamp": time.time(),
            "active_users": await self._count_active_users(),
            "pending_orders": await self._count_pending_orders(),
            "avg_processing_time": await self._get_avg_processing_time(),
            "cache_hit_rate": await self._get_cache_hit_rate(),
        }

        # Log custom metrics
        logger.info(f"Business metrics: {metrics}")

        # You can also send these to external monitoring services
        return metrics

    async def _count_active_users(self):
        """Count active users in the system."""
        # Implementation would query your database
        return 150

    async def _count_pending_orders(self):
        """Count pending orders."""
        # Implementation would query your database
        return 25

    async def _get_avg_processing_time(self):
        """Get average processing time."""
        # Implementation would calculate from your metrics
        return 245.5

    async def _get_cache_hit_rate(self):
        """Get cache hit rate."""
        # Implementation would check your cache stats
        return 0.85


# Example 7: Health Check with Monitoring
@router.get("/health")
async def health_check():
    """
    Health check endpoint with performance metrics.
    """
    tracker = PerformanceTracker()
    query_monitor = QueryMonitor()

    # Get current metrics
    perf_summary = tracker.get_performance_summary()
    query_stats = query_monitor.get_statistics()

    # Check system health
    memory_metrics = monitor_memory()
    memory_percent = memory_metrics["system_memory_percent"]
    cpu_percent = psutil.cpu_percent(interval=1)

    # Determine health status
    status = "healthy"
    issues = []

    if memory_percent > 80:
        status = "degraded"
        issues.append(f"High memory usage: {memory_percent:.1f}%")

    if cpu_percent > 80:
        status = "degraded"
        issues.append(f"High CPU usage: {cpu_percent:.1f}%")

    error_rate = perf_summary["endpoint_metrics"]["error_rate_percent"]
    if error_rate > 5:
        status = "unhealthy"
        issues.append(f"High error rate: {error_rate:.1f}%")

    slow_query_rate = (
        query_stats["total_slow_queries"] / query_stats["total_queries"] * 100
        if query_stats["total_queries"] > 0
        else 0
    )
    if slow_query_rate > 10:
        status = "degraded"
        issues.append(f"High slow query rate: {slow_query_rate:.1f}%")

    return {
        "status": status,
        "timestamp": time.time(),
        "metrics": {
            "memory_percent": memory_percent,
            "cpu_percent": cpu_percent,
            "error_rate_percent": error_rate,
            "slow_query_rate_percent": slow_query_rate,
            "total_requests": perf_summary["endpoint_metrics"]["total_requests"],
            "total_queries": query_stats["total_queries"],
        },
        "issues": issues if issues else None,
    }


# Example 8: Monitoring Configuration
def get_monitoring_config():
    """
    Get monitoring configuration from environment.
    """
    import os

    return {
        "query_monitoring": {
            "enabled": os.getenv("ENABLE_QUERY_MONITORING", "true").lower() == "true",
            "slow_threshold_ms": float(os.getenv("SLOW_QUERY_THRESHOLD_MS", "100")),
            "max_log_size": int(os.getenv("MAX_QUERY_LOG_SIZE", "10000")),
        },
        "performance_monitoring": {
            "enabled": os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true",
            "response_time_alert_ms": float(os.getenv("RESPONSE_TIME_ALERT_MS", "1000")),
            "memory_alert_percent": float(os.getenv("MEMORY_ALERT_PERCENT", "80")),
            "cpu_alert_percent": float(os.getenv("CPU_ALERT_PERCENT", "80")),
            "error_rate_alert_percent": float(os.getenv("ERROR_RATE_ALERT_PERCENT", "5")),
        },
        "resource_monitoring": {
            "interval_seconds": int(os.getenv("RESOURCE_MONITORING_INTERVAL", "60")),
            "enabled": os.getenv("ENABLE_RESOURCE_MONITORING", "true").lower() == "true",
        },
    }


# Helper function for database session (example)
def get_db():
    """Get database session."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import required modules
import logging
import psutil

logger = logging.getLogger(__name__)