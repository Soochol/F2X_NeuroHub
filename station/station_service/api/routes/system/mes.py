"""
MES integration routes.

Provides endpoints for:
- Get process list (/processes)
- Get process headers (/headers)
- Validate WIP (/validate-wip)
"""

import logging
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from station_service.api.dependencies import get_backend_client, get_config
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.routes.system.schemas import (
    ProcessInfo,
    ProcessHeaderInfo,
    ValidateWIPRequest,
    ValidateWIPResponse,
)
from station_service.api.routes.system.operator import (
    get_operator_session,
    clear_operator_session,
)
from station_service.core.exceptions import BackendError, WIPNotFoundError
from station_service.models.config import StationConfig
from station_service.sync.backend_client import BackendClient

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/processes",
    response_model=ApiResponse[List[ProcessInfo]],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get process list",
    description="""
    Get list of active processes from Backend MES.

    Used for selecting which process to use for 착공/완공 tracking.
    """,
)
async def get_processes(
    config: StationConfig = Depends(get_config),
    backend_client: BackendClient = Depends(get_backend_client),
) -> ApiResponse[List[ProcessInfo]]:
    """Get process list from Backend MES."""
    from station_service.core.exceptions import BackendConnectionError, BackendError

    try:
        # Check if backend is configured
        if not config.backend.url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend not configured. Set backend URL in station.yaml.",
            )

        # Ensure client is connected
        if not backend_client.is_connected:
            await backend_client.connect()

        # Fetch processes from backend (uses API Key auth)
        processes_data = await backend_client.get_processes()

        # Map to ProcessInfo
        processes = [
            ProcessInfo(
                id=p.get("id", 0),
                process_number=p.get("process_number", 0),
                process_code=p.get("process_code", ""),
                process_name_ko=p.get("process_name_ko", ""),
                process_name_en=p.get("process_name_en", ""),
            )
            for p in processes_data
        ]

        return ApiResponse(
            success=True,
            data=processes,
        )

    except BackendConnectionError as e:
        logger.error(f"Backend connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to backend: {str(e)}",
        )
    except BackendError as e:
        logger.warning(f"Backend error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e.message) if hasattr(e, "message") else "Failed to get processes",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get processes")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processes: {str(e)}",
        )


@router.get(
    "/headers",
    response_model=ApiResponse[List[ProcessHeaderInfo]],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get process headers",
    description="""
    Get list of process headers from Backend MES.

    Filter by station_id, batch_id, process_id, or status.
    Used for selecting existing headers to link to a batch.
    """,
)
async def get_headers(
    station_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    process_id: Optional[int] = None,
    header_status: Optional[str] = None,
    limit: int = 100,
    config: StationConfig = Depends(get_config),
    backend_client: BackendClient = Depends(get_backend_client),
) -> ApiResponse[List[ProcessHeaderInfo]]:
    """Get process headers from Backend MES."""
    from station_service.core.exceptions import BackendConnectionError, BackendError

    try:
        # Check if backend is configured
        if not config.backend.url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend not configured. Set backend URL in station.yaml.",
            )

        # Ensure client is connected
        if not backend_client.is_connected:
            await backend_client.connect()

        # Fetch headers from backend (uses API Key auth internally)
        headers_data = await backend_client.list_headers(
            station_id=station_id,
            batch_id=batch_id,
            process_id=process_id,
            status=header_status,
            limit=limit,
        )

        # Map to ProcessHeaderInfo
        headers = [
            ProcessHeaderInfo(
                id=h.id,
                station_id=h.station_id,
                batch_id=h.batch_id,
                process_id=h.process_id,
                status=h.status,
                total_count=h.total_count,
                pass_count=h.pass_count,
                fail_count=h.fail_count,
                opened_at=h.opened_at,
                closed_at=h.closed_at,
                process_name=h.process_name,
                process_code=h.process_code,
            )
            for h in headers_data
        ]

        return ApiResponse(
            success=True,
            data=headers,
        )

    except BackendConnectionError as e:
        logger.error(f"Backend connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to backend: {str(e)}",
        )
    except BackendError as e:
        logger.warning(f"Backend error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e.message) if hasattr(e, "message") else "Failed to get headers",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get headers")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get headers: {str(e)}",
        )


@router.post(
    "/validate-wip",
    response_model=ApiResponse[ValidateWIPResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
    summary="Validate WIP ID",
    description="""
    Validate a WIP ID against the backend before starting a batch.

    This endpoint performs a quick validation check to verify:
    - The WIP ID exists in the backend
    - The WIP is in a valid status for processing

    Use this before starting a batch to avoid the delay of
    stopping a batch after WIP validation fails.
    """,
)
async def validate_wip(
    request: ValidateWIPRequest,
    backend_client: BackendClient = Depends(get_backend_client),
    config: StationConfig = Depends(get_config),
) -> ApiResponse[ValidateWIPResponse]:
    """Validate WIP ID against the backend."""
    from station_service.core.exceptions import TokenExpiredError

    # Check if backend is configured
    if not config.backend.url:
        return ApiResponse(
            success=True,
            data=ValidateWIPResponse(
                valid=True,
                wip_id=request.wip_id,
                message="Backend not configured, skipping validation",
            ),
        )

    try:
        # Connect if not connected
        if not backend_client.is_connected:
            await backend_client.connect()

        # Get access token from operator session
        session = get_operator_session()
        access_token = session.get("access_token")

        if not access_token:
            return ApiResponse(
                success=True,
                data=ValidateWIPResponse(
                    valid=False,
                    wip_id=request.wip_id,
                    message="Operator not logged in. Please login first.",
                ),
            )

        # Lookup WIP (uses API Key auth internally)
        wip_result = await backend_client.lookup_wip(
            request.wip_id,
            process_id=request.process_id,
        )

        return ApiResponse(
            success=True,
            data=ValidateWIPResponse(
                valid=True,
                wip_id=request.wip_id,
                int_id=wip_result.id,
                lot_id=wip_result.lot_id,
                status=wip_result.status,
                has_pass_for_process=wip_result.has_pass_for_process,
                pass_warning_message=wip_result.pass_warning_message,
            ),
        )

    except WIPNotFoundError:
        return ApiResponse(
            success=True,
            data=ValidateWIPResponse(
                valid=False,
                wip_id=request.wip_id,
                message=f"WIP '{request.wip_id}' not found",
            ),
        )

    except httpx.ConnectError as e:
        logger.error(f"Backend connection error during WIP validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to backend: {str(e)}",
        )

    except httpx.HTTPStatusError as e:
        logger.warning(f"Backend HTTP error during WIP validation: {e}")
        return ApiResponse(
            success=True,
            data=ValidateWIPResponse(
                valid=False,
                wip_id=request.wip_id,
                message=f"Backend validation failed: {e.response.status_code}",
            ),
        )

    except TokenExpiredError:
        # Token expired and auto-refresh failed
        logger.warning("Token expired during WIP validation, clearing session")
        clear_operator_session()
        return ApiResponse(
            success=True,
            data=ValidateWIPResponse(
                valid=False,
                wip_id=request.wip_id,
                message="세션이 만료되었습니다. 다시 로그인해주세요.",
            ),
        )

    except BackendError as e:
        logger.warning(f"Backend error during WIP validation: {e}")
        return ApiResponse(
            success=True,
            data=ValidateWIPResponse(
                valid=False,
                wip_id=request.wip_id,
                message=str(e),
            ),
        )

    except Exception as e:
        logger.exception("Failed to validate WIP")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate WIP: {str(e)}",
        )
