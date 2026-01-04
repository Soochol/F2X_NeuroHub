"""
IPC Client for Station Service batch worker processes.

Provides ZeroMQ-based communication with the master process.
- DEALER socket for REQ/REP command handling
- PUB socket for publishing events to master
"""

import asyncio
import json
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional

import zmq
import zmq.asyncio

from station_service.core.exceptions import IPCError, IPCConnectionError
from station_service.ipc.messages import (
    CommandType,
    IPCCommand,
    IPCEvent,
    IPCResponse,
)

logger = logging.getLogger(__name__)

# Type alias for command callback
CommandCallback = Callable[[IPCCommand], Coroutine[Any, Any, IPCResponse]]


class IPCClient:
    """
    IPC Client for batch worker communication with master process.

    Uses two ZeroMQ sockets:
    - DEALER: Sends requests and receives responses from master ROUTER
    - PUB: Publishes events to master SUB socket

    Usage:
        client = IPCClient(
            batch_id="batch_1",
            router_address="tcp://127.0.0.1:5555",
            sub_address="tcp://127.0.0.1:5557",
        )
        await client.connect()

        # Publish events
        await client.publish_event(IPCEvent.log(batch_id, "info", "Hello"))

        # Handle incoming commands
        client.on_command(handle_command)

        await client.disconnect()
    """

    def __init__(
        self,
        batch_id: str,
        router_address: str = "tcp://127.0.0.1:5555",
        sub_address: str = "tcp://127.0.0.1:5557",
    ) -> None:
        """
        Initialize the IPC client.

        Args:
            batch_id: The batch ID this client represents
            router_address: Address of master's ROUTER socket
            sub_address: Address of master's SUB socket
        """
        self._batch_id = batch_id
        self._router_address = router_address
        self._sub_address = sub_address

        self._context: Optional[zmq.asyncio.Context] = None
        self._dealer_socket: Optional[zmq.asyncio.Socket] = None
        self._pub_socket: Optional[zmq.asyncio.Socket] = None

        self._connected = False
        self._command_task: Optional[asyncio.Task] = None
        self._command_callbacks: list[CommandCallback] = []

    @property
    def batch_id(self) -> str:
        """Get the batch ID."""
        return self._batch_id

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    async def connect(self) -> None:
        """
        Connect to the master process.

        Establishes DEALER and PUB socket connections and registers with master.

        Raises:
            IPCConnectionError: If connection fails
        """
        if self._connected:
            logger.warning(f"IPC Client {self._batch_id} already connected")
            return

        try:
            self._context = zmq.asyncio.Context()

            # DEALER socket for sending/receiving commands
            self._dealer_socket = self._context.socket(zmq.DEALER)
            # Set identity for routing
            self._dealer_socket.setsockopt_string(zmq.IDENTITY, self._batch_id)
            self._dealer_socket.connect(self._router_address)

            # PUB socket for publishing events
            self._pub_socket = self._context.socket(zmq.PUB)
            self._pub_socket.connect(self._sub_address)

            # Allow time for connection
            await asyncio.sleep(0.1)

            # Register with master
            await self._register()

            self._connected = True

            # Start command listener
            self._command_task = asyncio.create_task(self._command_loop())

            logger.info(
                f"IPC Client {self._batch_id} connected - "
                f"DEALER: {self._router_address}, PUB: {self._sub_address}"
            )

        except Exception as e:
            await self._cleanup()
            raise IPCConnectionError(self._router_address, str(e))

    async def disconnect(self) -> None:
        """Disconnect from the master process."""
        if not self._connected:
            return

        self._connected = False

        # Send unregister message
        try:
            await self._unregister()
        except Exception as e:
            logger.warning(f"Error unregistering: {e}")

        await self._cleanup()

        logger.info(f"IPC Client {self._batch_id} disconnected")

    async def _cleanup(self) -> None:
        """Clean up resources."""
        # Cancel command listener
        if self._command_task:
            self._command_task.cancel()
            try:
                await self._command_task
            except asyncio.CancelledError:
                pass
            self._command_task = None

        # Close sockets
        if self._dealer_socket:
            self._dealer_socket.close(linger=0)
            self._dealer_socket = None

        if self._pub_socket:
            self._pub_socket.close(linger=0)
            self._pub_socket = None

        # Terminate context
        if self._context:
            self._context.term()
            self._context = None

    async def _register(self) -> None:
        """Register with master process."""
        message = json.dumps({
            "type": "REGISTER",
            "batch_id": self._batch_id,
        })

        # Send via DEALER (which acts like REQ to ROUTER)
        await self._dealer_socket.send_multipart([
            b"",
            message.encode("utf-8"),
        ])

        # Wait for acknowledgment
        frames = await self._dealer_socket.recv_multipart()
        if len(frames) >= 2:
            response = json.loads(frames[1].decode("utf-8"))
            if response.get("status") != "ok":
                raise IPCError(
                    f"Registration failed: {response.get('message', 'Unknown error')}",
                    "REGISTRATION_FAILED",
                )

    async def _unregister(self) -> None:
        """Unregister from master process."""
        message = json.dumps({
            "type": "UNREGISTER",
            "batch_id": self._batch_id,
        })

        await self._dealer_socket.send_multipart([
            b"",
            message.encode("utf-8"),
        ])

    def on_command(self, callback: CommandCallback) -> None:
        """
        Register a command callback.

        Args:
            callback: Async function to handle incoming commands
        """
        self._command_callbacks.append(callback)

    def off_command(self, callback: CommandCallback) -> bool:
        """
        Unregister a command callback.

        Args:
            callback: The callback to remove

        Returns:
            True if callback was found and removed
        """
        try:
            self._command_callbacks.remove(callback)
            return True
        except ValueError:
            return False

    async def publish_event(self, event: IPCEvent) -> None:
        """
        Publish an event to the master process.

        Args:
            event: The event to publish

        Raises:
            IPCError: If not connected
        """
        if not self._connected:
            raise IPCError("IPC Client not connected", "NOT_CONNECTED")

        logger.info(f"[IPC Client {self._batch_id}] Publishing event: {event.type.value}")
        await self._pub_socket.send_string(event.serialize())

    async def send_response(self, response: IPCResponse) -> None:
        """
        Send a response to the master process.

        Args:
            response: The response to send
        """
        if not self._connected:
            raise IPCError("IPC Client not connected", "NOT_CONNECTED")

        try:
            serialized = response.serialize()
        except TypeError as e:
            # Debug: log the problematic data
            import json
            logger.error(f"Failed to serialize response: {e}")
            logger.error(f"Response object: status={response.status!r}, request_id={response.request_id!r}, error={response.error!r}")
            logger.error(f"Response data type: {type(response.data)}")
            logger.error(f"Response data: {response.data}")
            # Try to identify which field is problematic
            if response.data:
                for key, value in response.data.items():
                    try:
                        json.dumps(value)
                        logger.error(f"  {key}: {type(value).__name__} = {value!r} (OK)")
                    except TypeError as inner_e:
                        logger.error(f"  {key}: {type(value).__name__} = {value!r} (FAIL: {inner_e})")
            # Try serializing just status and request_id
            try:
                json.dumps({"status": response.status, "request_id": response.request_id})
                logger.error("status + request_id: OK")
            except TypeError as inner_e:
                logger.error(f"status + request_id: FAIL: {inner_e}")
            raise

        await self._dealer_socket.send_multipart([
            b"",
            serialized.encode("utf-8"),
        ])

    async def _command_loop(self) -> None:
        """Background task to receive and handle commands."""
        logger.debug(f"Command loop started for {self._batch_id}")

        while self._connected:
            try:
                # Poll with timeout
                events = await self._dealer_socket.poll(timeout=100)
                if not events:
                    continue

                # Receive command (DEALER frame format: [empty, message])
                frames = await self._dealer_socket.recv_multipart()
                if len(frames) < 2:
                    continue

                message = frames[1].decode("utf-8")
                command = IPCCommand.deserialize(message)

                logger.debug(f"Received command: {command.type.value}")

                # Dispatch to callbacks
                response: Optional[IPCResponse] = None
                for callback in self._command_callbacks:
                    try:
                        response = await callback(command)
                        if response:
                            break
                    except Exception as e:
                        logger.error(f"Command callback error: {e}")
                        response = IPCResponse.error(command.request_id, str(e))
                        break

                # Send response if any callback returned one
                if response:
                    await self.send_response(response)
                else:
                    # No handler returned a response, send generic error
                    await self.send_response(
                        IPCResponse.error(command.request_id, "No handler for command")
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                import traceback
                logger.error(f"Command loop error: {e}\n{traceback.format_exc()}")
                await asyncio.sleep(0.1)

        logger.debug(f"Command loop stopped for {self._batch_id}")

    # Convenience methods for common events

    async def log(self, level: str, message: str) -> None:
        """Publish a log event."""
        await self.publish_event(IPCEvent.log(self._batch_id, level, message))

    async def error(self, code: str, message: str, step: Optional[str] = None) -> None:
        """Publish an error event."""
        await self.publish_event(IPCEvent.error(self._batch_id, code, message, step))

    async def step_start(
        self,
        step_name: str,
        step_index: int,
        total_steps: int,
        execution_id: str = "",
        step_names: Optional[List[str]] = None,
    ) -> None:
        """Publish a step start event.

        Args:
            step_names: List of all step names from manifest (sent on first step only)
        """
        await self.publish_event(
            IPCEvent.step_start(
                self._batch_id, step_name, step_index, total_steps, execution_id, step_names
            )
        )

    async def step_complete(
        self,
        step_name: str,
        step_index: int,
        duration: float,
        passed: bool,
        result: Optional[Dict[str, Any]] = None,
        execution_id: str = "",
    ) -> None:
        """Publish a step complete event."""
        await self.publish_event(
            IPCEvent.step_complete(
                self._batch_id, step_name, step_index, duration, passed, result, execution_id
            )
        )

    async def sequence_complete(
        self,
        execution_id: str,
        overall_pass: bool,
        duration: float,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish a sequence complete event."""
        await self.publish_event(
            IPCEvent.sequence_complete(
                self._batch_id, execution_id, overall_pass, duration, result
            )
        )

    async def status_update(self, status: Dict[str, Any]) -> None:
        """Publish a status update event."""
        await self.publish_event(IPCEvent.status_update(self._batch_id, status))

    async def barcode_scanned(self, barcode: str, scanner_id: str = "") -> None:
        """Publish a barcode scanned event."""
        await self.publish_event(IPCEvent.barcode_scanned(self._batch_id, barcode, scanner_id))

    async def wip_process_complete(
        self,
        wip_id: str,
        process_id: int,
        result: str,
        wip_status: Optional[str] = None,
        can_convert: bool = False,
    ) -> None:
        """Publish a WIP process complete event."""
        await self.publish_event(
            IPCEvent.wip_process_complete(
                self._batch_id, wip_id, process_id, result, wip_status, can_convert
            )
        )
