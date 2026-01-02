"""
Pydantic schemas for Sequence API.

Provides request/response schemas for sequence upload, download, and deployment.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Base Schemas
# ============================================================================


class SequenceBase(BaseModel):
    """Base sequence schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Unique sequence identifier")
    version: str = Field(default="1.0.0", max_length=20, description="Version (semver)")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    description: Optional[str] = Field(None, description="Description")


class SequenceCreate(SequenceBase):
    """Schema for creating a sequence (metadata only, package uploaded separately)."""

    process_id: Optional[int] = Field(None, description="Target process ID")


class SequenceUpdate(BaseModel):
    """Schema for updating sequence metadata."""

    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_deprecated: Optional[bool] = None
    process_id: Optional[int] = None


# ============================================================================
# Response Schemas
# ============================================================================


class SequenceResponse(SequenceBase):
    """Response schema for sequence."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    checksum: str
    package_size: int
    hardware: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    process_id: Optional[int] = None
    is_active: bool
    is_deprecated: bool
    uploaded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class SequenceListResponse(BaseModel):
    """Response schema for sequence list."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    package_size: int
    process_id: Optional[int] = None
    is_active: bool
    is_deprecated: bool
    created_at: datetime
    updated_at: datetime


class SequenceVersionResponse(BaseModel):
    """Response schema for sequence version."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sequence_id: int
    version: str
    checksum: str
    package_size: int
    change_notes: Optional[str] = None
    uploaded_by: Optional[int] = None
    created_at: datetime


class SequenceDeploymentResponse(BaseModel):
    """Response schema for sequence deployment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sequence_id: int
    station_id: Optional[str] = None
    batch_id: Optional[str] = None
    version: str
    status: str
    error_message: Optional[str] = None
    deployed_by: Optional[int] = None
    created_at: datetime
    deployed_at: Optional[datetime] = None


# ============================================================================
# Upload Schemas
# ============================================================================


class SequenceUploadResponse(BaseModel):
    """Response schema for sequence upload."""

    id: int
    name: str
    version: str
    display_name: Optional[str] = None
    checksum: str
    package_size: int
    is_new: bool = Field(description="Whether this is a new sequence or an update")
    previous_version: Optional[str] = Field(None, description="Previous version if updated")
    message: str


class SequenceManifest(BaseModel):
    """Parsed manifest.yaml contents."""

    name: str
    version: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    hardware: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# Deployment Schemas
# ============================================================================


class SequenceDeployRequest(BaseModel):
    """Request schema for deploying sequence to station."""

    station_id: str = Field(..., description="Target station ID")
    batch_id: Optional[str] = Field(None, description="Target batch ID (optional)")
    version: Optional[str] = Field(None, description="Specific version to deploy (default: latest)")


class SequenceDeployResponse(BaseModel):
    """Response schema for deployment request."""

    deployment_id: int
    sequence_name: str
    version: str
    station_id: str
    batch_id: Optional[str] = None
    status: str
    message: str


class SequenceRollbackRequest(BaseModel):
    """Request schema for rolling back to previous version."""

    version: str = Field(..., description="Version to rollback to")
    reason: Optional[str] = Field(None, description="Reason for rollback")


class SequenceRollbackResponse(BaseModel):
    """Response schema for rollback."""

    sequence_name: str
    previous_version: str
    new_version: str
    message: str


# ============================================================================
# Download Schemas
# ============================================================================


class SequenceDownloadInfo(BaseModel):
    """Info about sequence package for download."""

    name: str
    version: str
    checksum: str
    package_size: int
    download_url: str


# ============================================================================
# Station Pull Schemas (for Station Service)
# ============================================================================


class SequencePullRequest(BaseModel):
    """Request from Station Service to pull sequence."""

    station_id: str = Field(..., description="Requesting station ID")
    batch_id: Optional[str] = Field(None, description="Target batch ID")
    current_version: Optional[str] = Field(None, description="Currently installed version")


class SequencePullResponse(BaseModel):
    """Response to Station Service pull request."""

    name: str
    version: str
    checksum: str
    package_size: int
    needs_update: bool = Field(description="Whether station needs to update")
    package_data: Optional[str] = Field(None, description="Base64-encoded package if needs_update")


# ============================================================================
# List/Filter Schemas
# ============================================================================


class SequenceListParams(BaseModel):
    """Query parameters for listing sequences."""

    is_active: Optional[bool] = None
    is_deprecated: Optional[bool] = None
    process_id: Optional[int] = None
    search: Optional[str] = Field(None, description="Search in name/display_name/description")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)
