"""
Unit tests for the EventEmitter class.

Tests event registration, emission, and handler management.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from station_service.core.events import Event, EventEmitter, EventType


class TestEventEmitter:
    """Test suite for EventEmitter."""

    @pytest.fixture
    def emitter(self) -> EventEmitter:
        """Create a fresh emitter for each test."""
        return EventEmitter()

    @pytest.fixture
    def sample_event(self) -> Event:
        """Create a sample event."""
        return Event(
            type=EventType.BATCH_STARTED,
            batch_id="batch_001",
            data={"pid": 12345},
        )

    # ============================================================
    # Handler Registration Tests
    # ============================================================

    def test_on_registers_handler(self, emitter: EventEmitter):
        """Test that on() registers a handler for an event type."""
        handler = AsyncMock()
        emitter.on(EventType.BATCH_STARTED, handler)

        assert EventType.BATCH_STARTED in emitter._handlers
        assert handler in emitter._handlers[EventType.BATCH_STARTED]

    def test_on_any_registers_wildcard_handler(self, emitter: EventEmitter):
        """Test that on_any() registers a wildcard handler."""
        handler = AsyncMock()
        emitter.on_any(handler)

        assert handler in emitter._wildcard_handlers

    def test_off_removes_handler(self, emitter: EventEmitter):
        """Test that off() removes a registered handler."""
        handler = AsyncMock()
        emitter.on(EventType.BATCH_STARTED, handler)

        result = emitter.off(EventType.BATCH_STARTED, handler)

        assert result is True
        assert handler not in emitter._handlers.get(EventType.BATCH_STARTED, [])

    def test_off_returns_false_for_unregistered_handler(self, emitter: EventEmitter):
        """Test that off() returns False for unregistered handler."""
        handler = AsyncMock()

        result = emitter.off(EventType.BATCH_STARTED, handler)

        assert result is False

    def test_off_any_removes_wildcard_handler(self, emitter: EventEmitter):
        """Test that off_any() removes a wildcard handler."""
        handler = AsyncMock()
        emitter.on_any(handler)

        result = emitter.off_any(handler)

        assert result is True
        assert handler not in emitter._wildcard_handlers

    def test_clear_removes_all_handlers(self, emitter: EventEmitter):
        """Test that clear() removes all handlers."""
        emitter.on(EventType.BATCH_STARTED, AsyncMock())
        emitter.on(EventType.BATCH_STOPPED, AsyncMock())
        emitter.on_any(AsyncMock())

        emitter.clear()

        assert len(emitter._handlers) == 0
        assert len(emitter._wildcard_handlers) == 0

    # ============================================================
    # Event Emission Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_emit_calls_registered_handler(
        self, emitter: EventEmitter, sample_event: Event
    ):
        """Test that emit() calls registered handlers."""
        handler = AsyncMock()
        emitter.on(EventType.BATCH_STARTED, handler)

        await emitter.emit(sample_event)

        handler.assert_called_once_with(sample_event)

    @pytest.mark.asyncio
    async def test_emit_calls_wildcard_handler(
        self, emitter: EventEmitter, sample_event: Event
    ):
        """Test that emit() calls wildcard handlers."""
        handler = AsyncMock()
        emitter.on_any(handler)

        await emitter.emit(sample_event)

        handler.assert_called_once_with(sample_event)

    @pytest.mark.asyncio
    async def test_emit_calls_multiple_handlers(
        self, emitter: EventEmitter, sample_event: Event
    ):
        """Test that emit() calls all registered handlers."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        wildcard_handler = AsyncMock()

        emitter.on(EventType.BATCH_STARTED, handler1)
        emitter.on(EventType.BATCH_STARTED, handler2)
        emitter.on_any(wildcard_handler)

        await emitter.emit(sample_event)

        handler1.assert_called_once_with(sample_event)
        handler2.assert_called_once_with(sample_event)
        wildcard_handler.assert_called_once_with(sample_event)

    @pytest.mark.asyncio
    async def test_emit_does_not_call_unrelated_handlers(
        self, emitter: EventEmitter, sample_event: Event
    ):
        """Test that emit() only calls handlers for the emitted event type."""
        started_handler = AsyncMock()
        stopped_handler = AsyncMock()

        emitter.on(EventType.BATCH_STARTED, started_handler)
        emitter.on(EventType.BATCH_STOPPED, stopped_handler)

        await emitter.emit(sample_event)  # BATCH_STARTED event

        started_handler.assert_called_once()
        stopped_handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_emit_with_no_handlers(self, emitter: EventEmitter, sample_event: Event):
        """Test that emit() does not raise when no handlers are registered."""
        # Should not raise
        await emitter.emit(sample_event)

    @pytest.mark.asyncio
    async def test_emit_handles_sync_handlers(self, emitter: EventEmitter, sample_event: Event):
        """Test that emit() can handle synchronous handlers."""
        sync_handler = MagicMock()
        emitter.on(EventType.BATCH_STARTED, sync_handler)

        await emitter.emit(sample_event)

        sync_handler.assert_called_once_with(sample_event)

    @pytest.mark.asyncio
    async def test_emit_continues_on_handler_error(
        self, emitter: EventEmitter, sample_event: Event
    ):
        """Test that emit() continues calling handlers even if one fails."""
        failing_handler = AsyncMock(side_effect=Exception("Handler error"))
        success_handler = AsyncMock()

        emitter.on(EventType.BATCH_STARTED, failing_handler)
        emitter.on(EventType.BATCH_STARTED, success_handler)

        # Should not raise
        await emitter.emit(sample_event)

        # Both handlers should be called
        failing_handler.assert_called_once()
        success_handler.assert_called_once()

    # ============================================================
    # Event Data Tests
    # ============================================================

    def test_event_to_dict(self, sample_event: Event):
        """Test that Event.to_dict() returns correct dictionary."""
        result = sample_event.to_dict()

        assert result["type"] == "batch_started"
        assert result["batch_id"] == "batch_001"
        assert result["data"] == {"pid": 12345}
        assert "timestamp" in result

    def test_event_with_default_values(self):
        """Test Event creation with default values."""
        event = Event(type=EventType.LOG)

        assert event.batch_id is None
        assert event.data == {}
        assert event.timestamp is not None


class TestEventType:
    """Test suite for EventType enum."""

    def test_batch_event_types(self):
        """Test that batch event types are defined."""
        assert EventType.BATCH_STARTED.value == "batch_started"
        assert EventType.BATCH_STOPPED.value == "batch_stopped"
        assert EventType.BATCH_CRASHED.value == "batch_crashed"
        assert EventType.BATCH_STATUS_CHANGED.value == "batch_status_changed"

    def test_sequence_event_types(self):
        """Test that sequence event types are defined."""
        assert EventType.SEQUENCE_STARTED.value == "sequence_started"
        assert EventType.SEQUENCE_COMPLETED.value == "sequence_completed"
        assert EventType.SEQUENCE_STOPPED.value == "sequence_stopped"

    def test_step_event_types(self):
        """Test that step event types are defined."""
        assert EventType.STEP_STARTED.value == "step_started"
        assert EventType.STEP_COMPLETED.value == "step_completed"
        assert EventType.STEP_SKIPPED.value == "step_skipped"
        assert EventType.STEP_FAILED.value == "step_failed"

    def test_sync_event_types(self):
        """Test that sync event types are defined."""
        assert EventType.SYNC_STARTED.value == "sync_started"
        assert EventType.SYNC_COMPLETED.value == "sync_completed"
        assert EventType.SYNC_FAILED.value == "sync_failed"
