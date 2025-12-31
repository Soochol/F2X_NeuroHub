"""
Sequence executor for running test sequences.

This module provides the SequenceExecutor class which handles the execution
of test sequences, including step ordering, condition checking, timeouts,
retries, and cleanup handling.
"""

import asyncio
import inspect
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from station_service.sequence.decorators import StepMeta
from station_service.sequence.exceptions import (
    ExecutionError,
    SequenceError,
    StepTimeoutError,
    TestFailure,
    TestSkipped,
)

logger = logging.getLogger(__name__)


@dataclass
class StepResult:
    """Result of a single step execution."""

    name: str
    order: int
    status: str  # "pending", "running", "completed", "failed", "skipped"
    passed: bool
    duration: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "order": self.order,
            "status": self.status,
            "pass": self.passed,
            "duration": self.duration,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class ExecutionResult:
    """Complete result of a sequence execution."""

    sequence_name: str
    sequence_version: str
    status: str  # "running", "completed", "failed", "stopped"
    overall_pass: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    steps: List[StepResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence_name": self.sequence_name,
            "sequence_version": self.sequence_version,
            "status": self.status,
            "overall_pass": self.overall_pass,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.duration,
            "parameters": self.parameters,
            "steps": [step.to_dict() for step in self.steps],
        }


class SequenceExecutor:
    """
    Executes test sequences with step management, condition checking,
    timeout handling, and retry logic.

    Usage:
        sequence = MySequence(hardware=hw_dict, parameters=params)
        executor = SequenceExecutor(
            sequence_instance=sequence,
            parameters=params,
            on_step_start=lambda step: print(f"Starting {step}"),
            on_step_complete=lambda step, result: print(f"Completed {step}"),
        )
        result = await executor.run()
    """

    def __init__(
        self,
        sequence_instance: Any,
        parameters: Optional[Dict[str, Any]] = None,
        on_step_start: Optional[Callable[[str, StepMeta], None]] = None,
        on_step_complete: Optional[Callable[[str, StepResult], None]] = None,
        on_log: Optional[Callable[[str, str], None]] = None,
        on_error: Optional[Callable[[str, Exception], None]] = None,
    ):
        """
        Initialize the sequence executor.

        Args:
            sequence_instance: Instance of the sequence class to execute
            parameters: Execution parameters dictionary
            on_step_start: Callback when a step starts (step_name, step_meta)
            on_step_complete: Callback when a step completes (step_name, step_result)
            on_log: Callback for log messages (level, message)
            on_error: Callback for errors (step_name, exception)
        """
        self._sequence = sequence_instance
        self._parameters = parameters or {}
        self._on_step_start = on_step_start
        self._on_step_complete = on_step_complete
        self._on_log = on_log
        self._on_error = on_error

        self._stopped = False
        self._current_step: Optional[str] = None
        self._step_results: Dict[str, StepResult] = {}

        # Pre-extract steps to get count
        self._steps = self._extract_steps()
        self._regular_steps = [(m, meta) for m, meta in self._steps if not meta.cleanup]
        self._cleanup_steps = [(m, meta) for m, meta in self._steps if meta.cleanup]

    async def run(self) -> ExecutionResult:
        """
        Execute the sequence.

        Returns:
            ExecutionResult containing all step results and overall status

        Raises:
            SequenceError: If the sequence cannot be executed
        """
        started_at = datetime.now()
        self._stopped = False

        # Get sequence metadata
        sequence_name = getattr(self._sequence, "name", self._sequence.__class__.__name__)
        sequence_version = getattr(self._sequence, "version", "1.0.0")

        # Initialize execution result
        result = ExecutionResult(
            sequence_name=sequence_name,
            sequence_version=sequence_version,
            status="running",
            overall_pass=True,
            started_at=started_at,
            parameters=self._parameters.copy(),
            steps=[],
        )

        # Use pre-extracted steps
        regular_steps = self._regular_steps
        cleanup_steps = self._cleanup_steps

        self._log("info", f"Starting sequence '{sequence_name}' v{sequence_version}")
        self._log("info", f"Found {len(regular_steps)} regular steps and {len(cleanup_steps)} cleanup steps")

        # Track if we encountered a failure (for cleanup execution)
        had_failure = False

        try:
            # Execute regular steps
            for step_method, step_meta in regular_steps:
                if self._stopped:
                    self._log("warning", "Sequence execution stopped by user")
                    result.status = "stopped"
                    break

                step_result = await self._execute_step(step_method, step_meta)
                result.steps.append(step_result)
                self._step_results[step_meta.name] = step_result

                if not step_result.passed and step_result.status != "skipped":
                    had_failure = True
                    result.overall_pass = False
                    if step_result.status == "failed":
                        # Stop execution on failure (except cleanup steps)
                        self._log("error", f"Step '{step_meta.name}' failed, stopping sequence")
                        result.status = "failed"
                        break

        except Exception as e:
            had_failure = True
            result.overall_pass = False
            result.status = "failed"
            self._log("error", f"Unexpected error during execution: {e}")

        finally:
            # Always execute cleanup steps
            if cleanup_steps:
                self._log("info", f"Executing {len(cleanup_steps)} cleanup steps")
                for step_method, step_meta in cleanup_steps:
                    try:
                        step_result = await self._execute_step(step_method, step_meta)
                        result.steps.append(step_result)
                        self._step_results[step_meta.name] = step_result
                    except Exception as e:
                        # Log cleanup errors but don't fail the sequence
                        self._log("error", f"Cleanup step '{step_meta.name}' failed: {e}")
                        cleanup_result = StepResult(
                            name=step_meta.name,
                            order=step_meta.order,
                            status="failed",
                            passed=False,
                            error=str(e),
                        )
                        result.steps.append(cleanup_result)

        # Finalize result
        result.completed_at = datetime.now()
        result.duration = (result.completed_at - started_at).total_seconds()

        if result.status == "running":
            result.status = "completed" if result.overall_pass else "failed"

        self._log(
            "info",
            f"Sequence completed: status={result.status}, "
            f"overall_pass={result.overall_pass}, duration={result.duration:.2f}s"
        )

        return result

    async def stop(self) -> None:
        """
        Request to stop the sequence execution.

        The current step will complete before execution stops.
        Cleanup steps will still run after stopping.
        """
        self._stopped = True
        self._log("warning", "Stop requested, will stop after current step completes")

    async def _execute_step(
        self, step_method: Callable, step_meta: StepMeta
    ) -> StepResult:
        """
        Execute a single step with timeout and retry handling.

        Args:
            step_method: The step method to execute
            step_meta: Step metadata

        Returns:
            StepResult containing the execution result
        """
        self._current_step = step_meta.name

        # Check condition
        if not self._check_condition(step_meta.condition):
            self._log("info", f"Skipping step '{step_meta.name}' (condition '{step_meta.condition}' not met)")
            return StepResult(
                name=step_meta.name,
                order=step_meta.order,
                status="skipped",
                passed=True,  # Skipped steps are considered passed
            )

        # Notify step start
        if self._on_step_start:
            try:
                self._on_step_start(step_meta.name, step_meta)
            except Exception as e:
                self._log("warning", f"on_step_start callback failed: {e}")

        # Yield to event loop to allow IPC messages to be sent
        await asyncio.sleep(0)

        started_at = datetime.now()
        step_result = StepResult(
            name=step_meta.name,
            order=step_meta.order,
            status="running",
            passed=False,
            started_at=started_at,
        )

        self._log("info", f"Executing step '{step_meta.name}' (timeout={step_meta.timeout}s, retry={step_meta.retry})")

        last_error: Optional[Exception] = None
        attempts = step_meta.retry + 1  # retry=0 means 1 attempt

        for attempt in range(attempts):
            if attempt > 0:
                self._log("info", f"Retrying step '{step_meta.name}' (attempt {attempt + 1}/{attempts})")

            try:
                # Execute with timeout
                if asyncio.iscoroutinefunction(step_method):
                    method_result = await asyncio.wait_for(
                        step_method(),
                        timeout=step_meta.timeout
                    )
                else:
                    # Support synchronous methods
                    loop = asyncio.get_running_loop()
                    method_result = await asyncio.wait_for(
                        loop.run_in_executor(None, step_method),
                        timeout=step_meta.timeout
                    )

                # Step succeeded
                step_result.status = "completed"
                step_result.passed = True
                step_result.result = self._normalize_result(method_result)
                step_result.completed_at = datetime.now()
                step_result.duration = (step_result.completed_at - started_at).total_seconds()

                self._log("info", f"Step '{step_meta.name}' completed successfully in {step_result.duration:.2f}s")
                break

            except asyncio.TimeoutError:
                elapsed = (datetime.now() - started_at).total_seconds()
                last_error = StepTimeoutError(
                    message=f"Step '{step_meta.name}' timed out",
                    step_name=step_meta.name,
                    timeout=step_meta.timeout,
                    elapsed=elapsed,
                )
                self._log("error", f"Step '{step_meta.name}' timed out after {elapsed:.2f}s")

            except TestFailure as e:
                last_error = e
                self._log("warning", f"Step '{step_meta.name}' test failed: {e}")
                # Test failures don't retry
                break

            except TestSkipped as e:
                # Step was skipped during execution
                step_result.status = "skipped"
                step_result.passed = True
                step_result.completed_at = datetime.now()
                step_result.duration = (step_result.completed_at - started_at).total_seconds()
                step_result.result = {"reason": str(e)}
                self._log("info", f"Step '{step_meta.name}' was skipped: {e}")
                break

            except Exception as e:
                last_error = e
                self._log("error", f"Step '{step_meta.name}' error: {type(e).__name__}: {e}")

        # Handle final failure state
        if step_result.status == "running":
            step_result.status = "failed"
            step_result.passed = False
            step_result.completed_at = datetime.now()
            step_result.duration = (step_result.completed_at - started_at).total_seconds()
            step_result.error = str(last_error) if last_error else "Unknown error"

            # Notify error
            if self._on_error and last_error:
                try:
                    self._on_error(step_meta.name, last_error)
                except Exception as e:
                    self._log("warning", f"on_error callback failed: {e}")

        # Notify step complete
        if self._on_step_complete:
            try:
                self._on_step_complete(step_meta.name, step_result)
            except Exception as e:
                self._log("warning", f"on_step_complete callback failed: {e}")

        # Yield to event loop to allow IPC messages to be sent
        # This ensures real-time updates reach clients during execution
        await asyncio.sleep(0)

        self._current_step = None
        return step_result

    def _check_condition(self, condition: Optional[str]) -> bool:
        """
        Check if a step's condition is met.

        Args:
            condition: Parameter name to check, or None for unconditional

        Returns:
            True if the condition is met (or no condition), False otherwise
        """
        if condition is None:
            return True

        # Check if condition parameter exists and is truthy
        if condition not in self._parameters:
            self._log("warning", f"Condition parameter '{condition}' not found in parameters")
            return False

        value = self._parameters.get(condition)
        return bool(value)

    def _extract_steps(self) -> List[Tuple[Callable, StepMeta]]:
        """
        Extract all step methods from the sequence instance.

        Returns:
            List of (method, metadata) tuples sorted by order
        """
        steps: List[Tuple[Callable, StepMeta]] = []

        for name in dir(self._sequence):
            if name.startswith("_"):
                continue

            try:
                method = getattr(self._sequence, name)
                if callable(method) and hasattr(method, "_step_meta"):
                    step_meta: StepMeta = method._step_meta
                    steps.append((method, step_meta))
            except Exception as e:
                self._log("warning", f"Error extracting step '{name}': {e}")

        # Sort by order
        steps.sort(key=lambda x: x[1].order)

        return steps

    def _normalize_result(self, result: Any) -> Optional[Dict[str, Any]]:
        """
        Normalize step result to dictionary format.

        Args:
            result: Raw result from step method

        Returns:
            Dictionary representation of the result
        """
        if result is None:
            return None

        if isinstance(result, dict):
            return result

        # Handle common return types
        if hasattr(result, "to_dict"):
            return result.to_dict()

        if hasattr(result, "__dict__"):
            return {
                k: v for k, v in result.__dict__.items()
                if not k.startswith("_")
            }

        # Wrap primitive values
        return {"value": result}

    def _log(self, level: str, message: str) -> None:
        """
        Log a message and notify callback.

        Args:
            level: Log level ("debug", "info", "warning", "error")
            message: Log message
        """
        # Log using standard logger
        log_func = getattr(logger, level, logger.info)
        log_func(message)

        # Notify callback
        if self._on_log:
            try:
                self._on_log(level, message)
            except Exception as e:
                logger.warning(f"on_log callback failed: {e}")

    @property
    def current_step(self) -> Optional[str]:
        """Get the name of the currently executing step."""
        return self._current_step

    @property
    def is_stopped(self) -> bool:
        """Check if stop has been requested."""
        return self._stopped

    def get_step_result(self, step_name: str) -> Optional[StepResult]:
        """
        Get the result of a specific step.

        Args:
            step_name: Name of the step

        Returns:
            StepResult if the step has been executed, None otherwise
        """
        return self._step_results.get(step_name)

    @property
    def total_steps(self) -> int:
        """Get the total number of steps (regular + cleanup)."""
        return len(self._regular_steps) + len(self._cleanup_steps)

    @property
    def regular_step_count(self) -> int:
        """Get the number of regular (non-cleanup) steps."""
        return len(self._regular_steps)
