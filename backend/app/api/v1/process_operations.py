"""
Process Operations API endpoints for manufacturing workflow.

Provides operational endpoints for:
    - Process start (착공 등록)
    - Process complete (완공 등록)
    - Process history (공정 이력 조회)

These endpoints are separate from the CRUD operations in processes.py
and handle the actual manufacturing workflow operations.
"""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.services.process_service import process_service
from app.schemas.process_operations import (
    ProcessStartRequest,
    ProcessStartResponse,
    ProcessCompleteRequest,
    ProcessCompleteResponse,
    ProcessHistoryResponse,
)

router = APIRouter()


@router.post(
    "/start",
    response_model=ProcessStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="착공 등록",
    description="Start a new process for a LOT/Serial. Validates process sequence and previous process completion.",
)
@router.post("/start/", response_model=ProcessStartResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def start_process(
    request: ProcessStartRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessStartResponse:
    """
    Register process start (착공 등록).

    **Validation Rules:**
    - LOT must exist and be active (CREATED or IN_PROGRESS)
    - Serial must exist (if serial_number provided)
    - Process sequence: Previous process must be PASS (except process 1)
    - Process 7 (Label Printing): Requires ALL processes 1-6 to be PASS

    **Request Body:**
    ```json
    {
        "lot_number": "WF-KR-251110D-001",
        "serial_number": "WF-KR-251110D-001-0001",
        "process_id": 1,
        "worker_id": "W001",
        "equipment_id": "EQ-001"
    }
    ```

    **Error Responses:**
    - 400: Invalid process sequence or validation failure
    - 404: LOT, Serial, or Process not found
    - 409: Process already started (duplicate)
    """
    return process_service.start_process(db, request)


@router.post(
    "/complete",
    response_model=ProcessCompleteResponse,
    summary="완공 등록",
    description="Complete a process with result and measurement data.",
)
@router.post("/complete/", response_model=ProcessCompleteResponse, include_in_schema=False)
def complete_process(
    request: ProcessCompleteRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessCompleteResponse:
    """
    Register process completion (완공 등록).

    **Request Body:**
    ```json
    {
        "lot_number": "WF-KR-251110D-001",
        "serial_number": "WF-KR-251110D-001-0001",
        "process_id": 1,
        "result": "PASS",
        "measurement_data": {
            "temperature": 25.5,
            "humidity": 60
        }
    }
    ```

    **Error Responses:**
    - 400: Invalid result or validation failure
    - 404: Process data not found (not started)
    """
    return process_service.complete_process(db, request)


@router.get(
    "/history/{serial_number}",
    response_model=ProcessHistoryResponse,
    summary="공정 이력 조회",
    description="Get complete process history for a serial number.",
)
def get_process_history(
    serial_number: str = Path(..., description="Serial number to look up"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessHistoryResponse:
    """
    Get process history for a serial number (공정 이력 조회).

    Returns the complete manufacturing history showing all 8 processes
    and their execution status.

    **Response:**
    ```json
    {
        "serial_number": "WF-KR-251110D-001-0001",
        "lot_number": "WF-KR-251110D-001",
        "total_processes": 8,
        "completed_processes": 5,
        "history": [
            {
                "process_number": 1,
                "process_name": "레이저 마킹",
                "result": "PASS",
                "started_at": "2025-01-10T09:00:00",
                "completed_at": "2025-01-10T09:05:00",
                "duration_seconds": 300,
                "operator_name": "김철수"
            },
            ...
        ]
    }
    ```
    """
    return process_service.get_process_history(db, serial_number)
