"""
Configuration model definitions.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CORSConfig(BaseModel):
    """CORS configuration for the HTTP server."""

    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class ServerConfig(BaseModel):
    """HTTP server configuration."""

    host: str = "0.0.0.0"
    port: int = 8080
    cors: CORSConfig = CORSConfig()


class BackendConfig(BaseModel):
    """Backend API connection configuration."""

    url: str = ""
    api_key: str = ""
    sync_interval: int = 30  # seconds

    # Station identification for Backend
    station_id: str = ""
    equipment_id: int | None = None

    # Timeout and retry settings
    timeout: float = 30.0  # seconds
    max_retries: int = 5


class StationInfo(BaseModel):
    """Station identification information."""

    id: str
    name: str
    description: str = ""


class SimulationMeasurementConfig(BaseModel):
    """Configuration for a simulated measurement range."""

    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    unit: str = Field("", description="Unit of measurement")
    noise: float = Field(0.02, description="Random noise factor (0-1)")


class SimulationProcessConfig(BaseModel):
    """Simulation configuration for a specific process."""

    measurements: Dict[str, SimulationMeasurementConfig] = Field(
        default_factory=dict,
        description="Measurement ranges for this process",
    )
    failure_rate: Optional[float] = Field(
        None, description="Override failure rate for this process"
    )


class SimulationConfig(BaseModel):
    """Global simulation configuration."""

    enabled: bool = Field(True, description="Enable simulation mode")
    min_delay: float = Field(0.1, description="Minimum operation delay in seconds")
    max_delay: float = Field(0.5, description="Maximum operation delay in seconds")
    failure_rate: float = Field(0.02, description="Default failure rate (0-1)")
    connection_delay: float = Field(0.3, description="Connection delay in seconds")
    processes: Dict[int, SimulationProcessConfig] = Field(
        default_factory=dict,
        description="Process-specific simulation configs (keyed by process_id 1-8)",
    )


class BatchConfig(BaseModel):
    """Batch configuration from station.yaml."""

    id: str
    name: str
    sequence_package: str
    hardware: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    auto_start: bool = False
    process_id: Optional[int] = Field(
        None, description="Associated process ID (1-8) for WIP tracking"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    file: str = "data/logs/station.log"
    max_size: str = "10MB"
    backup_count: int = 5


class StationConfig(BaseModel):
    """Complete station configuration (station.yaml)."""

    station: StationInfo
    server: ServerConfig = ServerConfig()
    backend: BackendConfig = BackendConfig()
    batches: List[BatchConfig] = []
    logging: LoggingConfig = LoggingConfig()
    simulation: SimulationConfig = SimulationConfig()
