from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session

from app.models.process_data import ProcessData, ProcessResult
from app.models.equipment import Equipment
from app.models.user import User
from app.models.process import Process

class MetricsAggregator:
    """
    Aggregates manufacturing metrics from the database.
    Designed to be used by the Analytics API and WebSocket services.
    """

    @staticmethod
    def aggregate_process_success_rate(
        db: Session, 
        process_id: int, 
        time_window_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate success rate for a specific process over a time window.
        """
        start_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        total_runs = db.query(func.count(ProcessData.id)).filter(
            and_(
                ProcessData.process_id == process_id,
                ProcessData.created_at >= start_time
            )
        ).scalar() or 0
        
        failures = db.query(func.count(ProcessData.id)).filter(
            and_(
                ProcessData.process_id == process_id,
                ProcessData.created_at >= start_time,
                ProcessData.result == ProcessResult.FAIL
            )
        ).scalar() or 0
        
        success_rate = ((total_runs - failures) / total_runs) if total_runs > 0 else 1.0
        
        return {
            "process_id": process_id,
            "success_rate": round(success_rate, 4),
            "total_runs": total_runs,
            "failures": failures,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def aggregate_equipment_utilization(
        db: Session, 
        equipment_id: int, 
        time_window_hours: int = 8
    ) -> Dict[str, Any]:
        """
        Calculate equipment utilization based on process execution time.
        Note: This is an estimation based on process duration sums vs total time.
        """
        start_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        # Sum of duration_seconds for all process data on this equipment
        total_runtime_seconds = db.query(func.sum(ProcessData.duration_seconds)).filter(
            and_(
                ProcessData.equipment_id == equipment_id,
                ProcessData.created_at >= start_time,
                ProcessData.duration_seconds.isnot(None)
            )
        ).scalar() or 0.0
        
        # Total available time in seconds
        total_available_seconds = time_window_hours * 3600
        
        utilization_percent = (total_runtime_seconds / total_available_seconds) if total_available_seconds > 0 else 0.0
        
        # Cap at 1.0 (100%) in case of data anomalies
        utilization_percent = min(utilization_percent, 1.0)
        
        equipment = db.query(Equipment).get(equipment_id)
        equipment_status = equipment.status if equipment else "UNKNOWN"
        
        return {
            "equipment_id": equipment_id,
            "utilization_percent": round(utilization_percent, 4),
            "uptime_hours": round(total_runtime_seconds / 3600, 2),
            "status": equipment_status
        }

    @staticmethod
    def aggregate_operator_productivity(
        db: Session, 
        operator_id: int, 
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate operator metrics for the specified window.
        """
        start_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        stats = db.query(
            func.count(ProcessData.id).label('total'),
            func.avg(ProcessData.duration_seconds).label('avg_duration'),
            func.sum(func.cast(ProcessData.result == ProcessResult.PASS, int)).label('passed')
        ).filter(
            and_(
                ProcessData.operator_id == operator_id,
                ProcessData.created_at >= start_time
            )
        ).first()
        
        total = stats.total or 0
        passed = stats.passed or 0
        avg_duration = float(stats.avg_duration) if stats.avg_duration else 0.0
        
        success_rate = (passed / total) if total > 0 else 0.0
        
        return {
            "operator_id": operator_id,
            "processes_completed": total,
            "average_success_rate": round(success_rate, 4),
            "average_duration_seconds": round(avg_duration, 1)
        }

    @staticmethod
    def get_realtime_dashboard_metrics(db: Session) -> Dict[str, Any]:
        """
        Get a composite set of metrics for the main dashboard.
        """
        # 1. Overall Success Rate (Last 1 hour)
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        recent_stats = db.query(
            func.count(ProcessData.id).label('total'),
            func.sum(func.cast(ProcessData.result == ProcessResult.FAIL, int)).label('failures')
        ).filter(
            ProcessData.created_at >= one_hour_ago
        ).first()
        
        total_recent = recent_stats.total or 0
        failures_recent = recent_stats.failures or 0
        recent_success_rate = ((total_recent - failures_recent) / total_recent) if total_recent > 0 else 1.0

        # 2. Active Equipment Count
        active_equipment_count = db.query(func.count(Equipment.id)).filter(
            Equipment.status == 'IN_USE'
        ).scalar() or 0
        
        total_equipment_count = db.query(func.count(Equipment.id)).filter(
            Equipment.is_active == True
        ).scalar() or 0

        # 3. Recent Failures List
        recent_failures = db.query(ProcessData).filter(
            ProcessData.result == ProcessResult.FAIL
        ).order_by(desc(ProcessData.created_at)).limit(5).all()
        
        formatted_failures = []
        for f in recent_failures:
            process_name = f.process.process_name_en if f.process else "Unknown"
            formatted_failures.append({
                "id": f.id,
                "process": process_name,
                "time": f.created_at.isoformat(),
                "serial": f.serial.serial_number if f.serial else "N/A"
            })

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "global_success_rate_1h": round(recent_success_rate, 4),
            "active_equipment": f"{active_equipment_count}/{total_equipment_count}",
            "recent_failures": formatted_failures
        }
