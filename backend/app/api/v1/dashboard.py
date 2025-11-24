"""
Dashboard API endpoints for web dashboard frontend.

Provides dashboard-specific aggregated data optimized for frontend display:
    - Dashboard summary with key metrics
    - Active and recent LOTs list
    - Process WIP (Work In Progress) tracking
    - Real-time production status

These endpoints are optimized for frequent polling (10-30 seconds) and
provide pre-aggregated data to minimize frontend computation.
"""

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User, LotStatus
from app.services.analytics_service import analytics_service


router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(deps.get_db),
    target_date: Optional[str] = Query(None, description="Target date (default: today, format: YYYY-MM-DD)"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get dashboard summary with key production metrics.

    Provides high-level overview optimized for dashboard display:
    - Today's production counts (started, completed, defective)
    - Defect rate
    - Active LOT progress
    - Process WIP breakdown

    Query Parameters:
        target_date: Date for metrics (default: today, format: YYYY-MM-DD)

    Returns:
        Dashboard summary with production KPIs
    """
    # Parse target_date string to date object
    if target_date:
        try:
            from datetime import datetime as dt
            target_date_obj = dt.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            target_date_obj = date.today()
    else:
        target_date_obj = date.today()

    return analytics_service.get_dashboard_summary(db, target_date_obj)


@router.get("/lots")
def get_dashboard_lots(
    db: Session = Depends(deps.get_db),
    status: Optional[LotStatus] = Query(None, description="Filter by LOT status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum LOTs to return"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get LOTs list for dashboard display.

    Provides list of LOTs with essential information optimized for
    dashboard cards/tables.

    Query Parameters:
        status: Filter by LOT status (default: active + recent)
        limit: Maximum number of LOTs to return (1-100)

    Returns:
        List of LOTs with progress and status information
    """
    return analytics_service.get_dashboard_lots(db, status, limit)


@router.get("/process-wip")
def get_process_wip(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get Work In Progress (WIP) breakdown by process.

    Provides count of in-progress items at each manufacturing process
    for bottleneck visualization and capacity planning.

    Returns:
        WIP count for each process with process details
    """
    return analytics_service.get_process_wip(db)


@router.get("/cycle-times")
def get_cycle_times(
    db: Session = Depends(deps.get_db),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get average cycle time by process.

    Returns:
        List of processes with their average cycle time
    """
    return analytics_service.get_process_cycle_times(db, days)
