"""
Event system for Station Service.

Provides a simple event emitter pattern for inter-component communication.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for Station Service."""

    # Batch events
    BATCH_STARTED = "batch_started"
    BATCH_STOPPED = "batch_stopped"
    BATCH_CRASHED = "batch_crashed"
    BATCH_STATUS_CHANGED = "batch_status_changed"

    # Sequence events
    SEQUENCE_STARTED = "sequence_started"
    SEQUENCE_COMPLETED = "sequence_completed"
    SEQUENCE_STOPPED = "sequence_stopped"
    SEQUENCE_ERROR = "sequence_error"

    # Step events
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_SKIPPED = "step_skipped"
    STEP_FAILED = "step_failed"

    # Hardware events
    HARDWARE_CONNECTED = "hardware_connected"
    HARDWARE_DISCONNECTED = "hardware_disconnected"
    HARDWARE_ERROR = "hardware_error"

    # Sync events
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"

    # Log events
    LOG = "log"
    ERROR = "error"


@dataclass
class Event:
    """Event data container."""

    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    batch_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "type": self.type.value,
            "batch_id": self.batch_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


# Type alias for event handlers
EventHandler = Callable[[Event], Union[None, Coroutine[Any, Any, None]]]


class EventEmitter:
    """
    Async event emitter for Station Service.

    Supports both sync and async event handlers. Handlers are called
    concurrently for each event.

    Usage:
        emitter = EventEmitter()

        async def on_batch_started(event: Event):
            print(f"Batch {event.batch_id} started")

        emitter.on(EventType.BATCH_STARTED, on_batch_started)
        await emitter.emit(Event(type=EventType.BATCH_STARTED, batch_id="batch_1"))
    """

    def __init__(self) -> None:
        """Initialize the event emitter."""
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._wildcard_handlers: List[EventHandler] = []

    def on(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Register an event handler.

        Args:
            event_type: The event type to listen for
            handler: The handler function (sync or async)
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def on_any(self, handler: EventHandler) -> None:
        """
        Register a wildcard handler that receives all events.

        Args:
            handler: The handler function (sync or async)
        """
        self._wildcard_handlers.append(handler)

    def off(self, event_type: EventType, handler: EventHandler) -> bool:
        """
        Unregister an event handler.

        Args:
            event_type: The event type
            handler: The handler to remove

        Returns:
            True if handler was found and removed, False otherwise
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False

    def off_any(self, handler: EventHandler) -> bool:
        """
        Unregister a wildcard handler.

        Args:
            handler: The handler to remove

        Returns:
            True if handler was found and removed, False otherwise
        """
        try:
            self._wildcard_handlers.remove(handler)
            return True
        except ValueError:
            return False

    async def emit(self, event: Event) -> None:
        """
        Emit an event to all registered handlers.

        Args:
            event: The event to emit
        """
        handlers: List[EventHandler] = []

        # Get type-specific handlers
        if event.type in self._handlers:
            handlers.extend(self._handlers[event.type])

        # Add wildcard handlers
        handlers.extend(self._wildcard_handlers)

        if not handlers:
            return

        # Create tasks for all handlers
        tasks: List[asyncio.Task] = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    task = asyncio.create_task(handler(event))
                else:
                    # Wrap sync handler in async
                    task = asyncio.create_task(self._run_sync_handler(handler, event))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error creating handler task: {e}")

        # Wait for all handlers to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Handler error: {result}")

    async def _run_sync_handler(self, handler: EventHandler, event: Event) -> None:
        """Run a synchronous handler in the executor."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, handler, event)

    def clear(self) -> None:
        """Remove all event handlers."""
        self._handlers.clear()
        self._wildcard_handlers.clear()


# Global event emitter singleton
_event_emitter: Optional[EventEmitter] = None


def get_event_emitter() -> EventEmitter:
    """
    Get the global event emitter singleton.

    Returns:
        EventEmitter instance
    """
    global _event_emitter
    if _event_emitter is None:
        _event_emitter = EventEmitter()
    return _event_emitter
