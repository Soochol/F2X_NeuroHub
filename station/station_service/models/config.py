"""
Configuration model definitions.
"""

from typing import Any, Dict, List, Literal, Optional

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


class WorkflowConfig(BaseModel):
    """Station-level workflow configuration for 착공/완공."""

    enabled: bool = Field(True, description="Enable WIP process start/complete workflow")
    input_mode: Literal["popup", "barcode"] = Field(
        "popup", description="WIP ID input mode: popup for manual entry, barcode for scanner"
    )
    auto_sequence_start: bool = Field(
        True, description="Automatically start sequence after barcode scan"
    )
    require_operator_login: bool = Field(
        True, description="Require backend login before workflow operations"
    )
    default_operator_id: Optional[int] = Field(
        None, description="Default operator ID for 착공/완공 when no operator logged in"
    )


class BatchWorkflowConfig(BaseModel):
    """Batch-level workflow configuration (overrides station-level)."""

    enabled: Optional[bool] = Field(
        None, description="Override station workflow.enabled (null = inherit)"
    )
    input_mode: Optional[Literal["popup", "barcode"]] = Field(
        None, description="Override station workflow.input_mode (null = inherit)"
    )


class BarcodeScannerConfig(BaseModel):
    """Barcode scanner configuration for a batch."""

    type: Literal["serial", "usb_hid", "keyboard_wedge"] = Field(
        "serial", description="Scanner connection type"
    )
    driver: str = Field(
        "SerialBarcodeScanner", description="Driver class name"
    )
    config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "port": "COM3",
            "baudrate": 9600,
            "terminator": "\r\n",
        },
        description="Driver-specific configuration",
    )


class BatchConfig(BaseModel):
    """Batch configuration from station.yaml."""

    id: str
    name: str
    sequence_package: str
    hardware: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    auto_start: bool = False
    # Dynamic config object (replaces hardcoded process_id, header_id)
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic batch configuration (processId, headerId, etc.)"
    )
    # Legacy fields - deprecated, use config instead
    process_id: Optional[int] = Field(
        None, description="[Deprecated] Use config.processId instead"
    )
    header_id: Optional[int] = Field(
        None, description="[Deprecated] Use config.headerId instead"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Batch parameters for sequence execution"
    )
    workflow: BatchWorkflowConfig = Field(
        default_factory=BatchWorkflowConfig,
        description="Batch-level workflow overrides",
    )
    barcode_scanner: Optional[BarcodeScannerConfig] = Field(
        None, description="Batch-specific barcode scanner configuration"
    )

    def get_process_id(self) -> Optional[int]:
        """Get process_id from config or legacy field."""
        return self.config.get("processId") or self.process_id

    def get_header_id(self) -> Optional[int]:
        """Get header_id from config or legacy field."""
        return self.config.get("headerId") or self.header_id


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    file: str = "data/logs/station.log"
    max_size: str = "10MB"
    backup_count: int = 5


class GitSyncConfig(BaseModel):
    """Git repository sync configuration for sequences."""

    enabled: bool = Field(False, description="Enable git-based sequence auto-sync")
    repository_url: str = Field("", description="Git repository URL for sequences")
    branch: str = Field("main", description="Git branch to track")
    poll_interval: int = Field(60, description="Polling interval in seconds")
    auto_pull: bool = Field(True, description="Automatically pull when new commits detected")
    ssh_key_path: Optional[str] = Field(None, description="Path to SSH private key for authentication")
    username: Optional[str] = Field(None, description="Git username for HTTPS auth")
    password: Optional[str] = Field(None, description="Git password/token for HTTPS auth")


class IPCConfig(BaseModel):
    """IPC (Inter-Process Communication) configuration."""

    router_port: int = Field(5555, description="ZMQ router port for IPC")
    sub_port: int = Field(5557, description="ZMQ subscriber port for IPC")


class PathsConfig(BaseModel):
    """Path configuration for Station Service."""

    sequences_dir: str = Field(
        "sequences",
        description="Directory for sequence packages (relative to project root or absolute)",
    )
    data_dir: str = Field(
        "data",
        description="Directory for data files (database, logs)",
    )


class StationConfig(BaseModel):
    """Complete station configuration (station.yaml)."""

    station: StationInfo
    workflow: WorkflowConfig = Field(
        default_factory=WorkflowConfig,
        description="Station-level workflow configuration",
    )
    server: ServerConfig = ServerConfig()
    ipc: IPCConfig = Field(
        default_factory=IPCConfig,
        description="IPC (Inter-Process Communication) configuration",
    )
    backend: BackendConfig = BackendConfig()
    paths: PathsConfig = Field(
        default_factory=PathsConfig,
        description="Path configuration",
    )
    git_sync: GitSyncConfig = Field(
        default_factory=GitSyncConfig,
        description="Git repository sync configuration for sequences",
    )
    batches: List[BatchConfig] = []
    logging: LoggingConfig = LoggingConfig()
    simulation: SimulationConfig = SimulationConfig()
