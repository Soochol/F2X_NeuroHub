"""
CLI-based sequence worker using subprocess.

Runs SDK-based sequences via subprocess and parses JSON Lines output
for real-time event forwarding to IPC.

Usage:
    worker = CLISequenceWorker(
        batch_id="batch_1",
        sequence_name="psa_sensor_test",
        ipc_client=ipc,
    )
    execution_id = await worker.start(config)
    # ... events are forwarded automatically ...
    await worker.wait()
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class CLISequenceWorker:
    """
    Runs sequence via subprocess and parses JSON Lines output.

    Replaces internal executor with subprocess execution:
    - Spawns sequence as: python -m sequences.{name}.main --start --config '...'
    - Parses JSON Lines output for real-time events
    - Forwards events to IPC for WebSocket broadcast
    """

    def __init__(
        self,
        batch_id: str,
        sequence_name: str,
        sequences_dir: Path = Path("sequences"),
        python_executable: Optional[str] = None,
        on_step_start: Optional[Callable] = None,
        on_step_complete: Optional[Callable] = None,
        on_measurement: Optional[Callable] = None,
        on_log: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_sequence_complete: Optional[Callable] = None,
        on_status: Optional[Callable] = None,
        on_input_request: Optional[Callable] = None,
    ):
        """
        Initialize CLI sequence worker.

        Args:
            batch_id: Batch identifier
            sequence_name: Name of the sequence package
            sequences_dir: Directory containing sequences
            python_executable: Python executable path (default: sys.executable)
            on_*: Event callbacks
        """
        self._batch_id = batch_id
        self._sequence_name = sequence_name
        self._sequences_dir = sequences_dir
        self._python = python_executable or sys.executable

        # Callbacks
        self._on_step_start = on_step_start
        self._on_step_complete = on_step_complete
        self._on_measurement = on_measurement
        self._on_log = on_log
        self._on_error = on_error
        self._on_sequence_complete = on_sequence_complete
        self._on_status = on_status
        self._on_input_request = on_input_request

        # Process state
        self._process: Optional[asyncio.subprocess.Process] = None
        self._running = False
        self._execution_id: Optional[str] = None
        self._output_task: Optional[asyncio.Task] = None
        self._stderr_task: Optional[asyncio.Task] = None

        # Result tracking
        self._step_results: List[Dict[str, Any]] = []
        self._measurements: Dict[str, Any] = {}
        self._final_result: Optional[Dict[str, Any]] = None

    @property
    def running(self) -> bool:
        """Check if sequence is running."""
        return self._running

    @property
    def execution_id(self) -> Optional[str]:
        """Get current execution ID."""
        return self._execution_id

    async def start(self, config: Dict[str, Any]) -> str:
        """
        Start sequence execution.

        Args:
            config: Execution configuration including:
                - execution_id: Optional execution ID
                - wip_id: WIP identifier
                - process_id: Process number
                - operator_id: Operator ID
                - hardware: Hardware configuration
                - parameters: Sequence parameters

        Returns:
            Execution ID

        Raises:
            RuntimeError: If sequence already running
        """
        if self._running:
            raise RuntimeError("Sequence already running")

        # Generate or use provided execution ID
        import uuid
        self._execution_id = config.get("execution_id") or str(uuid.uuid4())[:8]
        config["execution_id"] = self._execution_id

        # Reset state
        self._step_results = []
        self._measurements = {}
        self._final_result = None

        # Build command
        config_json = json.dumps(config, ensure_ascii=False)
        cmd = [
            self._python,
            "-m",
            f"sequences.{self._sequence_name}.main",
            "--start",
            "--config",
            config_json,
        ]

        logger.info(f"Starting CLI sequence: {self._sequence_name} (exec_id={self._execution_id})")
        logger.debug(f"Command: {cmd[0]} -m {cmd[2]} --start --config '...'")

        # Start subprocess
        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._sequences_dir.parent),
            )
            self._running = True

            # Start output parser tasks
            self._output_task = asyncio.create_task(self._parse_stdout())
            self._stderr_task = asyncio.create_task(self._parse_stderr())

            logger.info(f"CLI sequence started: pid={self._process.pid}")
            return self._execution_id

        except Exception as e:
            logger.error(f"Failed to start CLI sequence: {e}")
            self._running = False
            raise

    async def stop(self) -> None:
        """Stop running sequence."""
        if not self._process or not self._running:
            return

        logger.info(f"Stopping CLI sequence: {self._execution_id}")

        # Send stop command via stdin
        try:
            if self._process.stdin:
                stop_cmd = json.dumps({"type": "command", "action": "stop"})
                self._process.stdin.write(f"{stop_cmd}\n".encode())
                await self._process.stdin.drain()
        except Exception as e:
            logger.warning(f"Failed to send stop command: {e}")

        # Wait briefly for graceful shutdown
        try:
            await asyncio.wait_for(self._process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Sequence didn't stop gracefully, terminating")
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                logger.warning("Sequence didn't terminate, killing")
                self._process.kill()

        self._running = False

    async def send_input(self, request_id: str, value: Any) -> None:
        """
        Send input response to running sequence.

        Args:
            request_id: The request ID to respond to
            value: The input value
        """
        if not self._process or not self._process.stdin:
            logger.warning("Cannot send input: process not running")
            return

        response = json.dumps({
            "type": "input_response",
            "data": {
                "id": request_id,
                "value": value,
            }
        })

        try:
            self._process.stdin.write(f"{response}\n".encode())
            await self._process.stdin.drain()
            logger.debug(f"Sent input response: {request_id} = {value}")
        except Exception as e:
            logger.error(f"Failed to send input response: {e}")

    async def wait(self) -> Optional[Dict[str, Any]]:
        """
        Wait for sequence to complete.

        Returns:
            Final result dict or None if failed
        """
        if not self._process:
            return self._final_result

        # Wait for output parser to finish
        if self._output_task:
            await self._output_task

        # Wait for process to exit
        return_code = await self._process.wait()
        self._running = False

        logger.info(f"CLI sequence completed: return_code={return_code}")

        return self._final_result

    async def _parse_stdout(self) -> None:
        """Parse JSON Lines output from stdout."""
        try:
            while self._running and self._process and self._process.stdout:
                line = await self._process.stdout.readline()
                if not line:
                    break

                line_str = line.decode().strip()
                if not line_str:
                    continue

                try:
                    message = json.loads(line_str)
                    await self._handle_message(message)
                except json.JSONDecodeError:
                    # Non-JSON output - treat as log
                    logger.debug(f"Non-JSON stdout: {line_str}")
                    if self._on_log:
                        await self._safe_callback(
                            self._on_log,
                            "debug",
                            line_str,
                        )

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Error parsing stdout: {e}")

    async def _parse_stderr(self) -> None:
        """Parse stderr output (usually errors/warnings)."""
        try:
            while self._running and self._process and self._process.stderr:
                line = await self._process.stderr.readline()
                if not line:
                    break

                line_str = line.decode().strip()
                if line_str:
                    logger.warning(f"Sequence stderr: {line_str}")
                    if self._on_log:
                        await self._safe_callback(
                            self._on_log,
                            "warning",
                            f"[stderr] {line_str}",
                        )

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Error parsing stderr: {e}")

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle parsed JSON message.

        Args:
            message: Parsed JSON message with 'type' and 'data' fields
        """
        msg_type = message.get("type")
        data = message.get("data", {})
        timestamp = message.get("timestamp")

        logger.debug(f"Received message: type={msg_type}")

        if msg_type == "step_start":
            step_name = data.get("step", "")
            index = data.get("index", 0)
            total = data.get("total", 0)

            # Track step
            self._step_results.append({
                "name": step_name,
                "index": index,
                "status": "running",
                "started_at": timestamp,
            })

            if self._on_step_start:
                await self._safe_callback(
                    self._on_step_start,
                    step_name,
                    index,
                    total,
                    self._execution_id,
                )

        elif msg_type == "step_complete":
            step_name = data.get("step", "")
            index = data.get("index", 0)
            passed = data.get("passed", False)
            duration = data.get("duration", 0)
            measurements = data.get("measurements", {})
            error = data.get("error")

            # Update step result
            for step in self._step_results:
                if step.get("name") == step_name:
                    step.update({
                        "status": "completed" if passed else "failed",
                        "passed": passed,
                        "duration": duration,
                        "measurements": measurements,
                        "error": error,
                        "completed_at": timestamp,
                    })
                    break

            # Merge measurements
            self._measurements.update(measurements)

            if self._on_step_complete:
                await self._safe_callback(
                    self._on_step_complete,
                    step_name,
                    index,
                    passed,
                    duration,
                    data,
                    self._execution_id,
                )

        elif msg_type == "measurement":
            name = data.get("name", "")
            value = data.get("value")
            unit = data.get("unit", "")

            self._measurements[name] = {
                "value": value,
                "unit": unit,
                "passed": data.get("passed"),
                "min": data.get("min"),
                "max": data.get("max"),
            }

            if self._on_measurement:
                await self._safe_callback(
                    self._on_measurement,
                    name,
                    value,
                    unit,
                    data,
                )

        elif msg_type == "sequence_complete":
            overall_pass = data.get("overall_pass", False)
            duration = data.get("duration", 0)
            steps = data.get("steps", [])
            measurements = data.get("measurements", {})
            error = data.get("error")

            # Store final result
            self._final_result = {
                "overall_pass": overall_pass,
                "duration": duration,
                "steps": steps or self._step_results,
                "measurements": measurements or self._measurements,
                "error": error,
                "execution_id": self._execution_id,
            }

            if self._on_sequence_complete:
                await self._safe_callback(
                    self._on_sequence_complete,
                    self._execution_id,
                    overall_pass,
                    duration,
                    self._final_result,
                )

        elif msg_type == "log":
            level = data.get("level", "info")
            msg = data.get("message", "")

            if self._on_log:
                await self._safe_callback(self._on_log, level, msg)

        elif msg_type == "error":
            code = data.get("code", "ERROR")
            msg = data.get("message", "")
            step = data.get("step")

            if self._on_error:
                await self._safe_callback(self._on_error, code, msg, step)

        elif msg_type == "status":
            status = data.get("status", "")
            progress = data.get("progress", 0)
            current_step = data.get("current_step")

            if self._on_status:
                await self._safe_callback(
                    self._on_status,
                    status,
                    progress,
                    current_step,
                    self._execution_id,
                )

        elif msg_type == "input_request":
            request_id = data.get("id", "")
            prompt = data.get("prompt", "")
            input_type = data.get("input_type", "confirm")

            if self._on_input_request:
                await self._safe_callback(
                    self._on_input_request,
                    request_id,
                    prompt,
                    input_type,
                    data,
                )

        else:
            logger.debug(f"Unknown message type: {msg_type}")

    async def _safe_callback(self, callback: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Safely call a callback, handling both sync and async.

        Args:
            callback: Callback function
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Callback error: {e}")
