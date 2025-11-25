"""
History Manager - Tracks work start/complete/error events with file persistence.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pathlib import Path
import json
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event type enumeration."""
    START = "START"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


class EventResult(str, Enum):
    """Event result enumeration."""
    SUCCESS = "SUCCESS"
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


@dataclass
class WorkEvent:
    """Represents a single work event."""
    timestamp: datetime
    event_type: EventType
    wip_id: str
    lot_number: str
    result: EventResult
    message: str
    process_name: str = ""
    duration_seconds: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "wip_id": self.wip_id,
            "lot_number": self.lot_number,
            "result": self.result.value,
            "message": self.message,
            "process_name": self.process_name,
            "duration_seconds": self.duration_seconds,
        }


class HistoryManager(QObject):
    """
    Manages work history events with file persistence.

    Stores events in JSON files organized by date, maintains in-memory cache,
    and persists to disk automatically.
    """

    # Signals
    event_added = Signal(object)  # WorkEvent
    history_cleared = Signal()

    def __init__(self, max_events: int = 100, history_dir: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._events: List[WorkEvent] = []
        self._max_events = max_events

        # Setup history directory
        if history_dir is None:
            # Default: data/history/ relative to app directory
            history_dir = Path(__file__).parent.parent / "data" / "history"
        else:
            history_dir = Path(history_dir)

        self._history_dir = Path(history_dir)
        self._history_dir.mkdir(parents=True, exist_ok=True)

        # Load today's events from file
        self._load_today_events()

    def add_start_event(self, wip_id: str, lot_number: str, process_name: str = "",
                        success: bool = True, message: str = ""):
        """
        Add a work start event.

        Args:
            wip_id: WIP identifier
            lot_number: LOT number
            process_name: Process name
            success: Whether start was successful
            message: Additional message
        """
        event = WorkEvent(
            timestamp=datetime.now(),
            event_type=EventType.START,
            wip_id=wip_id,
            lot_number=lot_number,
            result=EventResult.SUCCESS if success else EventResult.ERROR,
            message=message or ("Work started" if success else "Start failed"),
            process_name=process_name,
        )
        self._add_event(event)

    def add_complete_event(self, wip_id: str, lot_number: str, result: str,
                           process_name: str = "", duration_seconds: int = None,
                           message: str = ""):
        """
        Add a work complete event.

        Args:
            wip_id: WIP identifier
            lot_number: LOT number
            result: Result string (PASS, FAIL, etc.)
            process_name: Process name
            duration_seconds: Work duration in seconds
            message: Additional message
        """
        if result.upper() == "PASS":
            event_result = EventResult.PASS
        elif result.upper() == "FAIL":
            event_result = EventResult.FAIL
        else:
            event_result = EventResult.SUCCESS

        event = WorkEvent(
            timestamp=datetime.now(),
            event_type=EventType.COMPLETE,
            wip_id=wip_id,
            lot_number=lot_number,
            result=event_result,
            message=message or f"Completed with {result}",
            process_name=process_name,
            duration_seconds=duration_seconds,
        )
        self._add_event(event)

    def add_error_event(self, wip_id: str, lot_number: str, error_message: str,
                        process_name: str = "", event_type: EventType = EventType.ERROR):
        """
        Add an error event.

        Args:
            wip_id: WIP identifier
            lot_number: LOT number
            error_message: Error message
            process_name: Process name
            event_type: Original event type (START or COMPLETE that failed)
        """
        event = WorkEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            wip_id=wip_id,
            lot_number=lot_number,
            result=EventResult.ERROR,
            message=error_message,
            process_name=process_name,
        )
        self._add_event(event)

    def _add_event(self, event: WorkEvent):
        """Add event to history, maintain max size, and save to file."""
        self._events.insert(0, event)  # Most recent first

        # Trim to max size
        if len(self._events) > self._max_events:
            self._events = self._events[:self._max_events]

        # Save to file
        self._save_today_events()

        self.event_added.emit(event)

    def _get_today_filename(self) -> Path:
        """Get today's history file path."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self._history_dir / f"{today}_events.json"

    def _load_today_events(self):
        """Load today's events from file."""
        file_path = self._get_today_filename()

        if not file_path.exists():
            logger.info(f"No history file found for today: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._events = []
            for event_dict in data.get('events', []):
                try:
                    timestamp = datetime.fromisoformat(event_dict['timestamp'])
                    event = WorkEvent(
                        timestamp=timestamp,
                        event_type=EventType(event_dict['event_type']),
                        wip_id=event_dict['wip_id'],
                        lot_number=event_dict['lot_number'],
                        result=EventResult(event_dict['result']),
                        message=event_dict['message'],
                        process_name=event_dict.get('process_name', ''),
                        duration_seconds=event_dict.get('duration_seconds'),
                    )
                    self._events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse event: {e}")
                    continue

            # Ensure most recent first
            self._events.sort(key=lambda e: e.timestamp, reverse=True)
            logger.info(f"Loaded {len(self._events)} events from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load history from {file_path}: {e}")

    def _save_today_events(self):
        """Save today's events to file."""
        file_path = self._get_today_filename()

        try:
            data = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'count': len(self._events),
                'events': [e.to_dict() for e in self._events]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(self._events)} events to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save history to {file_path}: {e}")

    def get_all_events(self) -> List[WorkEvent]:
        """Get all events (most recent first)."""
        return self._events.copy()

    def get_events_by_type(self, event_type: EventType) -> List[WorkEvent]:
        """Get events filtered by type."""
        return [e for e in self._events if e.event_type == event_type]

    def get_events_by_result(self, result: EventResult) -> List[WorkEvent]:
        """Get events filtered by result."""
        return [e for e in self._events if e.result == result]

    def get_error_events(self) -> List[WorkEvent]:
        """Get all error events."""
        return [e for e in self._events if e.result == EventResult.ERROR]

    def get_success_events(self) -> List[WorkEvent]:
        """Get all successful events (non-error)."""
        return [e for e in self._events if e.result != EventResult.ERROR]

    def get_event_count(self) -> int:
        """Get total event count."""
        return len(self._events)

    def get_error_count(self) -> int:
        """Get error event count."""
        return len(self.get_error_events())

    def clear(self):
        """Clear all events from memory and file."""
        self._events.clear()

        # Also delete the file
        file_path = self._get_today_filename()
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Cleared history file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete history file: {e}")

        self.history_cleared.emit()

    def get_history_dir(self) -> Path:
        """Get the history directory path."""
        return self._history_dir

    def load_events_by_date(self, date_str: str) -> List[WorkEvent]:
        """
        Load events from a specific date (YYYY-MM-DD format).

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            List of WorkEvent objects for that date
        """
        file_path = self._history_dir / f"{date_str}_events.json"

        if not file_path.exists():
            logger.warning(f"History file not found: {file_path}")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            events = []
            for event_dict in data.get('events', []):
                try:
                    timestamp = datetime.fromisoformat(event_dict['timestamp'])
                    event = WorkEvent(
                        timestamp=timestamp,
                        event_type=EventType(event_dict['event_type']),
                        wip_id=event_dict['wip_id'],
                        lot_number=event_dict['lot_number'],
                        result=EventResult(event_dict['result']),
                        message=event_dict['message'],
                        process_name=event_dict.get('process_name', ''),
                        duration_seconds=event_dict.get('duration_seconds'),
                    )
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse event: {e}")
                    continue

            logger.info(f"Loaded {len(events)} events from {date_str}")
            return events

        except Exception as e:
            logger.error(f"Failed to load history from {file_path}: {e}")
            return []

    def get_available_dates(self) -> List[str]:
        """
        Get list of all available history dates.

        Returns:
            List of date strings in YYYY-MM-DD format, sorted newest first
        """
        dates = []
        try:
            for file_path in sorted(self._history_dir.glob("*_events.json"), reverse=True):
                # Extract date from filename (YYYY-MM-DD_events.json)
                date_str = file_path.stem.replace("_events", "")
                dates.append(date_str)
        except Exception as e:
            logger.error(f"Failed to get available dates: {e}")

        return dates


# Singleton instance
_history_manager: Optional[HistoryManager] = None


def get_history_manager() -> HistoryManager:
    """Get the singleton HistoryManager instance."""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager
