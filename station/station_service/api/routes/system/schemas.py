"""
Shared schemas for system API routes.

Contains Pydantic models used across multiple system route modules.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from station_service.api.schemas.base import APIBaseModel


# ============================================================================
# System Info Schemas
# ============================================================================


class SyncStatus(APIBaseModel):
    """Sync queue status response."""

    pending_count: int = Field(..., description="Number of pending sync items")
    failed_count: int = Field(..., description="Number of failed sync items")
    last_sync_at: Optional[datetime] = Field(None, description="Last successful sync timestamp")
    backend_connected: bool = Field(..., description="Whether backend is reachable")
    backend_url: str = Field(..., description="Backend URL")


class UpdateStationInfoRequest(APIBaseModel):
    """Request body for updating station information."""

    id: str = Field(..., min_length=1, max_length=100, description="Station ID")
    name: str = Field(..., min_length=1, max_length=200, description="Station name")
    description: str = Field("", max_length=500, description="Station description")


# ============================================================================
# Workflow Schemas
# ============================================================================


class WorkflowConfigResponse(APIBaseModel):
    """Workflow configuration response."""

    enabled: bool = Field(..., description="Whether workflow is enabled")
    input_mode: str = Field(..., description="WIP ID input mode: 'popup' or 'barcode'")
    auto_sequence_start: bool = Field(..., description="Auto-start sequence after barcode scan")
    require_operator_login: bool = Field(..., description="Require backend login")


class UpdateWorkflowRequest(APIBaseModel):
    """Request body for updating workflow configuration."""

    enabled: Optional[bool] = Field(None, description="Enable/disable workflow")
    input_mode: Optional[str] = Field(None, description="Input mode: 'popup' or 'barcode'")
    auto_sequence_start: Optional[bool] = Field(None, description="Auto-start sequence")
    require_operator_login: Optional[bool] = Field(None, description="Require login")


# ============================================================================
# Operator Schemas
# ============================================================================


class OperatorInfo(APIBaseModel):
    """Operator information from backend."""

    id: int = Field(..., description="Operator ID")
    username: str = Field(..., description="Operator username")
    name: str = Field("", description="Operator display name")
    role: str = Field("", description="Operator role")


class OperatorSession(APIBaseModel):
    """Current operator session state."""

    logged_in: bool = Field(..., description="Whether an operator is logged in")
    operator: Optional[OperatorInfo] = Field(None, description="Logged in operator info")
    access_token: Optional[str] = Field(None, description="JWT access token")
    logged_in_at: Optional[datetime] = Field(None, description="Login timestamp")


class OperatorLoginRequest(APIBaseModel):
    """Request body for operator login."""

    username: str = Field(..., min_length=1, description="Operator username")
    password: str = Field(..., min_length=1, description="Operator password")


# ============================================================================
# MES Schemas
# ============================================================================


class ProcessInfo(APIBaseModel):
    """Process information from backend MES."""

    id: int = Field(..., description="Process ID")
    process_number: int = Field(..., description="Process number (1-8)")
    process_code: str = Field(..., description="Process code (e.g., SENSOR_INSPECTION)")
    process_name_ko: str = Field(..., description="Process name in Korean")
    process_name_en: str = Field(..., description="Process name in English")


class ProcessHeaderInfo(APIBaseModel):
    """Process header summary from backend MES."""

    id: int = Field(..., description="Header ID")
    station_id: str = Field(..., description="Station identifier")
    batch_id: str = Field(..., description="Batch identifier")
    process_id: int = Field(..., description="Process ID (foreign key)")
    status: str = Field(..., description="Header status: OPEN, CLOSED, CANCELLED")
    total_count: int = Field(default=0, description="Total WIP items processed")
    pass_count: int = Field(default=0, description="Number of PASS results")
    fail_count: int = Field(default=0, description="Number of FAIL results")
    opened_at: datetime = Field(..., description="When header was opened")
    closed_at: Optional[datetime] = Field(None, description="When header was closed")
    process_name: Optional[str] = Field(None, description="Process name (from relation)")
    process_code: Optional[str] = Field(None, description="Process code (from relation)")


class ValidateWIPRequest(APIBaseModel):
    """Request body for WIP validation."""

    wip_id: str = Field(..., min_length=1, description="WIP ID to validate")
    process_id: Optional[int] = Field(None, description="Optional process ID for validation")


class ValidateWIPResponse(APIBaseModel):
    """WIP validation response."""

    valid: bool = Field(..., description="Whether the WIP ID is valid")
    wip_id: str = Field(..., description="The validated WIP ID")
    int_id: Optional[int] = Field(None, description="WIP integer ID (if valid)")
    lot_id: Optional[int] = Field(None, description="LOT ID FK (if valid)")
    status: Optional[str] = Field(None, description="WIP status (if valid)")
    message: Optional[str] = Field(None, description="Error message (if invalid)")
    has_pass_for_process: Optional[bool] = Field(
        None, description="True if WIP already has PASS result for the requested process"
    )
    pass_warning_message: Optional[str] = Field(
        None, description="Warning message if has_pass_for_process is True"
    )


# ============================================================================
# Backend Config Schemas
# ============================================================================


class BackendConfigResponse(APIBaseModel):
    """Backend configuration response."""

    url: str = Field(..., description="Backend API URL")
    api_key_masked: str = Field(..., description="Masked API key (e.g., 'eyJh...***')")
    sync_interval: int = Field(..., description="Sync interval in seconds")
    station_id: str = Field(..., description="Station identifier for backend")
    timeout: float = Field(..., description="Request timeout in seconds")
    max_retries: int = Field(..., description="Maximum retry attempts")


class UpdateBackendConfigRequest(APIBaseModel):
    """Request body for updating backend configuration."""

    url: Optional[str] = Field(None, description="Backend API URL")
    sync_interval: Optional[int] = Field(None, ge=5, le=3600, description="Sync interval (5-3600 seconds)")
    station_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Station identifier")
    timeout: Optional[float] = Field(None, ge=1.0, le=300.0, description="Request timeout (1-300 seconds)")
    max_retries: Optional[int] = Field(None, ge=0, le=10, description="Max retries (0-10)")
