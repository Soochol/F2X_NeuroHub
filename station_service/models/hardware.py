"""
Hardware status model definitions.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class HardwareStatus(BaseModel):
    """Hardware device status."""

    id: str  # "dmm"
    driver: str  # "KeysightDMM"
    status: str  # "connected", "disconnected", "error"
    connected: bool
    last_error: Optional[str] = None
    config: Dict[str, Any]  # Applied configuration
    info: Optional[Dict[str, Any]] = None  # Device info (IDN, etc.)
