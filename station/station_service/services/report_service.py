"""
Report Service for Station Service.

Provides report generation with extensible factory pattern.
New report types can be added by creating a generator class and registering it.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from station_service.api.schemas.report import (
    BatchSummaryReport,
    FailureReason,
    PeriodDataPoint,
    PeriodStatisticsReport,
    PeriodType,
    ReportType,
    StepAnalysisItem,
    StepAnalysisReport,
    StepSummary,
)
from station_service.storage.database import Database
from station_service.storage.repositories.execution_repository import ExecutionRepository

logger = logging.getLogger(__name__)


def calculate_percentile(sorted_values: List[float], percentile: float) -> float:
    """Calculate percentile from sorted values."""
    if not sorted_values:
        return 0.0
    n = len(sorted_values)
    idx = (n - 1) * percentile / 100
    lower = int(idx)
    upper = lower + 1
    if upper >= n:
        return sorted_values[-1]
    weight = idx - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def calculate_trend(data_points: List[Dict[str, Any]]) -> tuple[str, float]:
    """
    Calculate trend direction and percentage from period data.

    Returns:
        Tuple of (direction, percentage) where direction is
        'increasing', 'decreasing', or 'stable'.
    """
    if len(data_points) < 2:
        return "stable", 0.0

    # Compare first half average with second half average
    mid = len(data_points) // 2
    first_half = data_points[:mid]
    second_half = data_points[mid:]

    first_avg = sum(d.get("pass_rate", 0) for d in first_half) / len(first_half)
    second_avg = sum(d.get("pass_rate", 0) for d in second_half) / len(second_half)

    if first_avg == 0:
        percentage = 100.0 if second_avg > 0 else 0.0
    else:
        percentage = ((second_avg - first_avg) / first_avg) * 100

    if percentage > 5:
        direction = "increasing"
    elif percentage < -5:
        direction = "decreasing"
    else:
        direction = "stable"

    return direction, round(percentage, 2)


class BaseReportGenerator(ABC):
    """Abstract base class for report generators."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._repo = ExecutionRepository(db)

    @abstractmethod
    async def generate(self, **kwargs) -> Any:
        """Generate report data."""
        pass


class BatchSummaryReportGenerator(BaseReportGenerator):
    """Generator for batch summary reports."""

    async def generate(
        self,
        batch_id: str,
        batch_name: Optional[str] = None,
    ) -> BatchSummaryReport:
        """
        Generate a batch summary report.

        Args:
            batch_id: Batch ID to report on.
            batch_name: Optional display name for the batch.

        Returns:
            BatchSummaryReport with aggregated statistics.
        """
        # Get overall batch statistics
        stats = await self._repo.get_batch_statistics(batch_id)

        if not stats:
            # Return empty report if no data
            return BatchSummaryReport(
                batch_id=batch_id,
                batch_name=batch_name,
                sequence_name="",
                sequence_version="",
                report_generated_at=datetime.now(),
                total_executions=0,
                pass_count=0,
                fail_count=0,
                pass_rate=0.0,
                avg_duration=0.0,
                steps=[],
                first_execution=None,
                last_execution=None,
            )

        total = stats["total_executions"]
        pass_count = stats["pass_count"] or 0
        fail_count = stats["fail_count"] or 0
        pass_rate = (pass_count / total * 100) if total > 0 else 0.0

        # Parse datetime strings
        first_exec = None
        last_exec = None
        if stats.get("first_execution"):
            try:
                first_exec = datetime.fromisoformat(stats["first_execution"])
            except (ValueError, TypeError):
                pass
        if stats.get("last_execution"):
            try:
                last_exec = datetime.fromisoformat(stats["last_execution"])
            except (ValueError, TypeError):
                pass

        # Get step-level statistics
        step_stats = await self._repo.get_step_statistics_by_batch(batch_id)
        steps = []
        for step in step_stats:
            step_total = step["total_runs"]
            step_pass = step["pass_count"] or 0
            step_fail = step["fail_count"] or 0
            step_pass_rate = (step_pass / step_total * 100) if step_total > 0 else 0.0

            steps.append(
                StepSummary(
                    step_name=step["step_name"],
                    total_runs=step_total,
                    pass_count=step_pass,
                    fail_count=step_fail,
                    pass_rate=round(step_pass_rate, 2),
                    avg_duration=round(step["avg_duration"] or 0, 3),
                    min_duration=round(step["min_duration"] or 0, 3),
                    max_duration=round(step["max_duration"] or 0, 3),
                )
            )

        return BatchSummaryReport(
            batch_id=batch_id,
            batch_name=batch_name,
            sequence_name=stats.get("sequence_name", ""),
            sequence_version=stats.get("sequence_version", ""),
            report_generated_at=datetime.now(),
            total_executions=total,
            pass_count=pass_count,
            fail_count=fail_count,
            pass_rate=round(pass_rate, 2),
            avg_duration=round(stats.get("avg_duration") or 0, 2),
            steps=steps,
            first_execution=first_exec,
            last_execution=last_exec,
        )


class PeriodStatisticsReportGenerator(BaseReportGenerator):
    """Generator for period-based statistics reports."""

    async def generate(
        self,
        period_type: PeriodType,
        from_date: datetime,
        to_date: datetime,
        batch_id: Optional[str] = None,
    ) -> PeriodStatisticsReport:
        """
        Generate a period statistics report.

        Args:
            period_type: Granularity (daily, weekly, monthly).
            from_date: Report start date.
            to_date: Report end date.
            batch_id: Optional batch filter.

        Returns:
            PeriodStatisticsReport with trend analysis.
        """
        # Get period statistics
        period_stats = await self._repo.get_period_statistics(
            period_type=period_type.value,
            from_date=from_date,
            to_date=to_date,
            batch_id=batch_id,
        )

        # Build data points
        data_points = []
        total_executions = 0
        total_pass = 0

        for period in period_stats:
            total = period["total"]
            pass_count = period["pass_count"] or 0
            fail_count = period["fail_count"] or 0
            pass_rate = (pass_count / total * 100) if total > 0 else 0.0

            total_executions += total
            total_pass += pass_count

            # Parse period start/end
            period_start = datetime.now()
            period_end = datetime.now()
            if period.get("period_start"):
                try:
                    period_start = datetime.fromisoformat(period["period_start"])
                except (ValueError, TypeError):
                    pass
            if period.get("period_end"):
                try:
                    period_end = datetime.fromisoformat(period["period_end"])
                except (ValueError, TypeError):
                    pass

            data_points.append(
                PeriodDataPoint(
                    period_start=period_start,
                    period_end=period_end,
                    period_label=period["period_label"],
                    total=total,
                    pass_count=pass_count,
                    fail_count=fail_count,
                    pass_rate=round(pass_rate, 2),
                    avg_duration=round(period.get("avg_duration") or 0, 2),
                )
            )

        # Calculate overall pass rate
        overall_pass_rate = (total_pass / total_executions * 100) if total_executions > 0 else 0.0

        # Calculate trend
        trend_data = [{"pass_rate": dp.pass_rate} for dp in data_points]
        trend_direction, trend_percentage = calculate_trend(trend_data)

        return PeriodStatisticsReport(
            period_type=period_type,
            from_date=from_date,
            to_date=to_date,
            batch_id=batch_id,
            report_generated_at=datetime.now(),
            total_executions=total_executions,
            overall_pass_rate=round(overall_pass_rate, 2),
            data_points=data_points,
            trend_direction=trend_direction,
            trend_percentage=trend_percentage,
        )


class StepAnalysisReportGenerator(BaseReportGenerator):
    """Generator for step-level analysis reports."""

    async def generate(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        batch_id: Optional[str] = None,
        step_name: Optional[str] = None,
    ) -> StepAnalysisReport:
        """
        Generate a step analysis report.

        Args:
            from_date: Optional start date filter.
            to_date: Optional end date filter.
            batch_id: Optional batch filter.
            step_name: Optional step filter.

        Returns:
            StepAnalysisReport with failure analysis.
        """
        # Get step analysis data
        step_data = await self._repo.get_step_analysis(
            from_date=from_date,
            to_date=to_date,
            batch_id=batch_id,
            step_name=step_name,
        )

        steps = []
        most_failed_step = None
        slowest_step = None
        max_fail_rate = -1.0
        max_avg_duration = -1.0

        for step in step_data:
            step_name_val = step["step_name"]
            total_runs = step["total_runs"]
            fail_count = step["fail_count"] or 0
            fail_rate = (fail_count / total_runs * 100) if total_runs > 0 else 0.0
            avg_duration = step.get("avg_duration") or 0

            # Track most failed and slowest
            if fail_rate > max_fail_rate:
                max_fail_rate = fail_rate
                most_failed_step = step_name_val
            if avg_duration > max_avg_duration:
                max_avg_duration = avg_duration
                slowest_step = step_name_val

            # Get percentiles
            durations = await self._repo.get_step_durations(
                step_name=step_name_val,
                from_date=from_date,
                to_date=to_date,
                batch_id=batch_id,
            )
            p50 = calculate_percentile(durations, 50)
            p95 = calculate_percentile(durations, 95)

            # Get failure reasons
            failure_reasons_data = await self._repo.get_failure_reasons_by_step(
                step_name=step_name_val,
                from_date=from_date,
                to_date=to_date,
                batch_id=batch_id,
                limit=5,
            )

            # Calculate percentages for failure reasons
            total_failures = sum(fr["occurrence_count"] for fr in failure_reasons_data)
            failure_reasons = []
            for fr in failure_reasons_data:
                pct = (fr["occurrence_count"] / total_failures * 100) if total_failures > 0 else 0.0
                failure_reasons.append(
                    FailureReason(
                        error_message=fr["error"],
                        occurrence_count=fr["occurrence_count"],
                        percentage=round(pct, 2),
                    )
                )

            steps.append(
                StepAnalysisItem(
                    step_name=step_name_val,
                    total_runs=total_runs,
                    fail_count=fail_count,
                    fail_rate=round(fail_rate, 2),
                    avg_duration=round(avg_duration, 3),
                    min_duration=round(step.get("min_duration") or 0, 3),
                    max_duration=round(step.get("max_duration") or 0, 3),
                    p50_duration=round(p50, 3),
                    p95_duration=round(p95, 3),
                    failure_reasons=failure_reasons,
                )
            )

        return StepAnalysisReport(
            from_date=from_date,
            to_date=to_date,
            batch_id=batch_id,
            report_generated_at=datetime.now(),
            steps=steps,
            total_steps=len(steps),
            most_failed_step=most_failed_step if max_fail_rate > 0 else None,
            slowest_step=slowest_step if max_avg_duration > 0 else None,
        )


class ReportService:
    """
    Report Service with factory pattern for extensibility.

    Usage:
        service = ReportService(db)
        generator = service.get_generator(ReportType.BATCH_SUMMARY)
        report = await generator.generate(batch_id="batch_1")

    Extending with new report types:
        class MyReportGenerator(BaseReportGenerator):
            async def generate(self, **kwargs) -> MyReport:
                ...

        ReportService.register_generator(ReportType.MY_TYPE, MyReportGenerator)
    """

    _generators: Dict[ReportType, Type[BaseReportGenerator]] = {
        ReportType.BATCH_SUMMARY: BatchSummaryReportGenerator,
        ReportType.PERIOD_STATS: PeriodStatisticsReportGenerator,
        ReportType.STEP_ANALYSIS: StepAnalysisReportGenerator,
    }

    def __init__(self, db: Database) -> None:
        self._db = db

    def get_generator(self, report_type: ReportType) -> BaseReportGenerator:
        """
        Get report generator for the specified type.

        Args:
            report_type: Type of report to generate.

        Returns:
            Report generator instance.

        Raises:
            ValueError: If report type is not registered.
        """
        generator_class = self._generators.get(report_type)
        if not generator_class:
            raise ValueError(f"Unknown report type: {report_type}")
        return generator_class(self._db)

    @classmethod
    def register_generator(
        cls,
        report_type: ReportType,
        generator_class: Type[BaseReportGenerator],
    ) -> None:
        """
        Register a new report generator.

        Args:
            report_type: Report type enum value.
            generator_class: Generator class to register.
        """
        cls._generators[report_type] = generator_class
        logger.info(f"Registered report generator: {report_type} -> {generator_class.__name__}")

    @classmethod
    def available_report_types(cls) -> List[ReportType]:
        """Get list of available report types."""
        return list(cls._generators.keys())
