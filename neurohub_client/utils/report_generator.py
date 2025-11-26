"""
Report Generator for Production Tracker App.

Generates various production reports including:
- Daily production report
- LOT progress report
- WIP status report
- Process performance report
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ReportData:
    """Base report data structure."""
    report_type: str
    generated_at: str
    generated_by: str
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None


class ReportGenerator:
    """Generate production reports."""

    def __init__(self, api_client: Any) -> None:
        """
        Initialize ReportGenerator.

        Args:
            api_client: APIClient instance
        """
        self.api_client = api_client

    def generate_daily_production_report(
        self,
        date: str,
        line_id: Optional[int] = None,
        process_id: Optional[int] = None
    ) -> ReportData:
        """
        Generate daily production report.

        Args:
            date: Date in YYYY-MM-DD format
            line_id: Optional production line filter
            process_id: Optional process filter

        Returns:
            ReportData with daily production summary
        """
        logger.info(f"Generating daily production report for {date}")

        try:
            # Fetch data from API
            params = {
                "date": date,
                "line_id": line_id,
                "process_id": process_id
            }
            params = {k: v for k, v in params.items() if v is not None}

            data = self.api_client.get("/api/v1/reports/daily-production", params=params)

            # Calculate summary
            summary = self._calculate_daily_summary(data)

            return ReportData(
                report_type="daily_production",
                generated_at=datetime.now().isoformat(),
                generated_by="system",
                date_range_start=date,
                date_range_end=date,
                filters=params,
                data=data,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Failed to generate daily production report: {e}")
            raise

    def generate_lot_progress_report(
        self,
        start_date: str,
        end_date: str,
        status: Optional[str] = None
    ) -> ReportData:
        """
        Generate LOT progress report.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            status: Optional status filter (CREATED, IN_PROGRESS, COMPLETED)

        Returns:
            ReportData with LOT progress information
        """
        logger.info(f"Generating LOT progress report: {start_date} ~ {end_date}")

        try:
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "status": status
            }
            params = {k: v for k, v in params.items() if v is not None}

            data = self.api_client.get("/api/v1/reports/lot-progress", params=params)

            # Calculate summary
            summary = self._calculate_lot_summary(data)

            return ReportData(
                report_type="lot_progress",
                generated_at=datetime.now().isoformat(),
                generated_by="system",
                date_range_start=start_date,
                date_range_end=end_date,
                filters=params,
                data=data,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Failed to generate LOT progress report: {e}")
            raise

    def generate_wip_status_report(
        self,
        process_id: Optional[int] = None,
        line_id: Optional[int] = None
    ) -> ReportData:
        """
        Generate WIP status report.

        Args:
            process_id: Optional process filter
            line_id: Optional production line filter

        Returns:
            ReportData with current WIP status
        """
        logger.info("Generating WIP status report")

        try:
            params = {
                "process_id": process_id,
                "line_id": line_id
            }
            params = {k: v for k, v in params.items() if v is not None}

            data = self.api_client.get("/api/v1/reports/wip-status", params=params)

            # Calculate summary
            summary = self._calculate_wip_summary(data)

            return ReportData(
                report_type="wip_status",
                generated_at=datetime.now().isoformat(),
                generated_by="system",
                filters=params,
                data=data,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Failed to generate WIP status report: {e}")
            raise

    def generate_process_performance_report(
        self,
        start_date: str,
        end_date: str,
        process_id: Optional[int] = None
    ) -> ReportData:
        """
        Generate process performance report.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            process_id: Optional process filter

        Returns:
            ReportData with process performance metrics
        """
        logger.info(f"Generating process performance report: {start_date} ~ {end_date}")

        try:
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "process_id": process_id
            }
            params = {k: v for k, v in params.items() if v is not None}

            data = self.api_client.get("/api/v1/reports/process-performance", params=params)

            # Calculate summary
            summary = self._calculate_performance_summary(data)

            return ReportData(
                report_type="process_performance",
                generated_at=datetime.now().isoformat(),
                generated_by="system",
                date_range_start=start_date,
                date_range_end=end_date,
                filters=params,
                data=data,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Failed to generate process performance report: {e}")
            raise

    def generate_defect_analysis_report(
        self,
        start_date: str,
        end_date: str,
        process_id: Optional[int] = None
    ) -> ReportData:
        """
        Generate defect analysis report.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            process_id: Optional process filter

        Returns:
            ReportData with defect analysis
        """
        logger.info(f"Generating defect analysis report: {start_date} ~ {end_date}")

        try:
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "process_id": process_id
            }
            params = {k: v for k, v in params.items() if v is not None}

            data = self.api_client.get("/api/v1/reports/defect-analysis", params=params)

            # Calculate summary
            summary = self._calculate_defect_summary(data)

            return ReportData(
                report_type="defect_analysis",
                generated_at=datetime.now().isoformat(),
                generated_by="system",
                date_range_start=start_date,
                date_range_end=end_date,
                filters=params,
                data=data,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Failed to generate defect analysis report: {e}")
            raise

    # Summary calculation methods

    def _calculate_daily_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate daily production summary."""
        if not data:
            return {
                "total_started": 0,
                "total_completed": 0,
                "total_pass": 0,
                "total_fail": 0,
                "pass_rate": 0.0,
                "avg_cycle_time": 0.0
            }

        total_started = len([d for d in data if d.get("status") in ["IN_PROGRESS", "COMPLETED"]])
        total_completed = len([d for d in data if d.get("status") == "COMPLETED"])
        total_pass = len([d for d in data if d.get("result") == "PASS"])
        total_fail = len([d for d in data if d.get("result") == "FAIL"])

        pass_rate = (total_pass / total_completed * 100) if total_completed > 0 else 0.0

        # Calculate average cycle time
        cycle_times = [
            d.get("cycle_time", 0)
            for d in data
            if d.get("cycle_time") is not None and d.get("status") == "COMPLETED"
        ]
        avg_cycle_time = sum(cycle_times) / len(cycle_times) if cycle_times else 0.0

        return {
            "total_started": total_started,
            "total_completed": total_completed,
            "total_pass": total_pass,
            "total_fail": total_fail,
            "pass_rate": round(pass_rate, 2),
            "avg_cycle_time": round(avg_cycle_time, 2)
        }

    def _calculate_lot_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate LOT progress summary."""
        if not data:
            return {
                "total_lots": 0,
                "completed_lots": 0,
                "in_progress_lots": 0,
                "completion_rate": 0.0
            }

        total_lots = len(data)
        completed_lots = len([d for d in data if d.get("status") == "COMPLETED"])
        in_progress_lots = len([d for d in data if d.get("status") == "IN_PROGRESS"])

        completion_rate = (completed_lots / total_lots * 100) if total_lots > 0 else 0.0

        return {
            "total_lots": total_lots,
            "completed_lots": completed_lots,
            "in_progress_lots": in_progress_lots,
            "completion_rate": round(completion_rate, 2)
        }

    def _calculate_wip_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate WIP status summary."""
        if not data:
            return {
                "total_wip": 0,
                "by_status": {},
                "by_process": {}
            }

        total_wip = len(data)

        # Group by status
        by_status = {}
        for item in data:
            status = item.get("status", "UNKNOWN")
            by_status[status] = by_status.get(status, 0) + 1

        # Group by process
        by_process = {}
        for item in data:
            process = item.get("process_name", "Unknown")
            by_process[process] = by_process.get(process, 0) + 1

        return {
            "total_wip": total_wip,
            "by_status": by_status,
            "by_process": by_process
        }

    def _calculate_performance_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate process performance summary."""
        if not data:
            return {
                "total_processed": 0,
                "avg_throughput": 0.0,
                "avg_yield": 0.0,
                "top_performers": []
            }

        total_processed = sum(d.get("total_count", 0) for d in data)
        avg_throughput = total_processed / len(data) if data else 0.0

        # Calculate average yield
        yields = [d.get("yield_rate", 0) for d in data if d.get("yield_rate") is not None]
        avg_yield = sum(yields) / len(yields) if yields else 0.0

        # Top performers (by yield rate)
        sorted_data = sorted(data, key=lambda x: x.get("yield_rate", 0), reverse=True)
        top_performers = [
            {
                "process": d.get("process_name", "Unknown"),
                "yield_rate": d.get("yield_rate", 0)
            }
            for d in sorted_data[:5]
        ]

        return {
            "total_processed": total_processed,
            "avg_throughput": round(avg_throughput, 2),
            "avg_yield": round(avg_yield, 2),
            "top_performers": top_performers
        }

    def _calculate_defect_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate defect analysis summary."""
        if not data:
            return {
                "total_defects": 0,
                "defect_rate": 0.0,
                "by_type": {},
                "top_defects": []
            }

        total_defects = sum(d.get("defect_count", 0) for d in data)
        total_inspected = sum(d.get("total_count", 0) for d in data)

        defect_rate = (total_defects / total_inspected * 100) if total_inspected > 0 else 0.0

        # Group by defect type
        by_type = {}
        for item in data:
            defect_type = item.get("defect_type", "Unknown")
            count = item.get("defect_count", 0)
            by_type[defect_type] = by_type.get(defect_type, 0) + count

        # Top defects
        top_defects = sorted(
            [{"type": k, "count": v} for k, v in by_type.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]

        return {
            "total_defects": total_defects,
            "defect_rate": round(defect_rate, 2),
            "by_type": by_type,
            "top_defects": top_defects
        }
