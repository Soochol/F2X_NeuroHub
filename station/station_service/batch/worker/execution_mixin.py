"""
Execution mixin for BatchWorker.

Handles CLI sequence execution and callbacks for step events,
measurements, logs, and completion.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from station_service.batch.cli_worker import CLISequenceWorker
    from station_service.ipc import IPCClient
    from station_service.storage.repositories.execution_repository import ExecutionRepository
    from station_service.batch.worker.state import WorkerState

logger = logging.getLogger(__name__)


class ExecutionMixinProtocol(Protocol):
    """Protocol for classes that use ExecutionMixin."""

    _ipc: "IPCClient"
    _cli_worker: Optional["CLISequenceWorker"]
    _execution_repo: Optional["ExecutionRepository"]
    _state: "WorkerState"

    @property
    def batch_id(self) -> str: ...

    # Backend mixin methods
    async def complete_process(
        self,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        result: str,
        measurements: Dict[str, Any],
        defects: List[str],
        notes: str = "",
        started_at: Optional[datetime] = None,
    ) -> Dict[str, Any]: ...

    async def queue_for_offline_sync(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: Dict[str, Any],
    ) -> None: ...

    @staticmethod
    def extract_defects_from_result(result: Dict[str, Any]) -> List[str]: ...


class ExecutionMixin:
    """
    Mixin providing execution management methods.

    Handles:
    - CLI worker lifecycle
    - Step event callbacks
    - Measurement handling
    - Execution result persistence
    - Backend completion integration
    """

    def create_cli_worker(
        self: ExecutionMixinProtocol,
        sequence_name: str,
        sequences_dir: Path,
    ) -> "CLISequenceWorker":
        """
        Create a CLI worker for subprocess execution.

        Args:
            sequence_name: Name of sequence package
            sequences_dir: Directory containing sequences

        Returns:
            Configured CLISequenceWorker
        """
        from station_service.batch.cli_worker import CLISequenceWorker

        self._cli_worker = CLISequenceWorker(
            batch_id=self.batch_id,
            sequence_name=sequence_name,
            sequences_dir=sequences_dir,
            on_step_start=self._on_cli_step_start,
            on_step_complete=self._on_cli_step_complete,
            on_measurement=self._on_cli_measurement,
            on_log=self._on_cli_log,
            on_error=self._on_cli_error,
            on_sequence_complete=self._on_cli_sequence_complete,
            on_status=self._on_cli_status,
            on_input_request=self._on_cli_input_request,
        )
        return self._cli_worker

    async def run_cli_sequence(self: ExecutionMixinProtocol) -> None:
        """
        Run the CLI sequence execution.

        Waits for the CLI worker to complete and handles final state transitions.
        Backend integration (완공) is handled in the _on_cli_sequence_complete callback.
        """
        try:
            if not self._cli_worker:
                logger.error("CLI worker not initialized")
                return

            # Wait for CLI worker to complete
            result = await self._cli_worker.wait()

            if result:
                logger.info(
                    f"CLI sequence completed: overall_pass={result.get('overall_pass')}, "
                    f"duration={result.get('duration'):.2f}s"
                )
            else:
                logger.warning("CLI sequence completed without result")

        except asyncio.CancelledError:
            logger.info("CLI sequence execution cancelled")
            await self._ipc.log("info", "Sequence execution cancelled")

        except Exception as e:
            logger.exception(f"CLI sequence execution error: {e}")
            await self._ipc.error("EXECUTION_ERROR", str(e))

        finally:
            self._state.complete_execution()

    async def stop_cli_worker(self: ExecutionMixinProtocol) -> None:
        """Stop the CLI worker if running."""
        if self._cli_worker:
            try:
                await self._cli_worker.stop()
            except Exception as e:
                logger.warning(f"Error stopping CLI worker: {e}")

    # ================================================================
    # CLI Worker Callbacks
    # ================================================================

    async def _on_cli_step_start(
        self: ExecutionMixinProtocol,
        step_name: str,
        index: int,
        total: int,
        execution_id: str,
    ) -> None:
        """Callback for CLI worker step start."""
        if not self._state.execution:
            return

        self._state.execution.update_step(step_name, index, total)
        self._state.execution.add_step_result(step_name)

        # Publish step start event
        # Include step_names on first step for UI to display skipped steps
        step_names = self._state.execution.step_names if index == 0 else None
        await self._ipc.step_start(
            step_name=step_name,
            step_index=index,
            total_steps=total,
            execution_id=execution_id,
            step_names=step_names,
        )

        # Broadcast status update
        await self._ipc.status_update({
            "status": self._state.status.value,
            **self._state.execution.to_status_dict(),
        })

    async def _on_cli_step_complete(
        self: ExecutionMixinProtocol,
        step_name: str,
        index: int,
        passed: bool,
        duration: float,
        data: Dict[str, Any],
        execution_id: str,
    ) -> None:
        """Callback for CLI worker step completion."""
        if not self._state.execution:
            return

        self._state.execution.complete_step(index)
        self._state.execution.update_step_result(
            name=step_name,
            status="completed" if passed else "failed",
            duration=duration,
            result=data,
        )

        # Publish step complete event
        await self._ipc.step_complete(
            step_name=step_name,
            step_index=index,
            duration=duration,
            passed=passed,
            result=data,
            execution_id=execution_id,
        )

        # Broadcast status update
        await self._ipc.status_update({
            "status": self._state.status.value,
            **self._state.execution.to_status_dict(),
        })

    async def _on_cli_measurement(
        self: ExecutionMixinProtocol,
        name: str,
        value: Any,
        unit: str,
        data: Dict[str, Any],
    ) -> None:
        """Callback for CLI worker measurement."""
        await self._ipc.measurement(
            name=name,
            value=value,
            unit=unit,
            passed=data.get("passed"),
            min_value=data.get("min"),
            max_value=data.get("max"),
        )

    async def _on_cli_log(
        self: ExecutionMixinProtocol,
        level: str,
        message: str,
    ) -> None:
        """Callback for CLI worker log messages."""
        await self._ipc.log(level, message)

    async def _on_cli_error(
        self: ExecutionMixinProtocol,
        code: str,
        message: str,
        step: Optional[str],
    ) -> None:
        """Callback for CLI worker errors."""
        await self._ipc.error(code=code, message=message, step=step)

    async def _on_cli_sequence_complete(
        self: ExecutionMixinProtocol,
        execution_id: str,
        overall_pass: bool,
        duration: float,
        result: Dict[str, Any],
    ) -> None:
        """
        Callback for CLI worker sequence completion.

        Handles Backend integration (완공) and result persistence.
        """
        wip_status = None
        can_convert = False

        # ═══════════════════════════════════════════════════════════════
        # Backend Integration: 완공 (Complete Process)
        # ═══════════════════════════════════════════════════════════════
        if self._state.execution and self._state.execution.has_wip_context:
            exec_state = self._state.execution
            try:
                # Determine result and extract data
                process_result = "PASS" if overall_pass else "FAIL"
                measurements = result.get("measurements", {})
                defects = self.extract_defects_from_result(result)

                # Call 완공 (complete-process)
                from station_service.core.exceptions import BackendError

                complete_response = await self.complete_process(
                    wip_int_id=exec_state.wip_int_id,
                    process_id=exec_state.process_id,
                    operator_id=exec_state.operator_id,
                    result=process_result,
                    measurements=measurements,
                    defects=defects,
                    notes=f"Sequence: {self._state.sequence_name} v{self._state.sequence_version}",
                    started_at=exec_state.process_start_time,
                )

                # Check if WIP is now COMPLETED
                wip_item = complete_response.get("wip_item", {})
                wip_status = wip_item.get("status")
                can_convert = wip_status == "COMPLETED"

                logger.info(
                    f"완공 completed: WIP={exec_state.wip_id}, "
                    f"Process={exec_state.process_id}, Result={process_result}"
                )

            except Exception as e:
                from station_service.core.exceptions import BackendError

                error_message = e.message if hasattr(e, 'message') else str(e)
                await self._ipc.error(
                    code="COMPLETE_PROCESS_FAILED",
                    message=f"완공 실패: {error_message}",
                    step="complete_process",
                )
                logger.warning(f"Backend error during 완공: {e}")

                # Queue for offline sync if transient error
                if isinstance(e, BackendError):
                    if e.status_code in (500, 502, 503, 504) or "connection" in str(e).lower():
                        await self.queue_for_offline_sync(
                            "wip_process",
                            exec_state.wip_id or "",
                            "complete_process",
                            {
                                "wip_int_id": exec_state.wip_int_id,
                                "process_id": exec_state.process_id,
                                "operator_id": exec_state.operator_id,
                                "request": {
                                    "result": "PASS" if overall_pass else "FAIL",
                                    "measurements": result.get("measurements", {}),
                                    "defects": self.extract_defects_from_result(result),
                                    "completed_at": datetime.now(timezone.utc).isoformat(),
                                },
                            },
                        )

        # Publish completion event
        await self._ipc.sequence_complete(
            execution_id=execution_id,
            overall_pass=overall_pass,
            duration=duration,
            result=result,
        )

        # Save execution result to database
        await self._save_cli_execution_to_db(execution_id, overall_pass, duration, result)

        # Publish WIP status if available
        if self._state.execution and self._state.execution.wip_id:
            await self._ipc.wip_process_complete(
                wip_id=self._state.execution.wip_id,
                process_id=self._state.execution.process_id or 0,
                result="PASS" if overall_pass else "FAIL",
                wip_status=wip_status,
                can_convert=can_convert,
            )

    async def _on_cli_status(
        self: ExecutionMixinProtocol,
        status: str,
        progress: float,
        current_step: Optional[str],
        execution_id: str,
    ) -> None:
        """Callback for CLI worker status updates."""
        if self._state.execution:
            self._state.execution.progress = progress / 100.0 if progress > 1 else progress

        await self._ipc.status_update({
            "status": status,
            "execution_id": execution_id,
            "current_step": current_step,
            "progress": self._state.execution.progress if self._state.execution else 0,
        })

    async def _on_cli_input_request(
        self: ExecutionMixinProtocol,
        request_id: str,
        prompt: str,
        input_type: str,
        data: Dict[str, Any],
    ) -> None:
        """Callback for CLI worker input requests (manual control)."""
        await self._ipc.input_request(
            request_id=request_id,
            prompt=prompt,
            input_type=input_type,
            options=data.get("options"),
            default=data.get("default"),
            timeout=data.get("timeout", 300),
        )

    async def _save_cli_execution_to_db(
        self: ExecutionMixinProtocol,
        execution_id: str,
        overall_pass: bool,
        duration: float,
        result: Dict[str, Any],
    ) -> None:
        """Save CLI execution result to database for persistent statistics."""
        if not self._execution_repo:
            logger.debug("Execution repository not available, skipping DB save")
            return

        try:
            started_at = (
                self._state.execution.started_at
                if self._state.execution
                else datetime.now(timezone.utc)
            )

            # Save execution result
            await self._execution_repo.create_execution(
                id=execution_id,
                batch_id=self.batch_id,
                sequence_name=self._state.sequence_name or "Unknown",
                sequence_version=self._state.sequence_version or "1.0.0",
                status="completed" if overall_pass else "failed",
                started_at=started_at,
                overall_pass=overall_pass,
                completed_at=datetime.now(timezone.utc),
                duration=int(duration),
            )

            # Save step results
            steps = result.get("steps", [])
            for idx, step in enumerate(steps):
                step_name = step.get("name", f"step_{idx}")
                step_passed = step.get("passed", False)
                step_duration = step.get("duration", 0)

                await self._execution_repo.create_step_result(
                    execution_id=execution_id,
                    step_order=idx + 1,
                    step_name=step_name,
                    status="completed" if step_passed else "failed",
                    pass_result=step_passed,
                    duration=step_duration,
                    result=step,
                )

            logger.info(f"Execution result saved to DB: {execution_id}")

        except Exception as e:
            logger.warning(f"Failed to save execution to DB: {e}")
