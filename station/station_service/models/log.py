"""
Log model definitions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class LogLevel(str, Enum):
    """Log severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class LogEntry(BaseModel):
    """Log entry record."""

    id: int
    batch_id: str
    execution_id: Optional[str] = None
    level: LogLevel
    message: str
    timestamp: datetime
