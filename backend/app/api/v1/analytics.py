"""
Analytics API endpoints for dashboard metrics and reporting.

Provides aggregated data and statistics for:
    - Production overview (LOTs, serials, completion rates)
    - Process performance metrics
    - Quality analysis (defect rates, rework statistics)
    - Operator performance
    - Real-time status
"""

from datetime import date, datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import lot as lot_crud, serial as serial_crud, process_data as process_data_crud
from app.models import Lot, Serial, ProcessData, Process, User, LotStatus, SerialStatus, ProcessResult


router = APIRouter()


@router.get("/dashboard")
def get_dashboard_summary(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get dashboard summary with key metrics.

    Returns overall production statistics including:
    - Total LOTs (all time, today, this week)
    - Total serials (all time, today, this week)
    - Active production (in-progress LOTs and serials)
    - Quality metrics (pass rate, defect rate)
    - Process performance summary

    **Response:**
    ```json
    {
        "lots": {
            "total": 1250,
            "today": 15,
            "this_week": 87,
            "active": 8,
            "completed_today": 12
        },
        "serials": {
            "total": 45000,
            "today": 550,
            "this_week": 3200,
            "in_progress": 120,
            "passed_today": 480,
            "failed_today": 15
        },
        "quality": {
            "overall_pass_rate": 98.5,
            "today_pass_rate": 97.2,
            "defect_rate": 1.5,
            "rework_rate": 2.3
        },
        "processes": {
            "total_executions_today": 4400,
            "average_cycle_time_seconds": 165,
            "failures_today": 22
        }
    }
    ```
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # LOT statistics
    total_lots = db.query(func.count(Lot.id)).scalar()
    lots_today = db.query(func.count(Lot.id)).filter(
        func.date(Lot.created_at) == today
    ).scalar()
    lots_this_week = db.query(func.count(Lot.id)).filter(
        func.date(Lot.created_at) >= week_start
    ).scalar()
    active_lots = db.query(func.count(Lot.id)).filter(
        Lot.status.in_([LotStatus.CREATED, LotStatus.IN_PROGRESS])
    ).scalar()
    completed_lots_today = db.query(func.count(Lot.id)).filter(
        and_(
            func.date(Lot.closed_at) == today,
            Lot.status == LotStatus.CLOSED
        )
    ).scalar()

    # Serial statistics
    total_serials = db.query(func.count(Serial.id)).scalar()
    serials_today = db.query(func.count(Serial.id)).filter(
        func.date(Serial.created_at) == today
    ).scalar()
    serials_this_week = db.query(func.count(Serial.id)).filter(
        func.date(Serial.created_at) >= week_start
    ).scalar()
    in_progress_serials = db.query(func.count(Serial.id)).filter(
        Serial.status == SerialStatus.IN_PROGRESS
    ).scalar()
    passed_today = db.query(func.count(Serial.id)).filter(
        and_(
            func.date(Serial.completed_at) == today,
            Serial.status == SerialStatus.PASSED
        )
    ).scalar()
    failed_today = db.query(func.count(Serial.id)).filter(
        and_(
            func.date(Serial.updated_at) == today,
            Serial.status == SerialStatus.FAILED
        )
    ).scalar()

    # Quality metrics
    total_completed = db.query(func.count(Serial.id)).filter(
        Serial.status.in_([SerialStatus.PASSED, SerialStatus.FAILED])
    ).scalar() or 1  # Avoid division by zero

    passed_total = db.query(func.count(Serial.id)).filter(
        Serial.status == SerialStatus.PASSED
    ).scalar() or 0

    overall_pass_rate = round((passed_total / total_completed) * 100, 2) if total_completed > 0 else 0

    today_completed = passed_today + failed_today
    today_pass_rate = round((passed_today / today_completed) * 100, 2) if today_completed > 0 else 0

    defect_rate = round(100 - overall_pass_rate, 2)

    rework_serials = db.query(func.count(Serial.id)).filter(
        Serial.rework_count > 0
    ).scalar() or 0
    rework_rate = round((rework_serials / total_serials) * 100, 2) if total_serials > 0 else 0

    # Process statistics
    process_executions_today = db.query(func.count(ProcessData.id)).filter(
        func.date(ProcessData.created_at) == today
    ).scalar() or 0

    avg_cycle_time = db.query(func.avg(ProcessData.duration_seconds)).filter(
        and_(
            ProcessData.duration_seconds.isnot(None),
            func.date(ProcessData.created_at) == today
        )
    ).scalar() or 0

    failures_today = db.query(func.count(ProcessData.id)).filter(
        and_(
            func.date(ProcessData.created_at) == today,
            ProcessData.result == ProcessResult.FAIL
        )
    ).scalar() or 0

    return {
        "lots": {
            "total": total_lots,
            "today": lots_today,
            "this_week": lots_this_week,
            "active": active_lots,
            "completed_today": completed_lots_today,
        },
        "serials": {
            "total": total_serials,
            "today": serials_today,
            "this_week": serials_this_week,
            "in_progress": in_progress_serials,
            "passed_today": passed_today,
            "failed_today": failed_today,
        },
        "quality": {
            "overall_pass_rate": overall_pass_rate,
            "today_pass_rate": today_pass_rate,
            "defect_rate": defect_rate,
            "rework_rate": rework_rate,
        },
        "processes": {
            "total_executions_today": process_executions_today,
            "average_cycle_time_seconds": round(avg_cycle_time, 1) if avg_cycle_time else 0,
            "failures_today": failures_today,
        }
    }


@router.get("/production-stats")
def get_production_statistics(
    start_date: Optional[date] = Query(None, description="Start date for statistics"),
    end_date: Optional[date] = Query(None, description="End date for statistics"),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get detailed production statistics for a date range.

    Query params:
        - start_date: Start of date range (default: 7 days ago)
        - end_date: End of date range (default: today)

    Returns daily production metrics for the specified period.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=7)
    if not end_date:
        end_date = date.today()

    # Daily LOT production
    lots_by_date = db.query(
        func.date(Lot.created_at).label('date'),
        func.count(Lot.id).label('count')
    ).filter(
        and_(
            func.date(Lot.created_at) >= start_date,
            func.date(Lot.created_at) <= end_date
        )
    ).group_by(
        func.date(Lot.created_at)
    ).order_by(
        func.date(Lot.created_at)
    ).all()

    # Daily serial production
    serials_by_date = db.query(
        func.date(Serial.created_at).label('date'),
        func.count(Serial.id).label('count'),
        func.sum(func.cast(Serial.status == SerialStatus.PASSED, db.Integer)).label('passed'),
        func.sum(func.cast(Serial.status == SerialStatus.FAILED, db.Integer)).label('failed')
    ).filter(
        and_(
            func.date(Serial.created_at) >= start_date,
            func.date(Serial.created_at) <= end_date
        )
    ).group_by(
        func.date(Serial.created_at)
    ).order_by(
        func.date(Serial.created_at)
    ).all()

    return {
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "lots_by_date": [
            {"date": str(row.date), "count": row.count}
            for row in lots_by_date
        ],
        "serials_by_date": [
            {
                "date": str(row.date),
                "total": row.count,
                "passed": row.passed or 0,
                "failed": row.failed or 0,
                "pass_rate": round((row.passed or 0) / row.count * 100, 2) if row.count > 0 else 0
            }
            for row in serials_by_date
        ]
    }


@router.get("/process-performance")
def get_process_performance(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get performance metrics for all 8 manufacturing processes.

    Returns statistics for each process including:
    - Total executions
    - Success rate
    - Average cycle time
    - Failure count
    """
    # Get all 8 processes
    processes = db.query(Process).order_by(Process.process_number).all()

    performance_data = []
    for process in processes:
        # Total executions
        total_executions = db.query(func.count(ProcessData.id)).filter(
            ProcessData.process_id == process.id
        ).scalar() or 0

        # Success count
        success_count = db.query(func.count(ProcessData.id)).filter(
            and_(
                ProcessData.process_id == process.id,
                ProcessData.result == ProcessResult.PASS
            )
        ).scalar() or 0

        # Failure count
        failure_count = db.query(func.count(ProcessData.id)).filter(
            and_(
                ProcessData.process_id == process.id,
                ProcessData.result == ProcessResult.FAIL
            )
        ).scalar() or 0

        # Average cycle time
        avg_duration = db.query(func.avg(ProcessData.duration_seconds)).filter(
            and_(
                ProcessData.process_id == process.id,
                ProcessData.duration_seconds.isnot(None)
            )
        ).scalar() or 0

        # Success rate
        success_rate = round((success_count / total_executions) * 100, 2) if total_executions > 0 else 0

        performance_data.append({
            "process_number": process.process_number,
            "process_code": process.process_code,
            "process_name_ko": process.process_name_ko,
            "process_name_en": process.process_name_en,
            "total_executions": total_executions,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_rate,
            "average_cycle_time_seconds": round(avg_duration, 1) if avg_duration else 0,
            "estimated_duration_seconds": process.estimated_duration_seconds,
        })

    return {
        "processes": performance_data,
        "summary": {
            "total_processes": len(processes),
            "total_executions": sum(p["total_executions"] for p in performance_data),
            "overall_success_rate": round(
                sum(p["success_count"] for p in performance_data) /
                sum(p["total_executions"] for p in performance_data) * 100, 2
            ) if sum(p["total_executions"] for p in performance_data) > 0 else 0
        }
    }


@router.get("/quality-metrics")
def get_quality_metrics(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get detailed quality metrics and defect analysis.

    Query params:
        - days: Number of days to analyze (default: 7, max: 90)

    Returns defect rates, rework statistics, and quality trends.
    """
    start_date = date.today() - timedelta(days=days)

    # Defect analysis by process
    defects_by_process = db.query(
        Process.process_name_ko,
        Process.process_name_en,
        func.count(ProcessData.id).label('failure_count')
    ).join(
        ProcessData, ProcessData.process_id == Process.id
    ).filter(
        and_(
            ProcessData.result == ProcessResult.FAIL,
            func.date(ProcessData.created_at) >= start_date
        )
    ).group_by(
        Process.id, Process.process_name_ko, Process.process_name_en
    ).order_by(
        func.count(ProcessData.id).desc()
    ).all()

    # Rework statistics
    rework_stats = db.query(
        Serial.rework_count,
        func.count(Serial.id).label('count')
    ).filter(
        and_(
            Serial.rework_count > 0,
            func.date(Serial.created_at) >= start_date
        )
    ).group_by(
        Serial.rework_count
    ).order_by(
        Serial.rework_count
    ).all()

    # Daily quality trend
    quality_trend = db.query(
        func.date(Serial.completed_at).label('date'),
        func.count(Serial.id).label('total'),
        func.sum(func.cast(Serial.status == SerialStatus.PASSED, db.Integer)).label('passed')
    ).filter(
        and_(
            Serial.completed_at.isnot(None),
            func.date(Serial.completed_at) >= start_date
        )
    ).group_by(
        func.date(Serial.completed_at)
    ).order_by(
        func.date(Serial.completed_at)
    ).all()

    return {
        "analysis_period_days": days,
        "defects_by_process": [
            {
                "process_name_ko": row.process_name_ko,
                "process_name_en": row.process_name_en,
                "failure_count": row.failure_count
            }
            for row in defects_by_process
        ],
        "rework_distribution": [
            {
                "rework_count": row.rework_count,
                "serial_count": row.count
            }
            for row in rework_stats
        ],
        "quality_trend": [
            {
                "date": str(row.date),
                "total_completed": row.total,
                "passed": row.passed or 0,
                "pass_rate": round((row.passed or 0) / row.total * 100, 2) if row.total > 0 else 0
            }
            for row in quality_trend
        ]
    }


@router.get("/operator-performance")
def get_operator_performance(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get operator performance statistics.

    Query params:
        - days: Number of days to analyze (default: 7, max: 90)

    Returns productivity and quality metrics per operator.
    """
    start_date = date.today() - timedelta(days=days)

    operator_stats = db.query(
        User.id,
        User.full_name,
        User.username,
        func.count(ProcessData.id).label('total_operations'),
        func.sum(func.cast(ProcessData.result == ProcessResult.PASS, db.Integer)).label('successful_operations'),
        func.sum(func.cast(ProcessData.result == ProcessResult.FAIL, db.Integer)).label('failed_operations'),
        func.avg(ProcessData.duration_seconds).label('avg_cycle_time')
    ).join(
        ProcessData, ProcessData.operator_id == User.id
    ).filter(
        func.date(ProcessData.created_at) >= start_date
    ).group_by(
        User.id, User.full_name, User.username
    ).order_by(
        func.count(ProcessData.id).desc()
    ).all()

    return {
        "analysis_period_days": days,
        "operators": [
            {
                "operator_id": row.id,
                "full_name": row.full_name,
                "username": row.username,
                "total_operations": row.total_operations,
                "successful_operations": row.successful_operations or 0,
                "failed_operations": row.failed_operations or 0,
                "success_rate": round(
                    (row.successful_operations or 0) / row.total_operations * 100, 2
                ) if row.total_operations > 0 else 0,
                "average_cycle_time_seconds": round(row.avg_cycle_time, 1) if row.avg_cycle_time else 0
            }
            for row in operator_stats
        ]
    }


@router.get("/realtime-status")
def get_realtime_status(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get real-time production status.

    Returns current status of active LOTs and in-progress serials.
    """
    # Active LOTs
    active_lots = db.query(Lot).filter(
        Lot.status.in_([LotStatus.CREATED, LotStatus.IN_PROGRESS])
    ).order_by(Lot.production_date.desc(), Lot.lot_number.desc()).limit(10).all()

    # In-progress serials
    in_progress_serials = db.query(Serial).filter(
        Serial.status == SerialStatus.IN_PROGRESS
    ).order_by(Serial.created_at.desc()).limit(20).all()

    # Latest process executions
    recent_processes = db.query(ProcessData).order_by(
        ProcessData.created_at.desc()
    ).limit(10).all()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "active_lots": [
            {
                "lot_number": lot.lot_number,
                "status": lot.status.value,
                "target_quantity": lot.target_quantity,
                "actual_quantity": lot.actual_quantity,
                "passed_quantity": lot.passed_quantity,
                "failed_quantity": lot.failed_quantity,
            }
            for lot in active_lots
        ],
        "in_progress_serials": [
            {
                "serial_number": serial.serial_number,
                "lot_number": serial.lot.lot_number if serial.lot else None,
                "status": serial.status.value,
                "rework_count": serial.rework_count,
            }
            for serial in in_progress_serials
        ],
        "recent_process_executions": [
            {
                "id": pd.id,
                "serial_number": pd.serial.serial_number if pd.serial else None,
                "process_code": pd.process.process_code if pd.process else None,
                "result": pd.result.value if pd.result else None,
                "created_at": pd.created_at.isoformat() if pd.created_at else None,
            }
            for pd in recent_processes
        ]
    }
