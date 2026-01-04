"""
Results API routes for Station Service.

This module provides endpoints for querying and exporting execution results.
"""

import csv
import io
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from station_service.api.dependencies import get_database
from station_service.api.schemas.responses import ApiResponse, ErrorResponse, PaginatedResponse
from station_service.api.schemas.result import ResultDetail, ResultSummary, StepResultDetail
from station_service.storage.database import Database
from station_service.storage.repositories.execution_repository import ExecutionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/results", tags=["Results"])


class ExportFormat(str, Enum):
    """Supported export formats for results."""

    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


class ResultStatistics(BaseModel):
    """Aggregate statistics for execution results."""

    total: int = Field(..., description="Total number of executions")
    passed: int = Field(..., description="Number of passed executions")
    failed: int = Field(..., description="Number of failed executions")
    pass_rate: float = Field(..., description="Pass rate percentage")
    avg_duration: float = Field(..., description="Average execution duration in seconds")


@router.get(
    "",
    response_model=PaginatedResponse[ResultSummary],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="List execution results",
    description="""
    Retrieve a paginated list of execution results.

    Supports filtering by:
    - batch_id: Filter results for a specific batch
    - status: Filter by execution status (completed, failed)
    - from/to: Filter by date range

    Results are returned in descending order by start time (newest first).
    """,
)
async def list_results(
    database: Database = Depends(get_database),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    result_status: Optional[str] = Query(None, alias="status", description="Filter by status (completed, failed)"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Filter results from this date"),
    to_date: Optional[datetime] = Query(None, alias="to", description="Filter results until this date"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> PaginatedResponse[ResultSummary]:
    """
    List execution results with optional filtering.
    """
    try:
        repo = ExecutionRepository(database)

        # Build query with filters
        query = """
            SELECT * FROM execution_results
            WHERE 1=1
        """
        count_query = "SELECT COUNT(*) FROM execution_results WHERE 1=1"
        params: List[Any] = []
        count_params: List[Any] = []

        if batch_id:
            query += " AND batch_id = ?"
            count_query += " AND batch_id = ?"
            params.append(batch_id)
            count_params.append(batch_id)

        if result_status:
            query += " AND status = ?"
            count_query += " AND status = ?"
            params.append(result_status)
            count_params.append(result_status)

        if from_date:
            query += " AND started_at >= ?"
            count_query += " AND started_at >= ?"
            params.append(from_date.isoformat())
            count_params.append(from_date.isoformat())

        if to_date:
            query += " AND started_at <= ?"
            count_query += " AND started_at <= ?"
            params.append(to_date.isoformat())
            count_params.append(to_date.isoformat())

        # Add ordering and pagination
        query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        # Execute queries
        rows = await database.fetch_all(query, params)
        total = await database.fetch_value(count_query, count_params) or 0

        # Convert to response models
        items = []
        for row in rows:
            # Parse parameters JSON if present
            parameters = {}
            if row.get("parameters_json"):
                try:
                    parameters = json.loads(row["parameters_json"])
                except json.JSONDecodeError:
                    pass

            # Parse datetime strings
            started_at = _parse_datetime(row.get("started_at"))
            completed_at = _parse_datetime(row.get("completed_at"))

            items.append(
                ResultSummary(
                    id=row["id"],
                    batch_id=row["batch_id"],
                    sequence_name=row["sequence_name"],
                    sequence_version=row["sequence_version"],
                    status=row["status"],
                    overall_pass=row.get("overall_pass", False) or False,
                    started_at=started_at,
                    completed_at=completed_at or started_at,
                    duration=float(row.get("duration") or 0),
                    synced=row.get("synced_at") is not None,
                )
            )

        return PaginatedResponse(
            success=True,
            data=items,
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.exception("Failed to list results")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list results: {str(e)}",
        )


@router.get(
    "/statistics",
    response_model=ApiResponse[ResultStatistics],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get result statistics",
    description="Get aggregate statistics for execution results.",
)
async def get_statistics(
    database: Database = Depends(get_database),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Filter results from this date"),
    to_date: Optional[datetime] = Query(None, alias="to", description="Filter results until this date"),
) -> ApiResponse[ResultStatistics]:
    """
    Get aggregate statistics for execution results.
    """
    try:
        # Build query with filters
        where_clause = "WHERE status IN ('completed', 'failed')"
        params: List[Any] = []

        if batch_id:
            where_clause += " AND batch_id = ?"
            params.append(batch_id)

        if from_date:
            where_clause += " AND started_at >= ?"
            params.append(from_date.isoformat())

        if to_date:
            where_clause += " AND started_at <= ?"
            params.append(to_date.isoformat())

        # Get total count
        total = await database.fetch_value(f"SELECT COUNT(*) FROM execution_results {where_clause}", params) or 0

        # Get passed count
        passed = (
            await database.fetch_value(
                f"SELECT COUNT(*) FROM execution_results {where_clause} AND overall_pass = 1", params
            )
            or 0
        )

        # Get failed count
        failed = total - passed

        # Calculate pass rate
        pass_rate = (passed / total * 100) if total > 0 else 0.0

        # Get average duration
        avg_duration = (
            await database.fetch_value(
                f"SELECT AVG(duration) FROM execution_results {where_clause} AND duration IS NOT NULL", params
            )
            or 0.0
        )

        stats = ResultStatistics(
            total=total,
            passed=passed,
            failed=failed,
            pass_rate=round(pass_rate, 2),
            avg_duration=round(float(avg_duration), 2),
        )

        return ApiResponse(success=True, data=stats)
    except Exception as e:
        logger.exception("Failed to get statistics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        )


@router.get(
    "/{result_id}",
    response_model=ApiResponse[ResultDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get result details",
    description="""
    Retrieve detailed information for a specific execution result.

    Returns comprehensive result information including:
    - Execution metadata (batch, sequence, timestamps)
    - Runtime parameters used
    - Detailed step-by-step results with measurements
    """,
)
async def get_result(
    database: Database = Depends(get_database),
    result_id: str = Path(..., description="Unique execution result identifier"),
) -> ApiResponse[ResultDetail]:
    """
    Get detailed information for a specific execution result.
    """
    try:
        repo = ExecutionRepository(database)

        # Get execution with steps
        execution = await repo.get_execution_with_steps(result_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Result not found: {result_id}",
            )

        # Parse datetime strings
        started_at = _parse_datetime(execution.get("started_at"))
        completed_at = _parse_datetime(execution.get("completed_at"))

        # Convert step results
        steps = []
        for step in execution.get("steps", []):
            step_started_at = _parse_datetime(step.get("started_at"))
            step_completed_at = _parse_datetime(step.get("completed_at"))

            steps.append(
                StepResultDetail(
                    name=step["step_name"],
                    order=step["step_order"],
                    status=step["status"],
                    pass_=step.get("pass_result", False) or False,
                    duration=float(step.get("duration") or 0),
                    started_at=step_started_at or started_at,
                    completed_at=step_completed_at or step_started_at or started_at,
                    result=step.get("result", {}),
                )
            )

        result_detail = ResultDetail(
            id=execution["id"],
            batch_id=execution["batch_id"],
            sequence_name=execution["sequence_name"],
            sequence_version=execution["sequence_version"],
            status=execution["status"],
            overall_pass=execution.get("overall_pass", False) or False,
            started_at=started_at,
            completed_at=completed_at or started_at,
            duration=float(execution.get("duration") or 0),
            parameters=execution.get("parameters", {}),
            steps=steps,
        )

        return ApiResponse(success=True, data=result_detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get result")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get result: {str(e)}",
        )


@router.get(
    "/{result_id}/export",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {},
                "text/csv": {},
            },
            "description": "Exported result data",
        },
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Export result",
    description="""
    Export execution result in the specified format.

    Supported formats:
    - json: Complete result data in JSON format
    - csv: Tabular step data in CSV format
    - xlsx: Excel spreadsheet
    - pdf: PDF document

    The response content type matches the requested format.
    """,
)
async def export_result(
    database: Database = Depends(get_database),
    result_id: str = Path(..., description="Unique execution result identifier"),
    format: ExportFormat = Query(ExportFormat.JSON, description="Export format"),
) -> Response:
    """
    Export execution result in the specified format.
    """
    try:
        repo = ExecutionRepository(database)

        # Get execution with steps
        execution = await repo.get_execution_with_steps(result_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Result not found: {result_id}",
            )

        if format == ExportFormat.JSON:
            return Response(
                content=json.dumps(execution, indent=2, default=str),
                media_type="application/json",
                headers={"Content-Disposition": f'attachment; filename="{result_id}.json"'},
            )
        elif format == ExportFormat.CSV:
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(
                [
                    "step_order",
                    "step_name",
                    "status",
                    "pass",
                    "duration",
                    "started_at",
                    "completed_at",
                    "result",
                ]
            )

            # Write step data
            for step in execution.get("steps", []):
                writer.writerow(
                    [
                        step.get("step_order", 0),
                        step.get("step_name", ""),
                        step.get("status", ""),
                        step.get("pass_result", False),
                        step.get("duration", 0),
                        step.get("started_at", ""),
                        step.get("completed_at", ""),
                        json.dumps(step.get("result", {})),
                    ]
                )

            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{result_id}.csv"'},
            )
        else:
            # Use ExportService for XLSX and PDF
            from station_service.api.schemas.report import ExportFormat as ReportExportFormat
            from station_service.services.export_service import ExportService

            export_service = ExportService()
            export_format = ReportExportFormat(format.value)
            exporter = export_service.get_exporter(export_format)
            return exporter.export([execution], f"result_{result_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to export result")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export result: {str(e)}",
        )


@router.delete(
    "/{result_id}",
    response_model=ApiResponse[Dict[str, bool]],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Delete result",
    description="Delete an execution result and its step results.",
)
async def delete_result(
    database: Database = Depends(get_database),
    result_id: str = Path(..., description="Unique execution result identifier"),
) -> ApiResponse[Dict[str, bool]]:
    """
    Delete an execution result.
    """
    try:
        repo = ExecutionRepository(database)

        # Check if exists
        execution = await repo.get_execution(result_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Result not found: {result_id}",
            )

        # Delete (CASCADE will remove step results)
        await repo.delete_execution(result_id)

        return ApiResponse(
            success=True,
            data={"deleted": True},
            message=f"Result {result_id} deleted successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete result")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete result: {str(e)}",
        )


def _parse_datetime(value: Any) -> datetime:
    """Parse datetime from string or return current time."""
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return datetime.now()


class BulkExportRequest(BaseModel):
    """Request body for bulk export."""

    result_ids: List[str] = Field(..., description="List of result IDs to export", min_length=1)
    format: ExportFormat = Field(ExportFormat.XLSX, description="Export format")
    include_step_details: bool = Field(True, description="Include step-level details")


@router.post(
    "/export",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {},
                "text/csv": {},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "application/pdf": {},
            },
            "description": "Exported results",
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Bulk export results",
    description="""
    Export multiple execution results in the specified format.

    Supported formats:
    - json: Complete results data in JSON format
    - csv: Tabular data in CSV format
    - xlsx: Excel spreadsheet with multiple sheets
    - pdf: PDF document with tables

    Use this endpoint when you need to export multiple selected results.
    """,
)
async def export_results_bulk(
    request: BulkExportRequest,
    database: Database = Depends(get_database),
) -> Response:
    """
    Export multiple execution results.
    """
    try:
        if not request.result_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one result ID is required",
            )

        repo = ExecutionRepository(database)

        # Get all executions with steps
        executions = await repo.get_multiple_executions_with_steps(request.result_ids)

        if not executions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No results found for the specified IDs",
            )

        # Export based on format
        if request.format == ExportFormat.JSON:
            return Response(
                content=json.dumps(executions, indent=2, default=str),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="results_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
                },
            )
        elif request.format == ExportFormat.CSV:
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow([
                "execution_id", "batch_id", "sequence_name", "sequence_version",
                "status", "overall_pass", "duration", "started_at", "completed_at",
                "step_name", "step_order", "step_status", "step_pass", "step_duration",
            ])

            # Write data
            for execution in executions:
                base_row = [
                    execution.get("id", ""),
                    execution.get("batch_id", ""),
                    execution.get("sequence_name", ""),
                    execution.get("sequence_version", ""),
                    execution.get("status", ""),
                    execution.get("overall_pass", ""),
                    execution.get("duration", ""),
                    execution.get("started_at", ""),
                    execution.get("completed_at", ""),
                ]
                if request.include_step_details and execution.get("steps"):
                    for step in execution["steps"]:
                        writer.writerow(base_row + [
                            step.get("step_name", ""),
                            step.get("step_order", ""),
                            step.get("status", ""),
                            step.get("pass_result", ""),
                            step.get("duration", ""),
                        ])
                else:
                    writer.writerow(base_row + ["", "", "", "", ""])

            content = "\ufeff" + output.getvalue()  # BOM for Excel
            return Response(
                content=content.encode("utf-8"),
                media_type="text/csv; charset=utf-8",
                headers={
                    "Content-Disposition": f'attachment; filename="results_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
                },
            )
        else:
            # Use ExportService for XLSX and PDF
            from station_service.api.schemas.report import ExportFormat as ReportExportFormat
            from station_service.services.export_service import ExportService

            export_service = ExportService()
            export_format = ReportExportFormat(request.format.value)
            exporter = export_service.get_exporter(export_format)
            filename = f"results_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return exporter.export(executions, filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to bulk export results")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export results: {str(e)}",
        )
