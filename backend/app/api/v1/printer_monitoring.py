"""
Printer Monitoring API endpoints.

Provides endpoints for:
- Printer status check
- Print logs query with filters
- Print statistics and analytics
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.api import deps
from app.models import PrintLog, User
from app.models.user import UserRole
from app.models.print_log import PrintStatus
from app.services.printer_service import printer_service, PrinterService
from app.config import settings

router = APIRouter()


class PrinterSettings(BaseModel):
    """Printer settings schema."""
    ip: str = Field(..., description="Printer IP address")
    port: int = Field(..., ge=1, le=65535, description="Printer port")
    queue_name: Optional[str] = Field(None, description="Printer queue name")


class PrinterSettingsUpdate(BaseModel):
    """Printer settings update schema."""
    ip: Optional[str] = Field(None, description="Printer IP address")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Printer port")
    queue_name: Optional[str] = Field(None, description="Printer queue name")


@router.get("/status", summary="프린터 상태 확인")
def get_printer_status(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Check printer connection status.
    
    Returns:
        {
            "online": bool,
            "ip": str,
            "port": int,
            "response_time_ms": float,
            "last_check": str
        }
    """
    status = printer_service.check_printer_status()
    status["last_check"] = datetime.utcnow().isoformat()
    
    return status


@router.get("/print-logs", summary="프린트 로그 조회")
def get_print_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    label_type: Optional[str] = Query(None, description="Label type filter (WIP_LABEL, SERIAL_LABEL, LOT_LABEL)"),
    status: Optional[str] = Query(None, description="Status filter (SUCCESS, FAILED)"),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get print logs with optional filters.
    
    Query Parameters:
        - skip: Number of records to skip (pagination)
        - limit: Maximum number of records to return
        - label_type: Filter by label type
        - status: Filter by status (SUCCESS/FAILED)
        - start_date: Filter from this date
        - end_date: Filter until this date
    
    Returns:
        {
            "total": int,
            "logs": [...]
        }
    """
    # Build query
    query = db.query(PrintLog)
    
    # Apply filters
    if label_type:
        query = query.filter(PrintLog.label_type == label_type)
    
    if status:
        query = query.filter(PrintLog.status == status)
    
    if start_date:
        query = query.filter(PrintLog.created_at >= start_date)
    
    if end_date:
        # Include the entire end_date day
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(PrintLog.created_at <= end_datetime)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    logs = query.order_by(PrintLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "logs": [log.to_dict() for log in logs]
    }


@router.get("/statistics", summary="프린트 통계")
def get_print_statistics(
    start_date: Optional[date] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get print statistics.
    
    Query Parameters:
        - start_date: Start date for statistics (default: 30 days ago)
        - end_date: End date for statistics (default: today)
    
    Returns:
        {
            "total_prints": int,
            "success_count": int,
            "failed_count": int,
            "success_rate": float,
            "by_label_type": {...},
            "recent_failures": [...]
        }
    """
    # Default date range: last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Convert to datetime for query
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Base query for date range
    base_query = db.query(PrintLog).filter(
        and_(
            PrintLog.created_at >= start_datetime,
            PrintLog.created_at <= end_datetime
        )
    )
    
    # Total prints
    total_prints = base_query.count()
    
    # Success/Failed counts
    success_count = base_query.filter(PrintLog.status == PrintStatus.SUCCESS.value).count()
    failed_count = base_query.filter(PrintLog.status == PrintStatus.FAILED.value).count()
    
    # Success rate
    success_rate = round((success_count / total_prints * 100), 2) if total_prints > 0 else 0.0
    
    # By label type
    label_type_stats = db.query(
        PrintLog.label_type,
        func.count(PrintLog.id).label('count')
    ).filter(
        and_(
            PrintLog.created_at >= start_datetime,
            PrintLog.created_at <= end_datetime
        )
    ).group_by(PrintLog.label_type).all()
    
    by_label_type = {stat.label_type: stat.count for stat in label_type_stats}
    
    # Recent failures (last 10)
    recent_failures = db.query(PrintLog).filter(
        and_(
            PrintLog.status == PrintStatus.FAILED.value,
            PrintLog.created_at >= start_datetime,
            PrintLog.created_at <= end_datetime
        )
    ).order_by(PrintLog.created_at.desc()).limit(10).all()
    
    recent_failures_list = [
        {
            "label_id": failure.label_id,
            "label_type": failure.label_type,
            "error": failure.error_message,
            "time": failure.created_at.isoformat()
        }
        for failure in recent_failures
    ]
    
    # Today's prints
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_prints = db.query(PrintLog).filter(
        PrintLog.created_at >= today_start
    ).count()
    
    return {
        "total_prints": total_prints,
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": success_rate,
        "today_prints": today_prints,
        "by_label_type": by_label_type,
        "recent_failures": recent_failures_list,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }


@router.get("/test-print", summary="테스트 프린트")
def test_print(
    label_type: str = Query("WIP_LABEL", description="Label type to test"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Test print with sample data.
    
    Query Parameters:
        - label_type: WIP_LABEL, SERIAL_LABEL, or LOT_LABEL
    
    Returns:
        Print result
    """
    test_ids = {
        "WIP_LABEL": "WIP-TEST-001",
        "SERIAL_LABEL": "TEST-SERIAL-001",
        "LOT_LABEL": "TEST-LOT-001"
    }
    
    test_id = test_ids.get(label_type, "WIP-TEST-001")
    
    if label_type == "WIP_LABEL":
        result = printer_service.print_wip_label(
            wip_id=test_id,
            db=db,
            operator_id=current_user.id
        )
    elif label_type == "SERIAL_LABEL":
        result = printer_service.print_serial_label(
            serial_number=test_id,
            db=db,
            operator_id=current_user.id
        )
    elif label_type == "LOT_LABEL":
        result = printer_service.print_lot_label(
            lot_number=test_id,
            db=db,
            operator_id=current_user.id
        )
    else:
        return {"success": False, "message": "Invalid label type"}

    return result


@router.get("/settings", summary="프린터 설정 조회", response_model=PrinterSettings)
def get_printer_settings(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get current printer settings.

    Returns:
        Current printer IP, port, and queue name
    """
    return PrinterSettings(
        ip=printer_service.printer_ip,
        port=printer_service.printer_port,
        queue_name=printer_service.queue_name
    )


@router.put("/settings", summary="프린터 설정 변경", response_model=PrinterSettings)
def update_printer_settings(
    settings_update: PrinterSettingsUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Update printer settings. Requires ADMIN role.

    Note: Changes are applied immediately but not persisted to environment.
    For permanent changes, update the PRINTER_IP and PRINTER_PORT environment variables.

    Args:
        settings_update: New printer settings (partial update supported)

    Returns:
        Updated printer settings
    """
    # Check admin permission
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permission required")

    # Update printer service settings
    global printer_service

    if settings_update.ip is not None:
        printer_service.printer_ip = settings_update.ip

    if settings_update.port is not None:
        printer_service.printer_port = settings_update.port

    if settings_update.queue_name is not None:
        printer_service.queue_name = settings_update.queue_name

    return PrinterSettings(
        ip=printer_service.printer_ip,
        port=printer_service.printer_port,
        queue_name=printer_service.queue_name
    )


@router.post("/settings/test", summary="프린터 연결 테스트")
def test_printer_connection(
    ip: str = Query(..., description="Printer IP to test"),
    port: int = Query(9100, ge=1, le=65535, description="Printer port to test"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Test connection to a printer without changing settings.

    Args:
        ip: Printer IP address to test
        port: Printer port to test

    Returns:
        Connection test result
    """
    # Create temporary printer service instance for testing
    test_printer = PrinterService(printer_ip=ip, printer_port=port)
    result = test_printer.check_printer_status()

    return {
        "success": result.get("online", False),
        "ip": ip,
        "port": port,
        "response_time_ms": result.get("response_time_ms"),
        "error": result.get("error")
    }
