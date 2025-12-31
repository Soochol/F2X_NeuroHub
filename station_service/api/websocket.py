"""
WebSocket handler for real-time updates.

Provides WebSocket endpoint for batch status updates and event streaming.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Set

from fastapi import WebSocket, WebSocketDisconnect

from station_service.models import (
    BatchStatusMessage,
    ErrorMessage,
    LogMessage,
    SequenceCompleteMessage,
    StepCompleteMessage,
    StepStartMessage,
    SubscribeMessage,
    UnsubscribeMessage,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""

    def __init__(self):
        """Initialize connection manager."""
        self._connections: Dict[WebSocket, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to accept.
        """
        await websocket.accept()
        async with self._lock:
            self._connections[websocket] = set()
        logger.info(f"WebSocket connected: {websocket.client}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove.
        """
        async with self._lock:
            if websocket in self._connections:
                del self._connections[websocket]
        logger.info(f"WebSocket disconnected: {websocket.client}")

    async def subscribe(self, websocket: WebSocket, batch_ids: List[str]) -> None:
        """
        Subscribe a connection to batch updates.

        Args:
            websocket: The WebSocket connection.
            batch_ids: List of batch IDs to subscribe to.
        """
        async with self._lock:
            if websocket in self._connections:
                self._connections[websocket].update(batch_ids)
        logger.debug(f"Subscribed to batches: {batch_ids}")

    async def unsubscribe(self, websocket: WebSocket, batch_ids: List[str]) -> None:
        """
        Unsubscribe a connection from batch updates.

        Args:
            websocket: The WebSocket connection.
            batch_ids: List of batch IDs to unsubscribe from.
        """
        async with self._lock:
            if websocket in self._connections:
                self._connections[websocket].difference_update(batch_ids)
        logger.debug(f"Unsubscribed from batches: {batch_ids}")

    async def broadcast(self, batch_id: str, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all subscribers of a batch.

        Args:
            batch_id: The batch ID.
            message: The message to broadcast.
        """
        async with self._lock:
            connections = list(self._connections.items())

        # Log how many connections are subscribed to this batch
        subscribers = sum(1 for _, subs in connections if batch_id in subs)
        logger.info(f"[WS Manager] Broadcasting to batch {batch_id[:8]}...: {subscribers} subscribers out of {len(connections)} connections")

        for websocket, subscribed_batches in connections:
            if batch_id in subscribed_batches:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")

    async def broadcast_all(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message: The message to broadcast.
        """
        async with self._lock:
            connections = list(self._connections.keys())

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint handler.

    Handles WebSocket connections and message processing for real-time updates.

    Args:
        websocket: The WebSocket connection.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_client_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "data": {"code": "INVALID_JSON", "message": "Invalid JSON"},
                    }
                )
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)


async def handle_client_message(
    websocket: WebSocket, message: Dict[str, Any]
) -> None:
    """
    Handle incoming client messages.

    Args:
        websocket: The WebSocket connection.
        message: The parsed message.
    """
    msg_type = message.get("type")

    if msg_type == "subscribe":
        batch_ids = message.get("batch_ids", [])
        if isinstance(batch_ids, list):
            await manager.subscribe(websocket, batch_ids)
            await websocket.send_json(
                {
                    "type": "subscribed",
                    "data": {"batch_ids": batch_ids},
                }
            )

    elif msg_type == "unsubscribe":
        batch_ids = message.get("batch_ids", [])
        if isinstance(batch_ids, list):
            await manager.unsubscribe(websocket, batch_ids)
            await websocket.send_json(
                {
                    "type": "unsubscribed",
                    "data": {"batch_ids": batch_ids},
                }
            )

    else:
        await websocket.send_json(
            {
                "type": "error",
                "data": {
                    "code": "UNKNOWN_MESSAGE_TYPE",
                    "message": f"Unknown message type: {msg_type}",
                },
            }
        )


# Helper functions for broadcasting events


async def broadcast_batch_status(
    batch_id: str,
    status: str,
    current_step: str = None,
    step_index: int = 0,
    progress: float = 0.0,
    execution_id: str = "",
) -> None:
    """Broadcast batch status update to ALL connected clients."""
    logger.info(f"[WS Broadcast] batch_status: batch={batch_id[:8]}..., status={status}, step={current_step}, exec={execution_id}")
    # Broadcast to ALL connections - clients filter by batch_id
    await manager.broadcast_all(
        {
            "type": "batch_status",
            "batch_id": batch_id,
            "data": {
                "status": status,
                "current_step": current_step,
                "step_index": step_index,
                "progress": progress,
                "execution_id": execution_id,
            },
        },
    )


async def broadcast_step_start(
    batch_id: str, step: str, index: int, total: int, execution_id: str = ""
) -> None:
    """Broadcast step start event to ALL connected clients."""
    logger.info(f"[WS Broadcast] step_start: batch={batch_id[:8]}..., step={step}, index={index}/{total}, exec={execution_id}")
    # Broadcast to ALL connections - clients filter by batch_id
    await manager.broadcast_all(
        {
            "type": "step_start",
            "batch_id": batch_id,
            "data": {
                "step": step,
                "index": index,
                "total": total,
                "execution_id": execution_id,
            },
        },
    )


async def broadcast_step_complete(
    batch_id: str,
    step: str,
    index: int,
    duration: float,
    pass_: bool,
    result: Dict[str, Any] = None,
    execution_id: str = "",
) -> None:
    """Broadcast step complete event to ALL connected clients."""
    logger.info(f"[WS Broadcast] step_complete: batch={batch_id[:8]}..., step={step}, pass={pass_}, exec={execution_id}")
    # Broadcast to ALL connections - clients filter by batch_id
    await manager.broadcast_all(
        {
            "type": "step_complete",
            "batch_id": batch_id,
            "data": {
                "step": step,
                "index": index,
                "duration": duration,
                "pass": pass_,
                "result": result or {},
                "execution_id": execution_id,
            },
        },
    )


async def broadcast_sequence_complete(
    batch_id: str,
    execution_id: str,
    overall_pass: bool,
    duration: int,
    steps: List[Dict[str, Any]] = None,
) -> None:
    """Broadcast sequence complete event to ALL connected clients."""
    logger.info(f"[WS Broadcast] sequence_complete: batch={batch_id[:8]}..., pass={overall_pass}")
    # Broadcast to ALL connections - clients filter by batch_id
    await manager.broadcast_all(
        {
            "type": "sequence_complete",
            "batch_id": batch_id,
            "data": {
                "execution_id": execution_id,
                "overall_pass": overall_pass,
                "duration": duration,
                "steps": steps or [],
            },
        },
    )


async def broadcast_log(
    batch_id: str, level: str, message: str, timestamp: str
) -> None:
    """Broadcast log event to ALL connected clients."""
    # Broadcast to ALL connections - clients filter by batch_id
    await manager.broadcast_all(
        {
            "type": "log",
            "batch_id": batch_id,
            "data": {
                "level": level,
                "message": message,
                "timestamp": timestamp,
            },
        },
    )


async def broadcast_error(
    batch_id: str, code: str, message: str, step: str = None, timestamp: str = None
) -> None:
    """Broadcast error event to ALL connected clients."""
    # Broadcast to ALL connections - clients filter by batch_id
    await manager.broadcast_all(
        {
            "type": "error",
            "batch_id": batch_id,
            "data": {
                "code": code,
                "message": message,
                "step": step,
                "timestamp": timestamp,
            },
        },
    )


async def broadcast_batch_created(
    batch_id: str, name: str, sequence_package: str = None
) -> None:
    """Broadcast batch created event to all connected clients."""
    await manager.broadcast_all(
        {
            "type": "batch_created",
            "batch_id": batch_id,
            "data": {
                "id": batch_id,
                "name": name,
                "sequence_package": sequence_package,
            },
        },
    )


async def broadcast_batch_deleted(batch_id: str) -> None:
    """Broadcast batch deleted event to all connected clients."""
    await manager.broadcast_all(
        {
            "type": "batch_deleted",
            "batch_id": batch_id,
            "data": {
                "id": batch_id,
            },
        },
    )
