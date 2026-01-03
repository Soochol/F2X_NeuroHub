"""
Reports API routes for Station Service.

This module provides endpoints for generating and exporting reports.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from station_service.api.dependencies import get_database
from station_service.api.schemas.report import (
    BatchSummaryReport,
    ExportFormat,
    PeriodStatisticsReport,
    PeriodType,
    ReportType,
    StepAnalysisReport,
)
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.services.export_service import ExportService
from station_service.services.report_service import ReportService
from station_service.storage.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Reports"])


# ============================================================================
# Batch Summary Report
# ============================================================================


@router.get(
    "/batch/{batch_id}",
    response_model=ApiResponse[BatchSummaryReport],
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {},
                "text/csv": {},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "application/pdf": {},
            },
            "description": "Batch summary report",
        },
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get batch summary report",
    description="""
    Generate a summary report for a specific batch.

    Includes:
    - Overall statistics (total executions, pass rate, duration)
    - Per-step statistics (pass rate, duration min/max/avg)
    - Time range of executions

    Supports export to JSON, CSV, Excel, or PDF formats.
    """,
)
async def get_batch_summary_report(
    batch_id: str,
    batch_name: Optional[str] = Query(None, description="Batch display name"),
    format: ExportFormat = Query(ExportFormat.JSON, description="Export format"),
    database: Database = Depends(get_database),
):
    """Generate batch summary report."""
    try:
        # Generate report
        report_service = ReportService(database)
        generator = report_service.get_generator(ReportType.BATCH_SUMMARY)
        report = await generator.generate(batch_id=batch_id, batch_name=batch_name)

        # Check if batch has data
        if report.total_executions == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No execution data found for batch: {batch_id}",
            )

        # Return JSON or export
        if format == ExportFormat.JSON:
            return ApiResponse(success=True, data=report)
        else:
            export_service = ExportService()
            exporter = export_service.get_exporter(format)
            filename = f"batch_summary_{batch_id}_{datetime.now().strftime('%Y%m%d')}"
            return exporter.export(report, filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to generate batch summary report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


# ============================================================================
# Period Statistics Report
# ============================================================================


@router.get(
    "/period",
    response_model=ApiResponse[PeriodStatisticsReport],
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {},
                "text/csv": {},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "application/pdf": {},
            },
            "description": "Period statistics report",
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get period statistics report",
    description="""
    Generate statistics report grouped by time period.

    Includes:
    - Per-period statistics (daily/weekly/monthly)
    - Trend analysis (increasing/decreasing/stable)
    - Overall pass rate across periods

    Supports export to JSON, CSV, Excel, or PDF formats.
    """,
)
async def get_period_statistics_report(
    period: PeriodType = Query(..., description="Period granularity (daily, weekly, monthly)"),
    from_date: datetime = Query(..., alias="from", description="Start date"),
    to_date: datetime = Query(..., alias="to", description="End date"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    format: ExportFormat = Query(ExportFormat.JSON, description="Export format"),
    database: Database = Depends(get_database),
):
    """Generate period statistics report."""
    try:
        # Validate date range
        if from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_date must be before to_date",
            )

        # Generate report
        report_service = ReportService(database)
        generator = report_service.get_generator(ReportType.PERIOD_STATS)
        report = await generator.generate(
            period_type=period,
            from_date=from_date,
            to_date=to_date,
            batch_id=batch_id,
        )

        # Return JSON or export
        if format == ExportFormat.JSON:
            return ApiResponse(success=True, data=report)
        else:
            export_service = ExportService()
            exporter = export_service.get_exporter(format)
            filename = f"period_stats_{period.value}_{datetime.now().strftime('%Y%m%d')}"
            return exporter.export(report, filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to generate period statistics report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


# ============================================================================
# Step Analysis Report
# ============================================================================


@router.get(
    "/step-analysis",
    response_model=ApiResponse[StepAnalysisReport],
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {},
                "text/csv": {},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "application/pdf": {},
            },
            "description": "Step analysis report",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get step analysis report",
    description="""
    Generate step-level analysis report.

    Includes:
    - Per-step failure rate (sorted by highest failure rate)
    - Duration statistics (avg, min, max, P50, P95)
    - Top failure reasons for each step
    - Identification of most problematic and slowest steps

    Supports export to JSON, CSV, Excel, or PDF formats.
    """,
)
async def get_step_analysis_report(
    from_date: Optional[datetime] = Query(None, alias="from", description="Start date filter"),
    to_date: Optional[datetime] = Query(None, alias="to", description="End date filter"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    step_name: Optional[str] = Query(None, description="Filter by step name"),
    format: ExportFormat = Query(ExportFormat.JSON, description="Export format"),
    database: Database = Depends(get_database),
):
    """Generate step analysis report."""
    try:
        # Generate report
        report_service = ReportService(database)
        generator = report_service.get_generator(ReportType.STEP_ANALYSIS)
        report = await generator.generate(
            from_date=from_date,
            to_date=to_date,
            batch_id=batch_id,
            step_name=step_name,
        )

        # Return JSON or export
        if format == ExportFormat.JSON:
            return ApiResponse(success=True, data=report)
        else:
            export_service = ExportService()
            exporter = export_service.get_exporter(format)
            filename = f"step_analysis_{datetime.now().strftime('%Y%m%d')}"
            return exporter.export(report, filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to generate step analysis report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


# ============================================================================
# Report Types Info
# ============================================================================


@router.get(
    "/types",
    response_model=ApiResponse[dict],
    summary="Get available report types",
    description="Returns list of available report types and export formats.",
)
async def get_report_types():
    """Get available report types and formats."""
    return ApiResponse(
        success=True,
        data={
            "report_types": [
                {
                    "id": ReportType.BATCH_SUMMARY.value,
                    "name": "Batch Summary",
                    "description": "Summary statistics for a specific batch",
                    "required_params": ["batch_id"],
                },
                {
                    "id": ReportType.PERIOD_STATS.value,
                    "name": "Period Statistics",
                    "description": "Statistics grouped by time period with trend analysis",
                    "required_params": ["period", "from", "to"],
                },
                {
                    "id": ReportType.STEP_ANALYSIS.value,
                    "name": "Step Analysis",
                    "description": "Step-level failure and performance analysis",
                    "required_params": [],
                },
            ],
            "export_formats": [
                {"id": f.value, "name": f.value.upper(), "extension": f".{f.value}"}
                for f in ExportFormat
            ],
        },
    )
