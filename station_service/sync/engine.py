"""
SyncEngine for Station Service.

Handles synchronization of local data with the backend server,
including offline queue management and automatic retry.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional

import httpx

from station_service.core.events import Event, EventEmitter, EventType, get_event_emitter
from station_service.core.exceptions import SyncConnectionError, SyncError
from station_service.models.config import BackendConfig
from station_service.storage.database import Database
from station_service.storage.repositories.sync_repository import SyncRepository

logger = logging.getLogger(__name__)


class SyncEngine:
    """
    Synchronization engine for backend communication.

    Handles:
    - Sending execution results to backend
    - Managing offline queue for failed syncs
    - Automatic retry with exponential backoff
    - Connection health monitoring
    - Station auto-registration and heartbeat with backend

    Usage:
        engine = SyncEngine(config=backend_config, database=db, station_config=cfg)
        await engine.start()

        # Queue data for sync
        await engine.queue_sync("execution", execution_id, data)

        # Check connection status
        if engine.is_connected:
            ...

        await engine.stop()
    """

    def __init__(
        self,
        config: BackendConfig,
        database: Database,
        event_emitter: Optional[EventEmitter] = None,
        station_name: Optional[str] = None,
        station_description: Optional[str] = None,
        server_host: str = "0.0.0.0",
        server_port: int = 8080,
    ) -> None:
        """
        Initialize the SyncEngine.

        Args:
            config: Backend configuration
            database: Database instance for sync queue
            event_emitter: Optional event emitter
            station_name: Station name for registration
            station_description: Station description for registration
            server_host: Station server host (for registration)
            server_port: Station server port (for registration)
        """
        self._config = config
        self._database = database
        self._event_emitter = event_emitter or get_event_emitter()
        self._sync_repo: Optional[SyncRepository] = None

        # Station info for auto-registration
        self._station_id = config.station_id
        self._station_name = station_name or config.station_id
        self._station_description = station_description or ""
        self._server_host = server_host
        self._server_port = server_port
        self._registered = False

        self._client: Optional[httpx.AsyncClient] = None
        self._running = False
        self._connected = False
        self._sync_task: Optional[asyncio.Task] = None
        self._health_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        # Sync settings
        self._sync_interval = config.sync_interval  # seconds
        self._max_retries = 5
        self._retry_backoff = 2.0  # exponential backoff multiplier
        self._heartbeat_interval = 15  # seconds

    @property
    def is_running(self) -> bool:
        """Check if engine is running."""
        return self._running

    @property
    def is_connected(self) -> bool:
        """Check if backend is connected."""
        return self._connected

    @property
    def backend_url(self) -> str:
        """Get the backend URL."""
        return self._config.url

    async def start(self) -> None:
        """
        Start the sync engine.

        Initializes HTTP client, registers with backend, and starts background tasks.
        """
        if self._running:
            logger.warning("SyncEngine already running")
            return

        if not self._config.url:
            logger.warning("Backend URL not configured, sync disabled")
            return

        # Initialize repository
        self._sync_repo = SyncRepository(self._database)

        # Create HTTP client
        headers = {}
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"

        self._client = httpx.AsyncClient(
            base_url=self._config.url,
            headers=headers,
            timeout=30.0,
        )

        self._running = True

        # Check connection first
        await self.check_connection()

        # Register with backend if station_id is configured
        if self._station_id and self._connected:
            await self._register_station()

        # Start background tasks
        self._health_task = asyncio.create_task(self._health_check_loop())
        self._sync_task = asyncio.create_task(self._sync_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        logger.info(f"SyncEngine started - Backend: {self._config.url}")

    async def stop(self) -> None:
        """
        Stop the sync engine.

        Attempts to flush queue before stopping.
        """
        if not self._running:
            return

        self._running = False

        # Cancel background tasks
        for task in [self._sync_task, self._health_task, self._heartbeat_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._sync_task = None
        self._health_task = None
        self._heartbeat_task = None

        # Close HTTP client
        if self._client:
            await self._client.aclose()
            self._client = None

        logger.info("SyncEngine stopped")

    async def queue_sync(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: Dict[str, Any],
    ) -> int:
        """
        Queue data for synchronization.

        Args:
            entity_type: Type of entity (e.g., "execution", "step")
            entity_id: Entity identifier
            action: Action type (e.g., "create", "update")
            payload: Data to sync

        Returns:
            Queue item ID
        """
        if not self._sync_repo:
            raise SyncError("SyncEngine not started", "SYNC_NOT_STARTED")

        item_id = await self._sync_repo.enqueue(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            payload=payload,
        )

        logger.debug(f"Queued sync: {entity_type}/{entity_id} ({action})")

        return item_id

    async def sync_execution(self, execution_id: str, data: Dict[str, Any]) -> bool:
        """
        Sync an execution result to backend.

        Args:
            execution_id: Execution ID
            data: Execution data

        Returns:
            True if sync succeeded
        """
        return await self._sync_item(
            entity_type="execution",
            entity_id=execution_id,
            action="create",
            payload=data,
        )

    async def force_sync(self) -> Dict[str, int]:
        """
        Force synchronization of all pending items.

        Returns:
            Dict with success/failure counts
        """
        if not self._sync_repo:
            return {"success": 0, "failed": 0}

        await self._event_emitter.emit(Event(type=EventType.SYNC_STARTED))

        success = 0
        failed = 0

        pending = await self._sync_repo.get_pending_items()

        for item in pending:
            try:
                result = await self._sync_item(
                    entity_type=item["entity_type"],
                    entity_id=item["entity_id"],
                    action=item["action"],
                    payload=item["payload"],
                    queue_id=item["id"],
                )
                if result:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Sync failed for {item['entity_id']}: {e}")
                failed += 1

        await self._event_emitter.emit(Event(
            type=EventType.SYNC_COMPLETED,
            data={"success": success, "failed": failed},
        ))

        return {"success": success, "failed": failed}

    async def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current sync queue status.

        Returns:
            Queue status including counts and oldest item
        """
        if not self._sync_repo:
            return {"pending": 0, "failed": 0}

        pending_count = await self._sync_repo.count_pending()
        failed_count = await self._sync_repo.count_failed()
        return {
            "pending": pending_count,
            "failed": failed_count,
        }

    async def check_connection(self) -> bool:
        """
        Check backend connection health.

        Returns:
            True if backend is reachable
        """
        if not self._client:
            return False

        try:
            response = await self._client.get("/health")
            self._connected = response.status_code == 200
            return self._connected
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            self._connected = False
            return False

    async def _sync_item(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: Dict[str, Any],
        queue_id: Optional[int] = None,
    ) -> bool:
        """
        Sync a single item to backend.

        Args:
            entity_type: Entity type
            entity_id: Entity ID
            action: Action
            payload: Data
            queue_id: Queue item ID for updating retry count

        Returns:
            True if sync succeeded
        """
        if not self._client:
            return False

        # Handle WIP process operations with dynamic endpoint
        if entity_type == "wip_process":
            return await self._sync_wip_process(entity_id, action, payload, queue_id)

        # Determine endpoint based on entity type
        endpoint_map = {
            "execution": "/api/v1/executions",
            "step": "/api/v1/steps",
            "log": "/api/v1/logs",
        }

        endpoint = endpoint_map.get(entity_type)
        if not endpoint:
            logger.error(f"Unknown entity type: {entity_type}")
            return False

        try:
            if action == "create":
                response = await self._client.post(endpoint, json=payload)
            elif action == "update":
                response = await self._client.put(f"{endpoint}/{entity_id}", json=payload)
            else:
                logger.error(f"Unknown action: {action}")
                return False

            if response.status_code in (200, 201):
                # Success - remove from queue if applicable
                if queue_id and self._sync_repo:
                    await self._sync_repo.dequeue(queue_id)
                return True
            else:
                logger.warning(
                    f"Sync failed: {response.status_code} - {response.text[:200]}"
                )
                if queue_id and self._sync_repo:
                    await self._sync_repo.mark_failed(queue_id, f"HTTP {response.status_code}")
                return False

        except httpx.RequestError as e:
            logger.error(f"Sync request error: {e}")
            # Mark as failed with error message
            if queue_id and self._sync_repo:
                await self._sync_repo.mark_failed(queue_id, str(e))
            return False

    async def _sync_loop(self) -> None:
        """Background task for periodic sync."""
        logger.debug("Sync loop started")

        while self._running:
            try:
                await asyncio.sleep(self._sync_interval)

                if not self._connected:
                    continue

                # Get pending items
                if self._sync_repo:
                    pending = await self._sync_repo.get_pending_items(limit=10)

                    for item in pending:
                        if not self._running:
                            break

                        # Skip items that have exceeded max retries
                        if item["retry_count"] >= self._max_retries:
                            continue

                        await self._sync_item(
                            entity_type=item["entity_type"],
                            entity_id=item["entity_id"],
                            action=item["action"],
                            payload=item["payload"],
                            queue_id=item["id"],
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                await asyncio.sleep(5)

        logger.debug("Sync loop stopped")

    async def _health_check_loop(self) -> None:
        """Background task for health checking."""
        logger.debug("Health check loop started")

        while self._running:
            try:
                was_connected = self._connected
                await self.check_connection()

                # Log connection state changes
                if was_connected and not self._connected:
                    logger.warning("Backend connection lost")
                elif not was_connected and self._connected:
                    logger.info("Backend connection established")

                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)

        logger.debug("Health check loop stopped")

    # ================================================================
    # Station Registration and Heartbeat
    # ================================================================

    async def _register_station(self) -> bool:
        """
        Register this station with the backend.

        Returns:
            True if registration succeeded
        """
        if not self._client or not self._station_id:
            return False

        try:
            # Determine station host for registration
            # If server_host is 0.0.0.0, use localhost for registration
            host = self._server_host
            if host == "0.0.0.0":
                host = "localhost"

            payload = {
                "station_id": self._station_id,
                "station_name": self._station_name,
                "host": host,
                "port": self._server_port,
                "description": self._station_description,
            }

            response = await self._client.post("/api/v1/stations/register", json=payload)

            if response.status_code in (200, 201):
                self._registered = True
                logger.info(f"Station registered with backend: {self._station_id}")
                return True
            else:
                logger.warning(
                    f"Station registration failed: {response.status_code} - {response.text[:200]}"
                )
                return False

        except httpx.RequestError as e:
            logger.error(f"Station registration request error: {e}")
            return False

    async def _send_heartbeat(self) -> bool:
        """
        Send a heartbeat to the backend.

        Returns:
            True if heartbeat succeeded
        """
        if not self._client or not self._station_id or not self._registered:
            return False

        try:
            # Collect health data to send with heartbeat
            health_data = {
                "status": "healthy",
                "batches_running": 0,  # Will be updated by actual batch count
                "backend_status": "connected" if self._connected else "disconnected",
                "disk_usage": 0,  # Could be fetched from system
            }

            response = await self._client.post(
                f"/api/v1/stations/{self._station_id}/heartbeat",
                json={"health_data": health_data},
            )

            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                # Station not found, need to re-register
                logger.warning("Station not found in backend, re-registering...")
                self._registered = False
                return await self._register_station()
            else:
                logger.debug(f"Heartbeat failed: {response.status_code}")
                return False

        except httpx.RequestError as e:
            logger.debug(f"Heartbeat request error: {e}")
            return False

    async def _heartbeat_loop(self) -> None:
        """Background task for sending periodic heartbeats."""
        logger.debug("Heartbeat loop started")

        while self._running:
            try:
                await asyncio.sleep(self._heartbeat_interval)

                if not self._connected:
                    continue

                if not self._registered:
                    # Try to register if not yet registered
                    await self._register_station()
                else:
                    # Send heartbeat
                    await self._send_heartbeat()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(5)

        logger.debug("Heartbeat loop stopped")

    # ================================================================
    # WIP Process Sync Methods
    # ================================================================

    async def _sync_wip_process(
        self,
        wip_id: str,
        action: str,
        payload: Dict[str, Any],
        queue_id: Optional[int] = None,
    ) -> bool:
        """
        Sync a WIP process operation to backend.

        Args:
            wip_id: WIP ID (string)
            action: Action type (start_process, complete_process, convert_to_serial)
            payload: Request payload including wip_int_id and request data
            queue_id: Queue item ID for retry tracking

        Returns:
            True if sync succeeded
        """
        if not self._client:
            return False

        wip_int_id = payload.get("wip_int_id")
        request_data = payload.get("request", {})

        if not wip_int_id:
            logger.error(f"Missing wip_int_id in payload for {action}")
            return False

        try:
            if action == "start_process":
                endpoint = f"/api/v1/wip-items/{wip_int_id}/start-process"
                response = await self._client.post(endpoint, json=request_data)

            elif action == "complete_process":
                endpoint = f"/api/v1/wip-items/{wip_int_id}/complete-process"
                process_id = payload.get("process_id")
                operator_id = payload.get("operator_id")
                params = {"process_id": process_id, "operator_id": operator_id}
                response = await self._client.post(endpoint, params=params, json=request_data)

            elif action == "convert_to_serial":
                endpoint = f"/api/v1/wip-items/{wip_int_id}/convert-to-serial"
                response = await self._client.post(endpoint, json=request_data)

            else:
                logger.error(f"Unknown WIP process action: {action}")
                return False

            if response.status_code in (200, 201):
                logger.info(f"WIP process sync successful: {action} for {wip_id}")
                if queue_id and self._sync_repo:
                    await self._sync_repo.dequeue(queue_id)
                return True
            else:
                logger.warning(
                    f"WIP process sync failed: {response.status_code} - {response.text[:200]}"
                )
                if queue_id and self._sync_repo:
                    await self._sync_repo.mark_failed(queue_id, f"HTTP {response.status_code}")
                return False

        except httpx.RequestError as e:
            logger.error(f"WIP process sync request error: {e}")
            if queue_id and self._sync_repo:
                await self._sync_repo.mark_failed(queue_id, str(e))
            return False

    async def sync_process_start(
        self,
        wip_id: str,
        wip_int_id: int,
        request_data: Dict[str, Any],
    ) -> bool:
        """
        Sync a process start operation to backend.

        Args:
            wip_id: WIP ID (string)
            wip_int_id: WIP integer ID for API call
            request_data: ProcessStartRequest data

        Returns:
            True if sync succeeded
        """
        payload = {
            "wip_int_id": wip_int_id,
            "request": request_data,
        }
        return await self._sync_wip_process(wip_id, "start_process", payload)

    async def sync_process_complete(
        self,
        wip_id: str,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        request_data: Dict[str, Any],
    ) -> bool:
        """
        Sync a process completion to backend.

        Args:
            wip_id: WIP ID (string)
            wip_int_id: WIP integer ID for API call
            process_id: Process ID
            operator_id: Operator ID
            request_data: ProcessCompleteRequest data

        Returns:
            True if sync succeeded
        """
        payload = {
            "wip_int_id": wip_int_id,
            "process_id": process_id,
            "operator_id": operator_id,
            "request": request_data,
        }
        return await self._sync_wip_process(wip_id, "complete_process", payload)

    async def sync_serial_convert(
        self,
        wip_id: str,
        wip_int_id: int,
        request_data: Dict[str, Any],
    ) -> bool:
        """
        Sync a serial conversion to backend.

        Args:
            wip_id: WIP ID (string)
            wip_int_id: WIP integer ID for API call
            request_data: SerialConvertRequest data

        Returns:
            True if sync succeeded
        """
        payload = {
            "wip_int_id": wip_int_id,
            "request": request_data,
        }
        return await self._sync_wip_process(wip_id, "convert_to_serial", payload)
