"""
Analytics API endpoints for dashboard metrics and reporting.

Provides aggregated data and statistics for:
    - Production overview (LOTs, serials, completion rates)
    - Process performance metrics
    - Quality analysis (defect rates, rework statistics)
    - Operator performance
    - Real-time status
"""

import logging
from datetime import date as date_module, datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Alias for clarity
date = date_module

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio
import json

from app.api import deps
from app.models import User
from app.services.analytics_service import analytics_service
from app.analytics.metrics_aggregator import MetricsAggregator
from app.analytics.alert_manager import AlertManager


router = APIRouter()


@router.get("/operations/metrics")
def get_operations_metrics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get real-time metrics for the Operations Dashboard.
    """
    return MetricsAggregator.get_realtime_dashboard_metrics(db)


@router.websocket("/ws/metrics/live")
async def websocket_live_metrics(
    websocket: WebSocket,
    db: Session = Depends(deps.get_db),
):
    """
    WebSocket endpoint for streaming real-time metrics.
    Updates every 5 seconds.
    """
    await websocket.accept()
    try:
        while True:
            # Fetch metrics
            # Note: In a real async app we might want to use an async DB session here
            # For now, we'll use the sync session in a blocking way (careful with blocking loop)
            # or ideally, offload to thread.
            # Since this is a simple loop, we will just call the aggregator.
            
            metrics = MetricsAggregator.get_realtime_dashboard_metrics(db)
            
            # Also check for alerts (optional, could be separate)
            # alert_manager = AlertManager(db)
            # alert_manager.check_process_failure_rate(1) # Example check
            
            await websocket.send_json(metrics)
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        logger.debug("Client disconnected from metrics websocket")
    except Exception as e:
        logger.info(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


@router.get("/dashboard")
def get_dashboard_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get dashboard summary with key metrics.

    Returns overall production statistics including:
    - Total LOTs (all time, today, this week)
    - Total serials (all time, today, this week)
    - Active production (in-progress LOTs and serials)
    - Quality metrics (pass rate, defect rate)
    - Process performance summary
    """
    return analytics_service.get_analytics_summary(db)


@router.get("/production-stats")
def get_production_statistics(
    start_date: Optional[date] = Query(None, description="Start date for statistics"),
    end_date: Optional[date] = Query(None, description="End date for statistics"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get production statistics for a date range.

    Query params:
        - start_date: Start of date range (default: 30 days ago)
        - end_date: End of date range (default: today)

    Returns aggregated production metrics including totals and rates.
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    return analytics_service.get_production_statistics(db, start_date, end_date)


@router.get("/process-performance")
def get_process_performance(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get performance metrics for all 8 manufacturing processes.

    Returns statistics for each process including:
    - Total executions
    - Success rate
    - Average cycle time
    - Failure count
    """
    return analytics_service.get_process_performance(db)


@router.get("/quality-metrics")
def get_quality_metrics(
    start_date: Optional[date] = Query(None, description="Start date for metrics"),
    end_date: Optional[date] = Query(None, description="End date for metrics"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed quality metrics for the Quality Management page.

    Query params:
        - start_date: Start date for metrics (default: 30 days ago)
        - end_date: End date for metrics (default: today)

    Returns aggregated quality metrics including pass/fail/rework counts and rates.
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    return analytics_service.get_quality_metrics(db, start_date, end_date)


@router.get("/operator-performance")
def get_operator_performance(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get operator performance statistics.

    Query params:
        - days: Number of days to analyze (default: 7, max: 90)

    Returns productivity and quality metrics per operator.
    """
    return analytics_service.get_operator_performance(db, days)


@router.get("/realtime-status")
def get_realtime_status(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get real-time production status.

    Returns current status of active LOTs and in-progress serials.
    """
    return analytics_service.get_realtime_status(db)


@router.get("/defects")
def get_defects_analysis(
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed defect analysis.

    Provides comprehensive defect statistics including:
    - Total defects count
    - Defect rate percentage
    - Breakdown by process
    - Breakdown by defect type
    - Top defect codes

    **Query Parameters:**
    - start_date: Filter defects from this date (optional)
    - end_date: Filter defects until this date (optional)
    """
    return analytics_service.get_defects_analysis(db, start_date, end_date)


@router.get("/defect-trends")
def get_defect_trends(
    db: Session = Depends(deps.get_db),
    period: str = Query("daily", description="Aggregation period: daily, weekly, monthly"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get defect rate trends over time.

    Tracks defect rates across different time periods for trend analysis.

    **Query Parameters:**
    - period: Aggregation period (daily, weekly, monthly)
    - days: Number of days to look back (1-365)
    """
    return analytics_service.get_defect_trends(db, period, days)
