"""
Station model definition.
"""

from typing import Optional

from pydantic import BaseModel


class Station(BaseModel):
    """Represents a test station."""

    id: str  # "ST-001"
    name: str  # "Station 1"
    description: Optional[str] = None  # "PCB 테스트 스테이션"
    version: str  # "1.0.0"
    status: str  # "online", "offline"
    backend_connected: bool
    uptime: int  # seconds
