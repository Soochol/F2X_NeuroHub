"""
ErrorLog schemas for request/response validation.

This module defines Pydantic schemas for error log operations,
including error logging, querying, and API responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ErrorLogBase(BaseModel):
    """Base error log schema with common fields."""

    trace_id: UUID = Field(..., description="Unique trace ID for frontend-backend correlation")
    error_code: str = Field(..., min_length=1, max_length=20, description="Standardized error code (e.g., RES_001, VAL_002)")
    message: str = Field(..., min_length=1, description="Human-readable error message")
    path: Optional[str] = Field(None, max_length=500, description="API endpoint path where error occurred")
    method: Optional[str] = Field(None, max_length=10, description="HTTP method (GET, POST, PUT, DELETE, PATCH)")
    status_code: int = Field(..., ge=400, lt=600, description="HTTP status code (4xx or 5xx)")
    user_id: Optional[int] = Field(None, description="User ID who triggered the error (NULL for unauthenticated)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details in JSONB format")


class ErrorLogCreate(ErrorLogBase):
    """Schema for creating a new error log (used by middleware)."""

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error occurrence timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "error_code": "RES_002",
                "message": "Lot with ID 999 not found",
                "path": "/api/v1/lots/999",
                "method": "GET",
                "status_code": 404,
                "user_id": 5,
                "details": {
                    "resource_type": "Lot",
                    "resource_id": 999
                },
                "timestamp": "2025-11-20T10:30:00.000Z"
            }
        }
    )


class ErrorLogInDB(ErrorLogBase):
    """Schema for error log data retrieved from database."""

    id: int = Field(..., description="Error log ID")
    timestamp: datetime = Field(..., description="Error occurrence timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 123,
                "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "error_code": "RES_002",
                "message": "Lot with ID 999 not found",
                "path": "/api/v1/lots/999",
                "method": "GET",
                "status_code": 404,
                "user_id": 5,
                "details": {
                    "resource_type": "Lot",
                    "resource_id": 999
                },
                "timestamp": "2025-11-20T10:30:00.000Z"
            }
        }
    )


class ErrorLogResponse(ErrorLogInDB):
    """Schema for error log API response with optional user info."""

    username: Optional[str] = Field(None, description="Username who triggered the error")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 123,
                "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "error_code": "RES_002",
                "message": "Lot with ID 999 not found",
                "path": "/api/v1/lots/999",
                "method": "GET",
                "status_code": 404,
                "user_id": 5,
                "username": "operator01",
                "details": {
                    "resource_type": "Lot",
                    "resource_id": 999
                },
                "timestamp": "2025-11-20T10:30:00.000Z"
            }
        }
    )


class ErrorLogListResponse(BaseModel):
    """Schema for paginated error log list response."""

    items: List[ErrorLogResponse] = Field(..., description="List of error logs")
    total: int = Field(..., ge=0, description="Total number of error logs matching filters")
    skip: int = Field(..., ge=0, description="Number of records skipped")
    limit: int = Field(..., ge=1, description="Maximum number of records returned")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 123,
                        "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "error_code": "RES_002",
                        "message": "Lot with ID 999 not found",
                        "path": "/api/v1/lots/999",
                        "method": "GET",
                        "status_code": 404,
                        "user_id": 5,
                        "username": "operator01",
                        "details": None,
                        "timestamp": "2025-11-20T10:30:00.000Z"
                    }
                ],
                "total": 150,
                "skip": 0,
                "limit": 50
            }
        }
    )


class ErrorCodeCount(BaseModel):
    """Schema for error code distribution statistics."""

    error_code: str = Field(..., description="Error code")
    count: int = Field(..., ge=0, description="Number of occurrences")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "RES_002",
                "count": 45
            }
        }
    )


class HourlyErrorCount(BaseModel):
    """Schema for hourly error count statistics."""

    hour: datetime = Field(..., description="Hour timestamp")
    count: int = Field(..., ge=0, description="Number of errors in this hour")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hour": "2025-11-20T10:00:00.000Z",
                "count": 12
            }
        }
    )


class TopErrorPath(BaseModel):
    """Schema for top error-prone API endpoints."""

    path: str = Field(..., description="API endpoint path")
    method: str = Field(..., description="HTTP method")
    count: int = Field(..., ge=0, description="Number of errors")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "path": "/api/v1/lots/999",
                "method": "GET",
                "count": 25
            }
        }
    )


class ErrorLogStats(BaseModel):
    """Schema for error log statistics response."""

    total_errors: int = Field(..., ge=0, description="Total number of errors in time range")
    by_error_code: List[ErrorCodeCount] = Field(..., description="Error distribution by error code")
    by_hour: List[HourlyErrorCount] = Field(..., description="Error trend by hour")
    top_paths: List[TopErrorPath] = Field(..., description="Top error-prone API endpoints")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_errors": 150,
                "by_error_code": [
                    {"error_code": "RES_002", "count": 45},
                    {"error_code": "VAL_001", "count": 30},
                    {"error_code": "AUTH_001", "count": 25}
                ],
                "by_hour": [
                    {"hour": "2025-11-20T10:00:00.000Z", "count": 12},
                    {"hour": "2025-11-20T11:00:00.000Z", "count": 8},
                    {"hour": "2025-11-20T12:00:00.000Z", "count": 15}
                ],
                "top_paths": [
                    {"path": "/api/v1/lots/999", "method": "GET", "count": 25},
                    {"path": "/api/v1/serials/456", "method": "PUT", "count": 20},
                    {"path": "/api/v1/processes", "method": "POST", "count": 15}
                ]
            }
        }
    )


class ErrorLogFilters(BaseModel):
    """Schema for error log query filters."""

    error_code: Optional[str] = Field(None, max_length=20, description="Filter by error code")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    path: Optional[str] = Field(None, max_length=500, description="Filter by API path")
    method: Optional[str] = Field(None, max_length=10, description="Filter by HTTP method")
    min_status_code: Optional[int] = Field(None, ge=400, lt=600, description="Minimum status code")
    max_status_code: Optional[int] = Field(None, ge=400, lt=600, description="Maximum status code")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "RES_002",
                "start_date": "2025-11-20T00:00:00.000Z",
                "end_date": "2025-11-20T23:59:59.999Z",
                "user_id": 5,
                "path": "/api/v1/lots",
                "method": "GET",
                "min_status_code": 400,
                "max_status_code": 499
            }
        }
    )
