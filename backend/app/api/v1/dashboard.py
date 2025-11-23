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

from datetime import date, datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_, or_, Date
from sqlalchemy.orm import Session

from app.api import deps
from app.models import (
    Lot,
    Serial,
    ProcessData,
    Process,
    User,
    LotStatus,
    SerialStatus,
    ProcessResult
)
from app.models.wip_item import WIPItem, WIPStatus


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

    Example Response:
        {
            "date": "2025-01-18",
            "total_started": 150,
            "total_completed": 120,
            "total_defective": 5,
            "defect_rate": 4.2,
            "lots": [
                {
                    "lot_number": "WF-KR-251118D-001",
                    "status": "IN_PROGRESS",
                    "target_quantity": 100,
                    "completed_count": 80,
                    "progress_percentage": 80.0
                }
            ],
            "process_wip": {
                "PROC-001": 5,
                "PROC-002": 10,
                ...
            }
        }
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

    try:
        # Total started (WIP items created today)
        start_of_day = datetime.combine(target_date_obj, datetime.min.time())
        end_of_day = datetime.combine(target_date_obj, datetime.max.time())
        total_started = db.query(func.count(WIPItem.id)).filter(
            WIPItem.created_at.between(start_of_day, end_of_day)
        ).scalar() or 0

        # Total in progress (WIP items currently being processed)
        total_in_progress = db.query(func.count(WIPItem.id)).filter(
            WIPItem.status == WIPStatus.IN_PROGRESS
        ).scalar() or 0

        # Total completed (WIP items completed today - all processes 1-6 PASS)
        total_completed = db.query(func.count(WIPItem.id)).filter(
            and_(
                WIPItem.completed_at.between(start_of_day, end_of_day),
                WIPItem.status == WIPStatus.COMPLETED
            )
        ).scalar() or 0

        # Total failed (WIP items failed today)
        total_failed = db.query(func.count(WIPItem.id)).filter(
            and_(
                WIPItem.updated_at.between(start_of_day, end_of_day),
                WIPItem.status == WIPStatus.FAILED
            )
        ).scalar() or 0

        # Calculate defect rate based on WIP
        total_finished = total_completed + total_failed
        defect_rate = (total_failed / total_finished * 100) if total_finished > 0 else 0

        # Get recent LOTs (all statuses)
        active_lots = (
            db.query(Lot)
            .order_by(Lot.created_at.desc())
            .limit(10)
            .all()
        )

        lots_summary = []
        for lot in active_lots:
            # Count WIP items for this lot
            wip_started = db.query(func.count(WIPItem.id)).filter(
                WIPItem.lot_id == lot.id
            ).scalar() or 0

            wip_completed = db.query(func.count(WIPItem.id)).filter(
                and_(
                    WIPItem.lot_id == lot.id,
                    WIPItem.status.in_([WIPStatus.COMPLETED, WIPStatus.CONVERTED])
                )
            ).scalar() or 0

            wip_failed = db.query(func.count(WIPItem.id)).filter(
                and_(
                    WIPItem.lot_id == lot.id,
                    WIPItem.status == WIPStatus.FAILED
                )
            ).scalar() or 0

            wip_in_progress = db.query(func.count(WIPItem.id)).filter(
                and_(
                    WIPItem.lot_id == lot.id,
                    WIPItem.status == WIPStatus.IN_PROGRESS
                )
            ).scalar() or 0

            progress = (wip_completed / lot.target_quantity * 100) if lot.target_quantity > 0 else 0

            lots_summary.append({
                "lot_number": lot.lot_number,
                "product_model_name": lot.product_model.model_name if lot.product_model else "Unknown",
                "status": lot.status,
                "target_quantity": lot.target_quantity,
                "started_count": wip_started,
                "in_progress_count": wip_in_progress,
                "completed_count": wip_completed,
                "defective_count": wip_failed,
                "progress": round(progress, 1),
                "created_at": lot.created_at.isoformat() if lot.created_at else None
            })

        # Get process WIP (Work In Progress) - count WIP items at each process
        process_wip = []
        processes = db.query(Process).filter(Process.is_active == True).order_by(Process.sort_order).all()

        for process in processes:
            # Count WIP items currently at this process
            wip_count = db.query(func.count(WIPItem.id)).filter(
                and_(
                    WIPItem.current_process_id == process.id,
                    WIPItem.status == WIPStatus.IN_PROGRESS
                )
            ).scalar() or 0

            process_wip.append({
                "process_name": process.process_name_ko,
                "wip_count": wip_count
            })

        return {
            "date": target_date_obj.isoformat(),
            "total_started": total_started,
            "total_in_progress": total_in_progress,
            "total_completed": total_completed,
            "total_defective": total_failed,
            "defect_rate": round(defect_rate, 2),
            "lots": lots_summary,
            "process_wip": process_wip
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_dashboard_summary: {str(e)}", exc_info=True)
        raise e


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

    Example Response:
        {
            "lots": [
                {
                    "lot_number": "WF-KR-251118D-001",
                    "product_model": "WF-A01",
                    "status": "IN_PROGRESS",
                    "production_date": "2025-01-18",
                    "target_quantity": 100,
                    "actual_quantity": 100,
                    "passed_quantity": 80,
                    "failed_quantity": 5,
                    "progress_percentage": 85.0,
                    "created_at": "2025-01-18T08:00:00Z"
                }
            ],
            "total": 15
        }
    """
    # Build query
    query = db.query(Lot)

    if status:
        query = query.filter(Lot.status == status)
    else:
        # Default: active LOTs + recently closed (last 7 days)
        recent_date = date.today() - timedelta(days=7)
        query = query.filter(
            or_(
                Lot.status.in_([LotStatus.CREATED, LotStatus.IN_PROGRESS]),
                and_(
                    Lot.status == LotStatus.CLOSED,
                    func.date(Lot.closed_at) >= recent_date
                )
            )
        )

    # Get total count before limit
    total = query.count()

    # Apply ordering and limit
    lots = query.order_by(Lot.created_at.desc()).limit(limit).all()

    # Build response
    lots_data = []
    for lot in lots:
        completed = lot.passed_quantity + lot.failed_quantity
        progress = (completed / lot.target_quantity * 100) if lot.target_quantity > 0 else 0

        lots_data.append({
            "lot_number": lot.lot_number,
            "product_model": lot.product_model.model_code if lot.product_model else None,
            "status": lot.status,
            "production_date": lot.production_date.isoformat() if lot.production_date else None,
            "target_quantity": lot.target_quantity,
            "actual_quantity": lot.actual_quantity,
            "passed_quantity": lot.passed_quantity,
            "failed_quantity": lot.failed_quantity,
            "progress_percentage": round(progress, 1),
            "created_at": lot.created_at.isoformat() if lot.created_at else None
        })

    return {
        "lots": lots_data,
        "total": total
    }


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

    Example Response:
        {
            "timestamp": "2025-01-18T10:30:00Z",
            "processes": [
                {
                    "process_number": 1,
                    "process_code": "PROC-001",
                    "process_name": "레이저 마킹",
                    "wip_count": 5,
                    "average_cycle_time_seconds": 60
                },
                {
                    "process_number": 2,
                    "process_code": "PROC-002",
                    "process_name": "LMA 조립",
                    "wip_count": 45,
                    "average_cycle_time_seconds": 3600
                }
            ],
            "total_wip": 120,
            "bottleneck_process": "PROC-002"
        }
    """
    processes = (
        db.query(Process)
        .filter(Process.is_active == True)
        .order_by(Process.process_number)
        .all()
    )

    # Import WIPItem for WIP-based metrics
    # from app.models.wip_item import WIPItem, WIPStatus

    process_wip_data = []
    total_wip = 0
    max_wip = 0
    bottleneck_process = None

    for process in processes:
        # Count WIP items currently at this process
        wip_count = db.query(func.count(WIPItem.id)).filter(
            and_(
                WIPItem.current_process_id == process.id,
                WIPItem.status == WIPStatus.IN_PROGRESS
            )
        ).scalar() or 0

        # Calculate average cycle time from recent completed processes
        recent_date = date.today() - timedelta(days=7)
        avg_cycle_time = db.query(
            func.avg(ProcessData.duration_seconds)
        ).filter(
            and_(
                ProcessData.process_id == process.id,
                ProcessData.completed_at.isnot(None),
                ProcessData.duration_seconds.isnot(None),
                func.date(ProcessData.completed_at) >= recent_date
            )
        ).scalar() or 0

        process_wip_data.append({
            "process_number": process.process_number,
            "process_code": process.process_code,
            "process_name": process.process_name_en,
            "wip_count": wip_count,
            "average_cycle_time_seconds": round(float(avg_cycle_time), 1) if avg_cycle_time else 0
        })

        total_wip += wip_count

        # Track bottleneck (highest WIP)
        if wip_count > max_wip:
            max_wip = wip_count
            bottleneck_process = process.process_code

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "processes": process_wip_data,
        "total_wip": total_wip,
        "bottleneck_process": bottleneck_process
    }
