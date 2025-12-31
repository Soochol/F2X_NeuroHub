"""FastAPI router for Station registry endpoints.

This module provides RESTful API endpoints for managing Station Service
registrations in the F2X NeuroHub MES system. Stations are automatically
registered when they connect and report their status via heartbeat.

Provides:
    - GET /: List all registered stations
    - GET /{station_id}: Get station by ID
    - POST /register: Register or update a station (called by Station Service)
    - POST /{station_id}/heartbeat: Update station status (called by Station Service)
    - DELETE /{station_id}: Unregister a station

All endpoints include:
    - Comprehensive docstrings with operation descriptions
    - Pydantic schema validation for request/response
    - OpenAPI documentation metadata
    - Proper HTTP status codes
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.models.station import Station, StationStatus


router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
    responses={
        404: {"description": "Station not found"},
        400: {"description": "Invalid request data"},
    },
)


# ============================================================================
# Schemas
# ============================================================================

class StationHealthData(BaseModel):
    """Health data reported by station."""
    status: str = Field(..., description="Health status: healthy, degraded, unhealthy")
    batches_running: int = Field(0, description="Number of running batches")
    backend_status: str = Field("disconnected", description="Backend connection status")
    disk_usage: float = Field(0, description="Disk usage percentage")
    uptime: int = Field(0, description="Uptime in seconds")


class StationRegisterRequest(BaseModel):
    """Request to register or update a station."""
    station_id: str = Field(..., description="Unique station identifier")
    station_name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Station description")
    host: str = Field(..., description="Station host/IP")
    port: int = Field(8080, description="Station port")
    version: Optional[str] = Field(None, description="Service version")
    health_data: Optional[StationHealthData] = None


class StationHeartbeatRequest(BaseModel):
    """Heartbeat request from station."""
    version: Optional[str] = None
    health_data: Optional[StationHealthData] = None


class StationResponse(BaseModel):
    """Station response model."""
    id: int
    station_id: str
    station_name: str
    description: Optional[str] = None
    host: str
    port: int
    status: str
    version: Optional[str] = None
    is_active: bool
    health_data: Optional[dict] = None
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StationListResponse(BaseModel):
    """Response for station list."""
    stations: List[StationResponse]
    total: int


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "/",
    response_model=StationListResponse,
    summary="List all stations",
    description="Retrieve all registered stations with their current status",
)
def list_stations(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
) -> StationListResponse:
    """List all registered stations.

    Retrieves all stations that have registered with the backend.
    Stations are automatically marked as OFFLINE if not seen for > 30 seconds.
    """
    # Update status for stations not seen recently
    _update_offline_stations(db)

    query = select(Station)

    if is_active is not None:
        query = query.where(Station.is_active == is_active)

    if status_filter:
        query = query.where(Station.status == status_filter.upper())

    query = query.order_by(Station.station_name)

    # Get total count
    count_query = select(func.count()).select_from(Station)
    if is_active is not None:
        count_query = count_query.where(Station.is_active == is_active)
    if status_filter:
        count_query = count_query.where(Station.status == status_filter.upper())
    total = db.scalar(count_query) or 0

    # Get paginated results
    query = query.offset(skip).limit(limit)
    stations = db.scalars(query).all()

    return StationListResponse(
        stations=[StationResponse.model_validate(s) for s in stations],
        total=total,
    )


@router.get(
    "/{station_id}",
    response_model=StationResponse,
    summary="Get station by ID",
    description="Retrieve a specific station by its station_id",
)
def get_station(
    station_id: str,
    db: Session = Depends(deps.get_db),
) -> StationResponse:
    """Get a specific station by station_id."""
    station = db.scalar(
        select(Station).where(Station.station_id == station_id)
    )

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station '{station_id}' not found",
        )

    return StationResponse.model_validate(station)


@router.post(
    "/register",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register or update station",
    description="Register a new station or update existing one. Called by Station Service on startup.",
)
def register_station(
    request: StationRegisterRequest,
    db: Session = Depends(deps.get_db),
) -> StationResponse:
    """Register or update a station.

    This endpoint is called by Station Service when it starts up.
    If the station already exists, it updates the registration.
    """
    # Check if station already exists
    station = db.scalar(
        select(Station).where(Station.station_id == request.station_id)
    )

    now = datetime.now(timezone.utc)

    if station:
        # Update existing station
        station.station_name = request.station_name
        station.description = request.description
        station.host = request.host
        station.port = request.port
        station.version = request.version
        station.status = StationStatus.ONLINE.value
        station.last_seen_at = now
        station.updated_at = now

        if request.health_data:
            station.health_data = request.health_data.model_dump()
    else:
        # Create new station
        station = Station(
            station_id=request.station_id,
            station_name=request.station_name,
            description=request.description,
            host=request.host,
            port=request.port,
            version=request.version,
            status=StationStatus.ONLINE.value,
            is_active=True,
            health_data=request.health_data.model_dump() if request.health_data else {},
            last_seen_at=now,
        )
        db.add(station)

    db.commit()
    db.refresh(station)

    return StationResponse.model_validate(station)


@router.post(
    "/{station_id}/heartbeat",
    response_model=StationResponse,
    summary="Station heartbeat",
    description="Update station status via heartbeat. Called periodically by Station Service.",
)
def station_heartbeat(
    station_id: str,
    request: StationHeartbeatRequest,
    db: Session = Depends(deps.get_db),
) -> StationResponse:
    """Process station heartbeat.

    Updates the last_seen_at timestamp and health data.
    Called periodically by Station Service.
    """
    station = db.scalar(
        select(Station).where(Station.station_id == station_id)
    )

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station '{station_id}' not found. Please register first.",
        )

    now = datetime.now(timezone.utc)
    station.last_seen_at = now
    station.status = StationStatus.ONLINE.value

    if request.version:
        station.version = request.version

    if request.health_data:
        station.health_data = request.health_data.model_dump()

        # Update status based on health
        if request.health_data.status == "unhealthy":
            station.status = StationStatus.DEGRADED.value

    db.commit()
    db.refresh(station)

    return StationResponse.model_validate(station)


@router.delete(
    "/{station_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister station",
    description="Remove a station from the registry",
)
def unregister_station(
    station_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Unregister a station.

    Removes the station from the registry. Requires authentication.
    """
    station = db.scalar(
        select(Station).where(Station.station_id == station_id)
    )

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station '{station_id}' not found",
        )

    db.delete(station)
    db.commit()


# ============================================================================
# Helper Functions
# ============================================================================

def _update_offline_stations(db: Session, timeout_seconds: int = 30) -> None:
    """Mark stations as OFFLINE if not seen recently."""
    threshold = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)

    stations = db.scalars(
        select(Station).where(
            Station.status == StationStatus.ONLINE.value,
            Station.last_seen_at < threshold,
        )
    ).all()

    for station in stations:
        station.status = StationStatus.OFFLINE.value

    if stations:
        db.commit()
