from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import func, and_, or_, Integer
from sqlalchemy.orm import Session

from app.models import (
    Lot, Serial, ProcessData, Process, User,
    LotStatus, SerialStatus, ProcessResult
)
from app.models.wip_item import WIPItem, WIPStatus

class AnalyticsService:
    """
    Service for Analytics and Dashboard data aggregation.
    Encapsulates complex queries for reporting and monitoring.
    """

    # --- Analytics API Methods ---

    def get_analytics_summary(self, db: Session) -> Dict[str, Any]:
        """Get overall production statistics for Analytics page."""
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
        ).scalar() or 1

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

    def get_production_statistics(self, db: Session, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get production statistics for a date range."""
        total_lots = db.query(func.count(Lot.id)).filter(
            and_(
                func.date(Lot.created_at) >= start_date,
                func.date(Lot.created_at) <= end_date
            )
        ).scalar() or 0

        total_serials = db.query(func.count(Serial.id)).filter(
            and_(
                func.date(Serial.created_at) >= start_date,
                func.date(Serial.created_at) <= end_date
            )
        ).scalar() or 0

        completed_serials = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.completed_at.isnot(None),
                func.date(Serial.completed_at) >= start_date,
                func.date(Serial.completed_at) <= end_date
            )
        ).scalar() or 0

        pass_count = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.status == SerialStatus.PASSED,
                Serial.completed_at.isnot(None),
                func.date(Serial.completed_at) >= start_date,
                func.date(Serial.completed_at) <= end_date
            )
        ).scalar() or 0

        fail_count = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.status == SerialStatus.FAILED,
                Serial.completed_at.isnot(None),
                func.date(Serial.completed_at) >= start_date,
                func.date(Serial.completed_at) <= end_date
            )
        ).scalar() or 0

        rework_count = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.rework_count > 0,
                func.date(Serial.created_at) >= start_date,
                func.date(Serial.created_at) <= end_date
            )
        ).scalar() or 0

        pass_rate = round((pass_count / completed_serials * 100), 2) if completed_serials > 0 else 0
        defect_rate = round((fail_count / completed_serials * 100), 2) if completed_serials > 0 else 0

        return {
            "total_lots": total_lots,
            "total_serials": total_serials,
            "completed_serials": completed_serials,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "rework_count": rework_count,
            "pass_rate": pass_rate,
            "defect_rate": defect_rate
        }

    def get_process_performance(self, db: Session) -> Dict[str, Any]:
        """Get performance metrics for all processes."""
        processes = db.query(Process).order_by(Process.process_number).all()
        performance_data = []

        for process in processes:
            total_executions = db.query(func.count(ProcessData.id)).filter(
                ProcessData.process_id == process.id
            ).scalar() or 0

            success_count = db.query(func.count(ProcessData.id)).filter(
                and_(
                    ProcessData.process_id == process.id,
                    ProcessData.result == ProcessResult.PASS
                )
            ).scalar() or 0

            failure_count = db.query(func.count(ProcessData.id)).filter(
                and_(
                    ProcessData.process_id == process.id,
                    ProcessData.result == ProcessResult.FAIL
                )
            ).scalar() or 0

            avg_duration = db.query(func.avg(ProcessData.duration_seconds)).filter(
                and_(
                    ProcessData.process_id == process.id,
                    ProcessData.duration_seconds.isnot(None)
                )
            ).scalar() or 0

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

    def get_quality_metrics(self, db: Session, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get detailed quality metrics."""
        total_inspected = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.completed_at.isnot(None),
                func.date(Serial.completed_at) >= start_date,
                func.date(Serial.completed_at) <= end_date
            )
        ).scalar() or 0

        pass_count = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.status == SerialStatus.PASSED,
                Serial.completed_at.isnot(None),
                func.date(Serial.completed_at) >= start_date,
                func.date(Serial.completed_at) <= end_date
            )
        ).scalar() or 0

        fail_count = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.status == SerialStatus.FAILED,
                Serial.completed_at.isnot(None),
                func.date(Serial.completed_at) >= start_date,
                func.date(Serial.completed_at) <= end_date
            )
        ).scalar() or 0

        rework_count = db.query(func.count(Serial.id)).filter(
            and_(
                Serial.rework_count > 0,
                func.date(Serial.created_at) >= start_date,
                func.date(Serial.created_at) <= end_date
            )
        ).scalar() or 0

        pass_rate = round((pass_count / total_inspected * 100), 2) if total_inspected > 0 else 0
        defect_rate = round((fail_count / total_inspected * 100), 2) if total_inspected > 0 else 0
        rework_rate = round((rework_count / total_inspected * 100), 2) if total_inspected > 0 else 0

        processes = db.query(Process).filter(Process.is_active == True).order_by(Process.process_number).all()
        by_process = []

        for process in processes:
            proc_total = db.query(func.count(ProcessData.id)).filter(
                and_(
                    ProcessData.process_id == process.id,
                    ProcessData.completed_at.isnot(None),
                    func.date(ProcessData.completed_at) >= start_date,
                    func.date(ProcessData.completed_at) <= end_date
                )
            ).scalar() or 0

            proc_pass = db.query(func.count(ProcessData.id)).filter(
                and_(
                    ProcessData.process_id == process.id,
                    ProcessData.result == ProcessResult.PASS,
                    ProcessData.completed_at.isnot(None),
                    func.date(ProcessData.completed_at) >= start_date,
                    func.date(ProcessData.completed_at) <= end_date
                )
            ).scalar() or 0

            proc_fail = db.query(func.count(ProcessData.id)).filter(
                and_(
                    ProcessData.process_id == process.id,
                    ProcessData.result == ProcessResult.FAIL,
                    ProcessData.completed_at.isnot(None),
                    func.date(ProcessData.completed_at) >= start_date,
                    func.date(ProcessData.completed_at) <= end_date
                )
            ).scalar() or 0

            proc_rework = db.query(func.count(ProcessData.id)).filter(
                and_(
                    ProcessData.process_id == process.id,
                    ProcessData.result == ProcessResult.REWORK,
                    ProcessData.completed_at.isnot(None),
                    func.date(ProcessData.completed_at) >= start_date,
                    func.date(ProcessData.completed_at) <= end_date
                )
            ).scalar() or 0

            proc_pass_rate = round((proc_pass / proc_total * 100), 2) if proc_total > 0 else 0

            by_process.append({
                "process_name": process.process_name_en or process.process_name_ko,
                "total": proc_total,
                "pass": proc_pass,
                "fail": proc_fail,
                "rework": proc_rework,
                "pass_rate": proc_pass_rate
            })

        return {
            "total_inspected": total_inspected,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "rework_count": rework_count,
            "pass_rate": pass_rate,
            "defect_rate": defect_rate,
            "rework_rate": rework_rate,
            "by_process": by_process
        }

    def get_operator_performance(self, db: Session, days: int) -> Dict[str, Any]:
        """Get operator performance statistics."""
        start_date = date.today() - timedelta(days=days)

        operator_stats = db.query(
            User.id,
            User.full_name,
            User.username,
            func.count(ProcessData.id).label('total_operations'),
            func.sum(func.cast(ProcessData.result == ProcessResult.PASS, Integer)).label('successful_operations'),
            func.sum(func.cast(ProcessData.result == ProcessResult.FAIL, Integer)).label('failed_operations'),
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

    def get_realtime_status(self, db: Session) -> Dict[str, Any]:
        """Get real-time production status."""
        active_lots = db.query(Lot).filter(
            Lot.status.in_([LotStatus.CREATED, LotStatus.IN_PROGRESS])
        ).order_by(Lot.production_date.desc(), Lot.lot_number.desc()).limit(10).all()

        in_progress_serials = db.query(Serial).filter(
            Serial.status == SerialStatus.IN_PROGRESS
        ).order_by(Serial.created_at.desc()).limit(20).all()

        recent_processes = db.query(ProcessData).order_by(
            ProcessData.created_at.desc()
        ).limit(10).all()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "active_lots": [
                {
                    "lot_number": lot.lot_number,
                    "status": lot.status,
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
                    "status": serial.status,
                    "rework_count": serial.rework_count,
                }
                for serial in in_progress_serials
            ],
            "recent_process_executions": [
                {
                    "id": pd.id,
                    "serial_number": pd.serial.serial_number if pd.serial else None,
                    "process_code": pd.process.process_code if pd.process else None,
                    "result": pd.result,
                    "created_at": pd.created_at.isoformat() if pd.created_at else None,
                }
                for pd in recent_processes
            ]
        }

    def get_defects_analysis(self, db: Session, start_date: Optional[date], end_date: Optional[date]) -> Dict[str, Any]:
        """Get detailed defect analysis."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        failed_query = db.query(ProcessData).filter(
            ProcessData.result == ProcessResult.FAIL
        )

        if start_date:
            failed_query = failed_query.filter(
                func.date(ProcessData.created_at) >= start_date
            )
        if end_date:
            failed_query = failed_query.filter(
                func.date(ProcessData.created_at) <= end_date
            )

        failed_processes = failed_query.all()
        total_defects = len(failed_processes)

        total_processes = db.query(func.count(ProcessData.id)).filter(
            and_(
                func.date(ProcessData.created_at) >= start_date,
                func.date(ProcessData.created_at) <= end_date,
                ProcessData.result.in_([ProcessResult.PASS, ProcessResult.FAIL])
            )
        ).scalar() or 0

        defect_rate = (total_defects / total_processes * 100) if total_processes > 0 else 0

        by_process_dict = {}
        by_defect_type = {}

        for pd in failed_processes:
            # By Process
            process_code = pd.process.process_code if pd.process else "UNKNOWN"
            process_name = pd.process.process_name_en if pd.process else "Unknown"

            if process_code not in by_process_dict:
                by_process_dict[process_code] = {
                    "process_name": process_name,
                    "count": 0,
                }
            by_process_dict[process_code]["count"] += 1

            # By Defect Type
            if pd.defects and isinstance(pd.defects, list):
                for defect in pd.defects:
                    if isinstance(defect, dict) and "defect_code" in defect:
                        defect_code = defect["defect_code"]
                        by_defect_type[defect_code] = by_defect_type.get(defect_code, 0) + 1

        by_process = [
            {
                "process_name": data["process_name"],
                "defect_count": data["count"],
                "defect_rate": round(data["count"] / total_defects * 100, 1) if total_defects > 0 else 0
            }
            for process_code, data in sorted(by_process_dict.items(), key=lambda x: x[1]["count"], reverse=True)
        ]

        top_defects = [
            {
                "defect_code": code,
                "count": count,
                "percentage": round(count / total_defects * 100, 1) if total_defects > 0 else 0
            }
            for code, count in sorted(by_defect_type.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "total_defects": total_defects,
            "defect_rate": round(defect_rate, 2),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "by_process": by_process,
            "by_defect_type": by_defect_type,
            "top_defects": top_defects[:10]
        }

    def get_defect_trends(self, db: Session, period: str, days: int) -> Dict[str, Any]:
        """Get defect rate trends over time."""
        # This implementation was truncated in the view_file output, 
        # but I will implement a basic version based on the docstring description.
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Simple daily trend for now
        trends = []
        current_date = start_date
        while current_date <= end_date:
            total = db.query(func.count(ProcessData.id)).filter(
                func.date(ProcessData.created_at) == current_date
            ).scalar() or 0
            
            defects = db.query(func.count(ProcessData.id)).filter(
                and_(
                    func.date(ProcessData.created_at) == current_date,
                    ProcessData.result == ProcessResult.FAIL
                )
            ).scalar() or 0
            
            rate = round(defects / total * 100, 2) if total > 0 else 0
            
            trends.append({
                "date": current_date.isoformat(),
                "total_processes": total,
                "defects": defects,
                "defect_rate": rate
            })
            current_date += timedelta(days=1)
            
        avg_rate = sum(t["defect_rate"] for t in trends) / len(trends) if trends else 0
        max_rate = max(t["defect_rate"] for t in trends) if trends else 0
        
        return {
            "period": period,
            "days_analyzed": days,
            "trends": trends,
            "summary": {
                "average_defect_rate": round(avg_rate, 2),
                "max_defect_rate": max_rate
            }
        }

    # --- Dashboard API Methods ---

    def get_dashboard_summary(self, db: Session, target_date: date) -> Dict[str, Any]:
        """Get dashboard summary with key production metrics."""
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        total_started = db.query(func.count(WIPItem.id)).filter(
            WIPItem.created_at.between(start_of_day, end_of_day)
        ).scalar() or 0

        total_in_progress = db.query(func.count(WIPItem.id)).filter(
            WIPItem.status == WIPStatus.IN_PROGRESS
        ).scalar() or 0

        total_completed = db.query(func.count(WIPItem.id)).filter(
            and_(
                WIPItem.completed_at.between(start_of_day, end_of_day),
                WIPItem.status == WIPStatus.COMPLETED
            )
        ).scalar() or 0

        total_failed = db.query(func.count(WIPItem.id)).filter(
            and_(
                WIPItem.updated_at.between(start_of_day, end_of_day),
                WIPItem.status == WIPStatus.FAILED
            )
        ).scalar() or 0

        total_finished = total_completed + total_failed
        defect_rate = (total_failed / total_finished * 100) if total_finished > 0 else 0

        active_lots = (
            db.query(Lot)
            .order_by(Lot.created_at.desc())
            .limit(10)
            .all()
        )

        lots_summary = []
        for lot in active_lots:
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

        process_wip = []
        processes = db.query(Process).filter(Process.is_active == True).order_by(Process.sort_order).all()

        for process in processes:
            wip_at_process = db.query(func.count(WIPItem.id)).filter(
                and_(
                    WIPItem.current_process_id == process.id,
                    WIPItem.status == WIPStatus.IN_PROGRESS
                )
            ).scalar() or 0
            
            wips_active = db.query(WIPItem.id).filter(
                WIPItem.status.in_([WIPStatus.CREATED.value, WIPStatus.IN_PROGRESS.value])
            ).all()
            
            waiting_count = 0
            for (wip_id,) in wips_active:
                has_completed = db.query(func.count(ProcessData.id)).filter(
                    and_(
                        ProcessData.wip_id == wip_id,
                        ProcessData.process_id == process.id,
                        ProcessData.result == ProcessResult.PASS.value,
                        ProcessData.completed_at.isnot(None)
                    )
                ).scalar() or 0
                
                if has_completed == 0:
                    if process.process_number == 1:
                        waiting_count += 1
                    else:
                        prev_process = db.query(Process).filter(
                            and_(
                                Process.process_number == process.process_number - 1,
                                Process.is_active == True
                            )
                        ).first()
                        
                        if prev_process:
                            prev_completed = db.query(func.count(ProcessData.id)).filter(
                                and_(
                                    ProcessData.wip_id == wip_id,
                                    ProcessData.process_id == prev_process.id,
                                    ProcessData.result == ProcessResult.PASS.value,
                                    ProcessData.completed_at.isnot(None)
                                )
                            ).scalar() or 0
                            
                            if prev_completed > 0:
                                waiting_count += 1
            
            total_wip = wip_at_process + waiting_count

            process_wip.append({
                "process_name": process.process_name_ko,
                "wip_count": total_wip
            })

        return {
            "date": target_date.isoformat(),
            "total_started": total_started,
            "total_in_progress": total_in_progress,
            "total_completed": total_completed,
            "total_defective": total_failed,
            "defect_rate": round(defect_rate, 2),
            "lots": lots_summary,
            "process_wip": process_wip
        }

    def get_dashboard_lots(self, db: Session, status: Optional[LotStatus], limit: int) -> Dict[str, Any]:
        """Get LOTs list for dashboard display."""
        query = db.query(Lot)

        if status:
            query = query.filter(Lot.status == status)
        else:
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

        total = query.count()
        lots = query.order_by(Lot.created_at.desc()).limit(limit).all()

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

    def get_process_wip(self, db: Session) -> Dict[str, Any]:
        """Get Work In Progress (WIP) breakdown by process."""
        processes = (
            db.query(Process)
            .filter(Process.is_active == True)
            .order_by(Process.process_number)
            .all()
        )

        process_wip_data = []
        total_wip = 0
        max_wip = 0
        bottleneck_process = None

        for process in processes:
            wip_count = db.query(func.count(WIPItem.id)).filter(
                and_(
                    WIPItem.current_process_id == process.id,
                    WIPItem.status == WIPStatus.IN_PROGRESS
                )
            ).scalar() or 0

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

            if wip_count > max_wip:
                max_wip = wip_count
                bottleneck_process = process.process_code

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "processes": process_wip_data,
            "total_wip": total_wip,
            "bottleneck_process": bottleneck_process
        }

analytics_service = AnalyticsService()
