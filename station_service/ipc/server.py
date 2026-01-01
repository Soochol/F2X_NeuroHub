"""
IPC Server for Station Service master process.

Provides ZeroMQ-based communication with batch worker processes.
- ROUTER socket for REQ/REP command handling
- SUB socket for receiving events from workers
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, Optional

import zmq
import zmq.asyncio

from station_service.core.exceptions import IPCError, IPCTimeoutError
from station_service.ipc.messages import (
    CommandType,
    IPCCommand,
    IPCEvent,
    IPCResponse,
)

logger = logging.getLogger(__name__)

# Default ports
DEFAULT_ROUTER_PORT = 5555
DEFAULT_PUB_PORT = 5556
DEFAULT_SUB_PORT = 5557

# Type alias for event callback
EventCallback = Callable[[IPCEvent], Coroutine[Any, Any, None]]


class IPCServer:
    """
    IPC Server for master process communication with batch workers.

    Uses three ZeroMQ sockets:
    - ROUTER: Receives REQ messages from workers and sends REP responses
    - PUB: Publishes commands to all workers (optional, for broadcast)
    - SUB: Receives events from worker PUB sockets

    Usage:
        server = IPCServer(router_port=5555, sub_port=5557)
        await server.start()

        # Send command to specific worker
        response = await server.send_command(batch_id, CommandType.GET_STATUS)

        # Register event callback
        server.on_event(handle_event)

        await server.stop()
    """

    def __init__(
        self,
        router_port: int = DEFAULT_ROUTER_PORT,
        sub_port: int = DEFAULT_SUB_PORT,
        host: str = "127.0.0.1",
    ) -> None:
        """
        Initialize the IPC server.

        Args:
            router_port: Port for ROUTER socket (command responses)
            sub_port: Port for SUB socket (event subscription)
            host: Host address to bind to
        """
        self._host = host
        self._router_port = router_port
        self._sub_port = sub_port

        self._context: Optional[zmq.asyncio.Context] = None
        self._router_socket: Optional[zmq.asyncio.Socket] = None
        self._sub_socket: Optional[zmq.asyncio.Socket] = None

        self._running = False
        self._event_task: Optional[asyncio.Task] = None
        self._router_task: Optional[asyncio.Task] = None
        self._event_callbacks: list[EventCallback] = []

        # Map batch_id to their ZMQ identity for routing
        self._worker_identities: Dict[str, bytes] = {}

        # Pending requests waiting for response
        self._pending_requests: Dict[str, asyncio.Future] = {}

    @property
    def router_address(self) -> str:
        """Get the ROUTER socket address."""
        return f"tcp://{self._host}:{self._router_port}"

    @property
    def sub_address(self) -> str:
        """Get the SUB socket address."""
        return f"tcp://{self._host}:{self._sub_port}"

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    async def start(self) -> None:
        """
        Start the IPC server.

        Binds ROUTER and SUB sockets and starts the event listener.
        """
        if self._running:
            logger.warning("IPC Server already running")
            return

        self._context = zmq.asyncio.Context()

        # ROUTER socket for receiving commands from workers
        self._router_socket = self._context.socket(zmq.ROUTER)
        self._router_socket.setsockopt(zmq.ROUTER_MANDATORY, 1)
        self._router_socket.bind(f"tcp://*:{self._router_port}")

        # SUB socket for receiving events from workers
        self._sub_socket = self._context.socket(zmq.SUB)
        self._sub_socket.bind(f"tcp://*:{self._sub_port}")
        self._sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self._running = True

        # Start event listener
        self._event_task = asyncio.create_task(self._event_loop())

        # Start router message handler for worker registration and responses
        self._router_task = asyncio.create_task(self._handle_router_messages())

        logger.info(
            f"IPC Server started - ROUTER: {self.router_address}, SUB: {self.sub_address}"
        )

    async def stop(self) -> None:
        """Stop the IPC server and close all sockets."""
        if not self._running:
            return

        self._running = False

        # Cancel event listener
        if self._event_task:
            self._event_task.cancel()
            try:
                await self._event_task
            except asyncio.CancelledError:
                pass
            self._event_task = None

        # Cancel router handler
        if self._router_task:
            self._router_task.cancel()
            try:
                await self._router_task
            except asyncio.CancelledError:
                pass
            self._router_task = None

        # Cancel pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()

        # Close sockets
        if self._router_socket:
            self._router_socket.close(linger=0)
            self._router_socket = None

        if self._sub_socket:
            self._sub_socket.close(linger=0)
            self._sub_socket = None

        # Terminate context
        if self._context:
            self._context.term()
            self._context = None

        self._worker_identities.clear()

        logger.info("IPC Server stopped")

    def on_event(self, callback: EventCallback) -> None:
        """
        Register an event callback.

        Args:
            callback: Async function to call when an event is received
        """
        self._event_callbacks.append(callback)

    def off_event(self, callback: EventCallback) -> bool:
        """
        Unregister an event callback.

        Args:
            callback: The callback to remove

        Returns:
            True if callback was found and removed
        """
        try:
            self._event_callbacks.remove(callback)
            return True
        except ValueError:
            return False

    async def send_command(
        self,
        batch_id: str,
        command_type: CommandType,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 5000,  # ms
    ) -> IPCResponse:
        """
        Send a command to a specific batch worker.

        Args:
            batch_id: The batch ID to send to
            command_type: The command type
            params: Command parameters
            timeout: Response timeout in milliseconds

        Returns:
            IPCResponse from the worker

        Raises:
            IPCError: If worker not found or communication fails
            IPCTimeoutError: If response times out
        """
        if not self._running:
            raise IPCError("IPC Server not running", "IPC_NOT_RUNNING")

        if batch_id not in self._worker_identities:
            raise IPCError(f"Worker for batch '{batch_id}' not connected", "WORKER_NOT_FOUND")

        command = IPCCommand(
            type=command_type,
            batch_id=batch_id,
            params=params or {},
        )

        # Create future for response
        loop = asyncio.get_running_loop()
        future: asyncio.Future[IPCResponse] = loop.create_future()
        self._pending_requests[command.request_id] = future

        try:
            # Send command via ROUTER socket
            identity = self._worker_identities[batch_id]
            await self._router_socket.send_multipart([
                identity,
                b"",
                command.serialize().encode("utf-8"),
            ])

            # Wait for response with timeout
            response = await asyncio.wait_for(
                future,
                timeout=timeout / 1000,  # Convert to seconds
            )
            return response

        except asyncio.TimeoutError:
            raise IPCTimeoutError(f"send_command:{command_type.value}", timeout)

        finally:
            self._pending_requests.pop(command.request_id, None)

    async def broadcast_command(
        self,
        command_type: CommandType,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, IPCResponse]:
        """
        Broadcast a command to all connected workers.

        Args:
            command_type: The command type
            params: Command parameters

        Returns:
            Dict mapping batch_id to their responses
        """
        responses: Dict[str, IPCResponse] = {}

        tasks = []
        for batch_id in self._worker_identities.keys():
            task = asyncio.create_task(
                self.send_command(batch_id, command_type, params)
            )
            tasks.append((batch_id, task))

        for batch_id, task in tasks:
            try:
                responses[batch_id] = await task
            except Exception as e:
                logger.error(f"Error sending command to {batch_id}: {e}")
                responses[batch_id] = IPCResponse.error("broadcast", str(e))

        return responses

    def register_worker(self, batch_id: str, identity: bytes) -> None:
        """
        Register a worker's ZMQ identity.

        Called when a worker first connects.

        Args:
            batch_id: The batch ID
            identity: ZMQ socket identity
        """
        self._worker_identities[batch_id] = identity
        logger.info(f"Worker registered: {batch_id}")

    def unregister_worker(self, batch_id: str) -> None:
        """
        Unregister a worker.

        Args:
            batch_id: The batch ID to unregister
        """
        self._worker_identities.pop(batch_id, None)
        logger.info(f"Worker unregistered: {batch_id}")

    def is_worker_connected(self, batch_id: str) -> bool:
        """
        Check if a worker is connected.

        Args:
            batch_id: The batch ID to check

        Returns:
            True if worker is connected
        """
        return batch_id in self._worker_identities

    async def wait_for_worker(
        self,
        batch_id: str,
        timeout: float = 10.0,
        poll_interval: float = 0.1,
    ) -> bool:
        """
        Wait for a worker to connect and register.

        Args:
            batch_id: The batch ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Time between checks in seconds

        Returns:
            True if worker connected within timeout

        Raises:
            IPCTimeoutError: If worker doesn't connect within timeout
        """
        elapsed = 0.0
        while elapsed < timeout:
            if self.is_worker_connected(batch_id):
                logger.info(f"Worker {batch_id} connected after {elapsed:.2f}s")
                return True
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise IPCTimeoutError(
            f"Worker '{batch_id}' failed to connect",
            timeout * 1000
        )

    async def _event_loop(self) -> None:
        """Background task to receive and dispatch events."""
        logger.info("[IPC Server] Event loop started - waiting for worker events on SUB socket")

        while self._running:
            try:
                # Poll with timeout to allow graceful shutdown
                events = await self._sub_socket.poll(timeout=100)
                if not events:
                    continue

                # Receive event message
                message = await self._sub_socket.recv_string()
                event = IPCEvent.deserialize(message)

                logger.info(f"[IPC Server] Received event: {event.type.value} from {event.batch_id}")

                # Dispatch to callbacks
                for callback in self._event_callbacks:
                    try:
                        await callback(event)
                    except Exception as e:
                        logger.error(f"Event callback error: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event loop error: {e}")
                await asyncio.sleep(0.1)

        logger.debug("Event loop stopped")

    async def _handle_router_messages(self) -> None:
        """
        Background task to handle ROUTER socket messages.

        Processes registration requests and command responses.
        """
        while self._running:
            try:
                events = await self._router_socket.poll(timeout=100)
                if not events:
                    continue

                # ROUTER frame format: [identity, empty, message]
                frames = await self._router_socket.recv_multipart()
                if len(frames) < 3:
                    continue

                identity = frames[0]
                message = frames[2].decode("utf-8")

                # Try to parse as response
                try:
                    response = IPCResponse.deserialize(message)
                    if response.request_id in self._pending_requests:
                        future = self._pending_requests[response.request_id]
                        if not future.done():
                            future.set_result(response)
                except Exception:
                    # Not a response, might be a registration message
                    try:
                        data = __import__("json").loads(message)
                        if data.get("type") == "REGISTER":
                            batch_id = data.get("batch_id")
                            if batch_id:
                                self.register_worker(batch_id, identity)
                                # Send acknowledgment
                                await self._router_socket.send_multipart([
                                    identity,
                                    b"",
                                    b'{"status": "ok", "message": "registered"}',
                                ])
                    except Exception as e:
                        logger.error(f"Error handling router message: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Router handler error: {e}")
                await asyncio.sleep(0.1)
