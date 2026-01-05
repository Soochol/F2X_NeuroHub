"""
Command handler mixin for BatchWorker.

Handles IPC command processing for START_SEQUENCE, STOP_SEQUENCE,
GET_STATUS, MANUAL_CONTROL, and SHUTDOWN commands.
"""

import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, TYPE_CHECKING

from station_service.ipc import IPCResponse
from station_service.ipc.messages import CommandType, IPCCommand
from station_service.models.batch import BatchStatus

from station_service.batch.worker.exceptions import (
    SequenceAlreadyRunningError,
    SequenceNotRunningError,
    CLIWorkerStartError,
)

if TYPE_CHECKING:
    from station_service.batch.cli_worker import CLISequenceWorker
    from station_service.ipc import IPCClient
    from station_service.models.config import BatchConfig, WorkflowConfig
    from station_service.batch.worker.state import WorkerState

logger = logging.getLogger(__name__)


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def convert_params_to_snake_case(params: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all parameter keys from camelCase to snake_case."""
    return {camel_to_snake(k): v for k, v in params.items()}


class CommandsMixinProtocol(Protocol):
    """Protocol for classes that use CommandsMixin."""

    _config: "BatchConfig"
    _ipc: "IPCClient"
    _cli_worker: Optional["CLISequenceWorker"]
    _execution_task: Optional[asyncio.Task]
    _running: bool
    _state: "WorkerState"

    @property
    def batch_id(self) -> str: ...

    # Backend mixin methods
    async def lookup_wip(self, wip_id_string: str, process_id: Optional[int] = None) -> Any: ...
    async def start_process(
        self,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        equipment_id: Optional[int] = None,
        header_id: Optional[int] = None,
    ) -> Dict[str, Any]: ...
    async def close_process_header(self, status: str = "CLOSED") -> None: ...
    async def queue_for_offline_sync(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: Dict[str, Any],
    ) -> None: ...

    # Execution mixin methods
    def create_cli_worker(self, sequence_name: str, sequences_dir: Path) -> "CLISequenceWorker": ...
    async def run_cli_sequence(self) -> None: ...
    async def stop_cli_worker(self) -> None: ...

    # Hardware mixin methods
    async def handle_manual_control(
        self,
        hardware: str,
        command: str,
        params: Dict[str, Any],
    ) -> Any: ...


class CommandsMixin:
    """
    Mixin providing IPC command handling methods.

    Handles:
    - START_SEQUENCE: Start sequence execution with WIP context
    - STOP_SEQUENCE: Stop running sequence
    - GET_STATUS: Return current worker status
    - MANUAL_CONTROL: Execute manual hardware commands
    - SHUTDOWN: Graceful shutdown
    - PING: Health check
    """

    async def handle_command(
        self: CommandsMixinProtocol,
        command: IPCCommand,
    ) -> IPCResponse:
        """
        Handle incoming IPC commands.

        Args:
            command: The command to handle

        Returns:
            Response to the command
        """
        logger.debug(f"Handling command: {command.type.value}")

        try:
            if command.type == CommandType.START_SEQUENCE:
                return await self._cmd_start_sequence(command)

            elif command.type == CommandType.STOP_SEQUENCE:
                return await self._cmd_stop_sequence(command)

            elif command.type == CommandType.GET_STATUS:
                return await self._cmd_get_status(command)

            elif command.type == CommandType.MANUAL_CONTROL:
                return await self._cmd_manual_control(command)

            elif command.type == CommandType.SHUTDOWN:
                return await self._cmd_shutdown(command)

            elif command.type == CommandType.PING:
                return IPCResponse.ok(command.request_id, {"pong": True})

            else:
                return IPCResponse.error(
                    command.request_id,
                    f"Unknown command type: {command.type.value}",
                )

        except SequenceAlreadyRunningError as e:
            logger.warning(f"Sequence already running: {e}")
            return IPCResponse.error(command.request_id, str(e))

        except SequenceNotRunningError as e:
            logger.warning(f"Sequence not running: {e}")
            return IPCResponse.error(command.request_id, str(e))

        except CLIWorkerStartError as e:
            logger.error(f"CLI worker start error: {e}")
            return IPCResponse.error(command.request_id, str(e))

        except Exception as e:
            logger.exception(f"Command handling error: {e}")
            return IPCResponse.error(command.request_id, str(e))

    async def _cmd_start_sequence(
        self: CommandsMixinProtocol,
        command: IPCCommand,
    ) -> IPCResponse:
        """
        Handle START_SEQUENCE command with Backend integration.

        Expected parameters:
        - wip_id: WIP ID string from barcode scan (required for Backend)
        - process_id: Process number 1-8 (required for Backend)
        - operator_id: Operator ID (required for Backend)
        - equipment_id: Equipment ID (optional)
        - Other sequence-specific parameters
        """
        if self._state.status == BatchStatus.RUNNING:
            raise SequenceAlreadyRunningError(
                self.batch_id,
                self._state.execution.execution_id if self._state.execution else None,
            )

        parameters = command.params.get("parameters", {})

        # Extract WIP context from parameters
        wip_id_string = parameters.get("wip_id")
        wip_int_id = parameters.get("wip_int_id")  # Pre-validated WIP int ID
        process_id = parameters.get("process_id")
        operator_id = parameters.get("operator_id")
        equipment_id = parameters.get("equipment_id")
        header_id = parameters.get("header_id")  # Header ID from batch config

        # Generate execution ID
        execution_id = str(uuid.uuid4())[:8]

        # Resolved WIP int ID
        wip_int_id_resolved = None

        # ═══════════════════════════════════════════════════════════════
        # Backend Integration: 착공 (Start Process)
        # ═══════════════════════════════════════════════════════════════
        if wip_id_string and process_id and operator_id:
            try:
                from station_service.core.exceptions import (
                    BackendError,
                    WIPNotFoundError,
                )

                # 1. Get WIP int ID (use pre-validated or lookup)
                if wip_int_id:
                    logger.info(f"Using pre-validated WIP int ID: {wip_int_id}")
                    wip_int_id_resolved = wip_int_id
                else:
                    wip_lookup = await self.lookup_wip(wip_id_string, process_id)
                    wip_int_id_resolved = wip_lookup.id

                # 2. Call 착공 (start-process)
                await self.start_process(
                    wip_int_id=wip_int_id_resolved,
                    process_id=process_id,
                    operator_id=operator_id,
                    equipment_id=equipment_id,
                    header_id=header_id,
                )
                logger.info(f"착공 completed: WIP={wip_id_string}, Process={process_id}, Header={header_id}")

            except WIPNotFoundError as e:
                logger.error(f"WIP not found: {e}")
                return IPCResponse.error(command.request_id, str(e))

            except BackendError as e:
                # Check if it's a client error (4xx) - should fail, not continue offline
                if e.status_code and 400 <= e.status_code < 500:
                    logger.error(f"Client error during 착공: {e}")
                    return IPCResponse.error(command.request_id, str(e))

                # Server error (5xx) or connection error - continue in offline mode
                logger.warning(f"Backend error during 착공, continuing offline: {e}")
                self._state.backend.is_online = False

                # Queue for later sync
                await self.queue_for_offline_sync(
                    "wip_process",
                    wip_id_string,
                    "start_process",
                    {
                        "wip_int_id": wip_int_id_resolved,
                        "request": {
                            "process_id": process_id,
                            "operator_id": operator_id,
                            "equipment_id": equipment_id,
                            "started_at": datetime.now(timezone.utc).isoformat(),
                        },
                    },
                )
        else:
            # No WIP context - running sequence without Backend integration
            logger.debug("Running sequence without Backend integration (no wip_id)")

        # Get step names from manifest for UI to display skipped steps
        step_names = None
        if self._state.manifest and "steps" in self._state.manifest:
            manifest_steps = self._state.manifest["steps"]
            # steps can be a list of dicts with 'name' key or just step names
            if isinstance(manifest_steps, list):
                step_names = [
                    s.get("name") if isinstance(s, dict) else str(s)
                    for s in manifest_steps
                ]

        # Start execution state
        self._state.start_execution(
            execution_id=execution_id,
            wip_id=wip_id_string,
            wip_int_id=wip_int_id_resolved,
            process_id=process_id,
            operator_id=operator_id,
            step_names=step_names,
        )

        # Create CLI worker for subprocess execution
        self._cli_worker = self.create_cli_worker(
            sequence_name=self._state.sequence_name or self._config.sequence_package,
            sequences_dir=Path("sequences"),
        )

        # Build config for CLI execution
        cli_config = {
            "execution_id": execution_id,
            "wip_id": wip_id_string,
            "process_id": process_id,
            "operator_id": operator_id,
            "hardware": self._config.hardware,
            "parameters": convert_params_to_snake_case(parameters),
            "sequence_name": self._state.sequence_name,
            "sequence_version": self._state.sequence_version,
            "station_id": self._state.backend.station_id,
        }

        # Start CLI worker
        try:
            await self._cli_worker.start(cli_config)
        except Exception as e:
            logger.error(f"Failed to start CLI sequence: {e}")
            self._state.cancel_execution()
            raise CLIWorkerStartError(str(e), self.batch_id, self._state.sequence_name)

        # Start task to wait for completion
        self._execution_task = asyncio.create_task(self.run_cli_sequence())

        # Publish batch status update immediately
        await self._ipc.status_update({
            "status": self._state.status.value,
            **self._state.execution.to_status_dict(),
        })

        return IPCResponse.ok(command.request_id, {
            "execution_id": execution_id,
            "status": "started",
            "wip_id": wip_id_string,
            "process_id": process_id,
            "backend_online": self._state.backend.is_online,
        })

    async def _cmd_stop_sequence(
        self: CommandsMixinProtocol,
        command: IPCCommand,
    ) -> IPCResponse:
        """Handle STOP_SEQUENCE command."""
        await self.stop_cli_worker()

        if self._execution_task:
            self._execution_task.cancel()
            try:
                await self._execution_task
            except asyncio.CancelledError:
                pass
            self._execution_task = None

        # Close process header with CANCELLED status since sequence was stopped
        await self.close_process_header(status="CANCELLED")

        self._state.cancel_execution()

        return IPCResponse.ok(command.request_id, {"status": "stopped"})

    async def _cmd_get_status(
        self: CommandsMixinProtocol,
        command: IPCCommand,
    ) -> IPCResponse:
        """Handle GET_STATUS command."""
        return IPCResponse.ok(command.request_id, self._state.to_status_dict())

    async def _cmd_manual_control(
        self: CommandsMixinProtocol,
        command: IPCCommand,
    ) -> IPCResponse:
        """Handle MANUAL_CONTROL command."""
        if self._state.status == BatchStatus.RUNNING:
            return IPCResponse.error(
                command.request_id,
                "Cannot execute manual control during sequence execution",
            )

        hardware = command.params.get("hardware")
        cmd = command.params.get("command")
        params = command.params.get("params", {})

        try:
            result = await self.handle_manual_control(hardware, cmd, params)
            return IPCResponse.ok(command.request_id, {"result": result})
        except Exception as e:
            return IPCResponse.error(command.request_id, str(e))

    async def _cmd_shutdown(
        self: CommandsMixinProtocol,
        command: IPCCommand,
    ) -> IPCResponse:
        """Handle SHUTDOWN command."""
        self._running = False

        # Stop any running CLI sequence
        await self.stop_cli_worker()

        return IPCResponse.ok(command.request_id, {"status": "shutdown"})
