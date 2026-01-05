"""
Backend integration mixin for BatchWorker.

Handles 착공 (start-process) and 완공 (complete-process) operations,
WIP lookup, process headers, and offline sync queueing.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol, TYPE_CHECKING

from station_service.core.exceptions import (
    BackendConnectionError,
    BackendError,
    WIPNotFoundError,
)
from station_service.sync.models import (
    ProcessCompleteRequest,
    ProcessStartRequest,
    ProcessHeaderOpenRequest,
    WIPLookupResult,
)

if TYPE_CHECKING:
    from station_service.models.config import BackendConfig, BatchConfig
    from station_service.storage.repositories.sync_repository import SyncRepository
    from station_service.sync.backend_client import BackendClient
    from station_service.batch.worker.state import WorkerState

logger = logging.getLogger(__name__)


class BackendMixinProtocol(Protocol):
    """Protocol for classes that use BackendMixin."""

    _backend_client: Optional["BackendClient"]
    _backend_config: Optional["BackendConfig"]
    _sync_repo: Optional["SyncRepository"]
    _state: "WorkerState"
    _config: "BatchConfig"

    @property
    def batch_id(self) -> str: ...


class BackendMixin:
    """
    Mixin providing Backend integration methods.

    Handles:
    - WIP lookup
    - 착공 (start-process)
    - 완공 (complete-process)
    - Process headers
    - Offline sync queueing
    """

    async def init_backend_client(self: BackendMixinProtocol) -> None:
        """Initialize and connect Backend client if configured."""
        if not self._backend_config or not self._backend_config.url:
            logger.info("Backend not configured, running without Backend integration")
            return

        try:
            from station_service.sync.backend_client import BackendClient
            from station_service.core.token_manager import get_token_manager
            from station_service.api.routes.system import update_operator_tokens

            self._backend_client = BackendClient(self._backend_config)
            await self._backend_client.connect()

            # Connect TokenManager for automatic token refresh
            token_manager = get_token_manager()
            self._backend_client.set_token_manager(token_manager)
            self._backend_client.set_token_update_callback(update_operator_tokens)
            logger.info("Worker BackendClient connected with TokenManager")

            is_online = await self._backend_client.health_check()
            self._state.backend.is_online = is_online

            if is_online:
                logger.info(f"Backend client connected: {self._backend_config.url}")
            else:
                logger.warning("Backend client connected but health check failed")

        except Exception as e:
            logger.warning(f"Failed to initialize Backend client: {e}")
            self._backend_client = None
            self._state.backend.is_online = False

    async def lookup_wip(
        self: BackendMixinProtocol,
        wip_id_string: str,
        process_id: Optional[int] = None,
    ) -> WIPLookupResult:
        """
        Lookup WIP by string ID to get integer ID.

        Args:
            wip_id_string: WIP ID string from barcode
            process_id: Optional process ID for validation

        Returns:
            WIPLookupResult with int ID

        Raises:
            WIPNotFoundError: If WIP not found
            BackendConnectionError: If Backend not available
        """
        if not self._backend_client:
            raise BackendConnectionError("", "Backend client not initialized")

        return await self._backend_client.lookup_wip(wip_id_string, process_id)

    async def start_process(
        self: BackendMixinProtocol,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        equipment_id: Optional[int] = None,
        header_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Call Backend start-process API (착공).

        Args:
            wip_int_id: WIP integer ID
            process_id: Process number
            operator_id: Operator ID
            equipment_id: Optional equipment ID
            header_id: Optional header ID from batch config

        Returns:
            Backend response

        Raises:
            BackendError: If API call fails
        """
        if not self._backend_client:
            raise BackendConnectionError("", "Backend client not initialized")

        # Ensure process header exists for station/batch tracking
        header_id = await self._ensure_process_header(process_id, header_id)

        request = ProcessStartRequest(
            process_id=process_id,
            header_id=header_id,
            operator_id=operator_id,
            equipment_id=equipment_id,
            started_at=datetime.now(timezone.utc),
        )

        return await self._backend_client.start_process(wip_int_id, request)

    async def complete_process(
        self: BackendMixinProtocol,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        result: str,
        measurements: Dict[str, Any],
        defects: List[str],
        notes: str = "",
        started_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Call Backend complete-process API (완공).

        Args:
            wip_int_id: WIP integer ID
            process_id: Process number
            operator_id: Operator ID
            result: PASS, FAIL, or REWORK
            measurements: Measurement data from sequence
            defects: Defect codes if failed
            notes: Operator notes
            started_at: Process start time from 착공

        Returns:
            Backend response

        Raises:
            BackendError: If API call fails
        """
        if not self._backend_client:
            raise BackendConnectionError("", "Backend client not initialized")

        request = ProcessCompleteRequest(
            result=result,
            header_id=self._state.backend.current_header_id,
            measurements=measurements,
            defects=defects,
            notes=notes,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
        )

        return await self._backend_client.complete_process(
            wip_int_id, process_id, operator_id, request
        )

    async def _ensure_process_header(
        self: BackendMixinProtocol,
        process_id: int,
        header_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Ensure a process header exists for this batch session.

        Uses header ID from parameters if specified, otherwise opens a new header
        or retrieves existing one for station+batch+process.

        Args:
            process_id: Process ID for the header
            header_id: Optional header ID from batch config (via start_sequence params)

        Returns:
            Header ID if successful, None otherwise
        """
        if not self._backend_client or not self._state.backend.station_id:
            logger.debug("Backend client or station_id not available, skipping header")
            return None

        # If we already have a header for this process, return it
        if self._state.backend.current_header_id is not None:
            logger.debug(f"Using existing header: {self._state.backend.current_header_id}")
            return self._state.backend.current_header_id

        # Use header_id from parameters (passed from batch config via start_sequence)
        if header_id is not None:
            self._state.backend.current_header_id = header_id
            logger.info(
                f"Using header_id from batch config: id={header_id}, "
                f"batch={self.batch_id}, process={process_id}"
            )
            return header_id

        try:
            # Prepare header open request
            request = ProcessHeaderOpenRequest(
                station_id=self._state.backend.station_id,
                batch_id=self.batch_id,
                process_id=process_id,
                sequence_package=self._state.manifest.get("name") if self._state.manifest else None,
                sequence_version=self._state.manifest.get("version") if self._state.manifest else None,
                parameters={},  # Could be expanded
                hardware_config={},  # Could be expanded
            )

            # Open or get existing header
            header = await self._backend_client.open_header(request)
            self._state.backend.current_header_id = header.id

            logger.info(
                f"Process header opened: id={header.id}, "
                f"station={self._state.backend.station_id}, "
                f"batch={self.batch_id}, process={process_id}"
            )

            return self._state.backend.current_header_id

        except BackendError as e:
            logger.warning(f"Failed to open process header: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error opening process header: {e}")
            return None

    async def close_process_header(
        self: BackendMixinProtocol,
        status: str = "CLOSED",
    ) -> None:
        """
        Close the current process header when batch completes.

        Args:
            status: Final status (CLOSED or CANCELLED)
        """
        if not self._backend_client or not self._state.backend.current_header_id:
            return

        try:
            header = await self._backend_client.close_header(
                header_id=self._state.backend.current_header_id,
                status=status,
            )
            logger.info(
                f"Process header closed: id={header.id}, status={status}, "
                f"total={header.total_count}, pass={header.pass_count}, fail={header.fail_count}"
            )
        except BackendError as e:
            logger.warning(f"Failed to close process header: {e}")
        except Exception as e:
            logger.error(f"Unexpected error closing process header: {e}")
        finally:
            self._state.backend.reset_header()

    async def queue_for_offline_sync(
        self: BackendMixinProtocol,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: Dict[str, Any],
    ) -> None:
        """
        Queue operation for offline sync using SQLite.

        Args:
            entity_type: Type of entity (e.g., "wip_process")
            entity_id: Entity identifier
            action: Action type (e.g., "start_process", "complete_process")
            payload: Request data
        """
        if self._sync_repo:
            try:
                queue_id = await self._sync_repo.enqueue(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                    payload=payload,
                )
                logger.info(f"Queued for offline sync: {action} for {entity_id} (id={queue_id})")
            except Exception as e:
                logger.error(f"Failed to queue for offline sync: {e}")
        else:
            logger.warning(f"No sync repo available, cannot queue {action} for {entity_id}")

    @staticmethod
    def extract_defects_from_result(result: Dict[str, Any]) -> List[str]:
        """
        Extract defect codes from CLI execution result.

        Args:
            result: CLI execution result dict

        Returns:
            List of unique defect codes
        """
        defects: List[str] = []

        steps = result.get("steps", [])
        for step in steps:
            step_passed = step.get("passed", True)
            if not step_passed:
                # Get defects from step
                step_defects = step.get("defects", [])
                if step_defects:
                    defects.extend(step_defects)

                # Also check for error
                step_error = step.get("error")
                if step_error and step_error not in defects:
                    defects.append(step_error)

        # Return unique defects
        return list(set(defects))
