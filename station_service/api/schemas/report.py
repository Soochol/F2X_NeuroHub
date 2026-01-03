"""
Report-related API schemas for Station Service.

This module defines request and response schemas for report generation and export.
All responses use camelCase field names in JSON output via APIBaseModel.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from station_service.api.schemas.base import APIBaseModel


# ============================================================================
# Enums
# ============================================================================


class ReportType(str, Enum):
    """Available report types."""

    BATCH_SUMMARY = "batch_summary"
    PERIOD_STATS = "period_stats"
    STEP_ANALYSIS = "step_analysis"


class PeriodType(str, Enum):
    """Time period granularity for statistics."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ExportFormat(str, Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


# ============================================================================
# Batch Summary Report Models
# ============================================================================


class StepSummary(APIBaseModel):
    """Summary statistics for a single step.

    Attributes:
        step_name: Name of the step
        total_runs: Total number of times this step was executed
        pass_count: Number of successful executions
        fail_count: Number of failed executions
        pass_rate: Pass rate as percentage (0-100)
        avg_duration: Average execution duration in seconds
        min_duration: Minimum execution duration in seconds
        max_duration: Maximum execution duration in seconds
    """

    step_name: str = Field(..., description="Step name")
    total_runs: int = Field(..., description="Total runs", ge=0)
    pass_count: int = Field(..., description="Passed runs", ge=0)
    fail_count: int = Field(..., description="Failed runs", ge=0)
    pass_rate: float = Field(..., description="Pass rate percentage", ge=0.0, le=100.0)
    avg_duration: float = Field(..., description="Average duration in seconds", ge=0.0)
    min_duration: float = Field(..., description="Minimum duration in seconds", ge=0.0)
    max_duration: float = Field(..., description="Maximum duration in seconds", ge=0.0)


class BatchSummaryReport(APIBaseModel):
    """Batch summary report with aggregated statistics.

    Attributes:
        batch_id: Unique batch identifier
        batch_name: Display name of the batch
        sequence_name: Name of the executed sequence
        sequence_version: Version of the executed sequence
        report_generated_at: Report generation timestamp
        total_executions: Total number of executions in this batch
        pass_count: Number of passed executions
        fail_count: Number of failed executions
        pass_rate: Overall pass rate percentage
        avg_duration: Average execution duration in seconds
        steps: Per-step summary statistics
        first_execution: Timestamp of first execution
        last_execution: Timestamp of last execution
    """

    batch_id: str = Field(..., description="Batch identifier")
    batch_name: Optional[str] = Field(None, description="Batch display name")
    sequence_name: str = Field(..., description="Sequence name")
    sequence_version: str = Field(..., description="Sequence version")
    report_generated_at: datetime = Field(..., description="Report generation time")

    # Overall statistics
    total_executions: int = Field(..., description="Total executions", ge=0)
    pass_count: int = Field(..., description="Passed executions", ge=0)
    fail_count: int = Field(..., description="Failed executions", ge=0)
    pass_rate: float = Field(..., description="Pass rate percentage", ge=0.0, le=100.0)
    avg_duration: float = Field(..., description="Average duration in seconds", ge=0.0)

    # Step-level statistics
    steps: List[StepSummary] = Field(default_factory=list, description="Step summaries")

    # Time range
    first_execution: Optional[datetime] = Field(None, description="First execution time")
    last_execution: Optional[datetime] = Field(None, description="Last execution time")


# ============================================================================
# Period Statistics Report Models
# ============================================================================


class PeriodDataPoint(APIBaseModel):
    """Data point for a single time period.

    Attributes:
        period_start: Start of the period
        period_end: End of the period
        period_label: Human-readable period label (e.g., "2025-01-01", "2025-W01")
        total: Total executions in this period
        pass_count: Passed executions
        fail_count: Failed executions
        pass_rate: Pass rate percentage
        avg_duration: Average duration in seconds
    """

    period_start: datetime = Field(..., description="Period start time")
    period_end: datetime = Field(..., description="Period end time")
    period_label: str = Field(..., description="Period label")
    total: int = Field(..., description="Total executions", ge=0)
    pass_count: int = Field(..., description="Passed executions", ge=0)
    fail_count: int = Field(..., description="Failed executions", ge=0)
    pass_rate: float = Field(..., description="Pass rate percentage", ge=0.0, le=100.0)
    avg_duration: float = Field(..., description="Average duration in seconds", ge=0.0)


class PeriodStatisticsReport(APIBaseModel):
    """Period-based statistics report with trend analysis.

    Attributes:
        period_type: Granularity of the report (daily, weekly, monthly)
        from_date: Report start date
        to_date: Report end date
        batch_id: Optional batch filter
        report_generated_at: Report generation timestamp
        total_executions: Total executions across all periods
        overall_pass_rate: Overall pass rate percentage
        data_points: Per-period statistics
        trend_direction: Trend direction (increasing, decreasing, stable)
        trend_percentage: Trend percentage change
    """

    period_type: PeriodType = Field(..., description="Period granularity")
    from_date: datetime = Field(..., description="Report start date")
    to_date: datetime = Field(..., description="Report end date")
    batch_id: Optional[str] = Field(None, description="Batch filter")
    report_generated_at: datetime = Field(..., description="Report generation time")

    # Overall statistics
    total_executions: int = Field(..., description="Total executions", ge=0)
    overall_pass_rate: float = Field(..., description="Overall pass rate", ge=0.0, le=100.0)

    # Period data
    data_points: List[PeriodDataPoint] = Field(
        default_factory=list, description="Period data points"
    )

    # Trend analysis
    trend_direction: str = Field(
        ..., description="Trend direction (increasing, decreasing, stable)"
    )
    trend_percentage: float = Field(..., description="Trend percentage change")


# ============================================================================
# Step Analysis Report Models
# ============================================================================


class FailureReason(APIBaseModel):
    """Aggregated failure reason.

    Attributes:
        error_message: Error message text
        occurrence_count: Number of occurrences
        percentage: Percentage of total failures
    """

    error_message: str = Field(..., description="Error message")
    occurrence_count: int = Field(..., description="Number of occurrences", ge=0)
    percentage: float = Field(..., description="Percentage of failures", ge=0.0, le=100.0)


class StepAnalysisItem(APIBaseModel):
    """Detailed analysis for a single step.

    Attributes:
        step_name: Name of the step
        total_runs: Total number of executions
        fail_count: Number of failures
        fail_rate: Failure rate percentage
        avg_duration: Average duration in seconds
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
        p50_duration: 50th percentile duration
        p95_duration: 95th percentile duration
        failure_reasons: Top failure reasons with counts
    """

    step_name: str = Field(..., description="Step name")
    total_runs: int = Field(..., description="Total runs", ge=0)
    fail_count: int = Field(..., description="Failed runs", ge=0)
    fail_rate: float = Field(..., description="Failure rate percentage", ge=0.0, le=100.0)
    avg_duration: float = Field(..., description="Average duration in seconds", ge=0.0)
    min_duration: float = Field(..., description="Minimum duration in seconds", ge=0.0)
    max_duration: float = Field(..., description="Maximum duration in seconds", ge=0.0)
    p50_duration: float = Field(0.0, description="50th percentile duration", ge=0.0)
    p95_duration: float = Field(0.0, description="95th percentile duration", ge=0.0)
    failure_reasons: List[FailureReason] = Field(
        default_factory=list, description="Top failure reasons"
    )


class StepAnalysisReport(APIBaseModel):
    """Step-level analysis report.

    Attributes:
        from_date: Report start date (optional)
        to_date: Report end date (optional)
        batch_id: Batch filter (optional)
        report_generated_at: Report generation timestamp
        steps: Step analysis results sorted by failure rate
        total_steps: Total number of unique steps analyzed
        most_failed_step: Name of the step with highest failure rate
        slowest_step: Name of the step with highest average duration
    """

    from_date: Optional[datetime] = Field(None, description="Report start date")
    to_date: Optional[datetime] = Field(None, description="Report end date")
    batch_id: Optional[str] = Field(None, description="Batch filter")
    report_generated_at: datetime = Field(..., description="Report generation time")

    # Step analysis results
    steps: List[StepAnalysisItem] = Field(default_factory=list, description="Step analysis")

    # Summary
    total_steps: int = Field(..., description="Total unique steps", ge=0)
    most_failed_step: Optional[str] = Field(None, description="Step with highest failure rate")
    slowest_step: Optional[str] = Field(None, description="Step with highest avg duration")


# ============================================================================
# Export Request Models
# ============================================================================


class BulkExportRequest(APIBaseModel):
    """Request for bulk export of execution results.

    Attributes:
        result_ids: List of execution result IDs to export
        format: Export format
        include_step_details: Whether to include step-level details
    """

    result_ids: List[str] = Field(..., description="Result IDs to export", min_length=1)
    format: ExportFormat = Field(ExportFormat.XLSX, description="Export format")
    include_step_details: bool = Field(True, description="Include step details")


class ReportExportRequest(APIBaseModel):
    """Request for report export.

    Attributes:
        report_type: Type of report to generate
        format: Export format
        batch_id: Batch filter (optional)
        from_date: Start date filter (optional)
        to_date: End date filter (optional)
        period_type: Period granularity for period reports
        step_name: Step filter for step analysis
    """

    report_type: ReportType = Field(..., description="Report type")
    format: ExportFormat = Field(ExportFormat.XLSX, description="Export format")
    batch_id: Optional[str] = Field(None, description="Batch filter")
    from_date: Optional[datetime] = Field(None, description="Start date filter")
    to_date: Optional[datetime] = Field(None, description="End date filter")
    period_type: Optional[PeriodType] = Field(None, description="Period granularity")
    step_name: Optional[str] = Field(None, description="Step filter")
