"""
Station Service - Main Entry Point.

This is the main entry point for the Station Service FastAPI application.
It handles startup/shutdown lifecycle, initializes all components, and
serves the REST API along with WebSocket connections.

Usage:
    # Run directly
    python -m station_service.main

    # Run with uvicorn
    uvicorn station_service.main:app --host 0.0.0.0 --port 8080

    # Run with custom config
    STATION_CONFIG=/path/to/station.yaml python -m station_service.main
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from station_service.api import create_app
from station_service.api.websocket import websocket_endpoint
from station_service.core.container import ServiceContainer, set_container
from station_service.core.events import Event, EventEmitter, EventType
from station_service.models.config import StationConfig
from station_service.sync.backend_client import BackendClient
from station_service.services.auto_sync import (
    AutoSyncService,
    AutoSyncConfig,
    set_auto_sync_service,
)
from station_service.services.sequence_sync import SequenceSyncService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Global container instance (replaces individual globals)
_container: Optional[ServiceContainer] = None
_backend_client: Optional[BackendClient] = None


def load_config(config_path: Optional[str] = None) -> StationConfig:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file (uses STATION_CONFIG env var if not provided)

    Returns:
        StationConfig instance

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config is invalid
    """
    if config_path is None:
        config_path = os.environ.get("STATION_CONFIG", "config/station.yaml")

    path = Path(config_path)

    if not path.exists():
        # Try relative to module
        module_path = Path(__file__).parent / config_path
        if module_path.exists():
            path = module_path
        else:
            raise FileNotFoundError(f"Config file not found: {config_path}")

    logger.info(f"Loading configuration from: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return StationConfig(**data)


async def setup_event_forwarding(emitter: EventEmitter) -> None:
    """
    Setup event forwarding from EventEmitter to WebSocket.

    Args:
        emitter: The event emitter to listen to
    """
    from station_service.api.websocket import (
        broadcast_batch_status,
        broadcast_step_start,
        broadcast_step_complete,
        broadcast_sequence_complete,
        broadcast_log,
        broadcast_error,
    )

    async def forward_event(event: Event) -> None:
        """Forward events to WebSocket clients."""
        logger.info(f"[EventForwarder] Received event: {event.type.value} for batch {event.batch_id}")
        if event.type == EventType.BATCH_STATUS_CHANGED:
            await broadcast_batch_status(
                batch_id=event.batch_id,
                status=event.data.get("status", ""),
                current_step=event.data.get("current_step"),
                step_index=event.data.get("step_index", 0),
                progress=event.data.get("progress", 0.0),
                execution_id=event.data.get("execution_id", ""),
            )
        elif event.type == EventType.STEP_STARTED:
            await broadcast_step_start(
                batch_id=event.batch_id,
                step=event.data.get("step", ""),
                index=event.data.get("index", 0),
                total=event.data.get("total", 0),
                execution_id=event.data.get("execution_id", ""),
            )
        elif event.type == EventType.STEP_COMPLETED:
            await broadcast_step_complete(
                batch_id=event.batch_id,
                step=event.data.get("step", ""),
                index=event.data.get("index", 0),
                duration=event.data.get("duration", 0.0),
                pass_=event.data.get("pass", False),
                result=event.data.get("result"),
                execution_id=event.data.get("execution_id", ""),
            )
        elif event.type == EventType.SEQUENCE_COMPLETED:
            await broadcast_sequence_complete(
                batch_id=event.batch_id,
                execution_id=event.data.get("execution_id", ""),
                overall_pass=event.data.get("overall_pass", False),
                duration=float(event.data.get("duration", 0.0)),
                steps=event.data.get("steps"),
            )
        elif event.type == EventType.LOG:
            await broadcast_log(
                batch_id=event.batch_id,
                level=event.data.get("level", "info"),
                message=event.data.get("message", ""),
                timestamp=event.timestamp.isoformat(),
            )
        elif event.type == EventType.ERROR:
            await broadcast_error(
                batch_id=event.batch_id,
                code=event.data.get("code", "ERROR"),
                message=event.data.get("message", ""),
                step=event.data.get("step"),
                timestamp=event.timestamp.isoformat(),
            )

    emitter.on_any(forward_event)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown of all components using ServiceContainer.
    """
    global _container, _backend_client

    logger.info("Station Service starting...")

    try:
        # Load configuration
        config = load_config()
        logger.info(f"Loaded config for station: {config.station.name}")

        # Compute paths from config
        # __file__ = station/station_service/main.py
        # project_root = station/ (where pyproject.toml is)
        project_root = Path(__file__).parent.parent

        # Resolve sequences_dir (can be relative or absolute)
        sequences_dir_config = config.paths.sequences_dir
        if Path(sequences_dir_config).is_absolute():
            sequences_dir = Path(sequences_dir_config)
        else:
            sequences_dir = project_root / sequences_dir_config

        # Resolve data_dir
        data_dir_config = config.paths.data_dir
        if Path(data_dir_config).is_absolute():
            data_dir = Path(data_dir_config)
        else:
            data_dir = project_root / data_dir_config

        db_path = data_dir / "station.db"

        # Ensure directories exist
        sequences_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize container with all services
        _container = ServiceContainer()
        await _container.initialize(
            config=config,
            db_path=db_path,
            sequences_dir=str(sequences_dir),
        )

        # Set global container for backward compatibility
        set_container(_container)

        # Setup event forwarding to WebSocket
        await setup_event_forwarding(_container.event_emitter)

        # Initialize SyncEngine separately (needs additional params not in container)
        from station_service.sync.engine import SyncEngine
        sync_engine = SyncEngine(
            config=config.backend,
            database=_container.database,
            event_emitter=_container.event_emitter,
            station_name=config.station.name,
            station_description=config.station.description,
            server_host=config.server.host,
            server_port=config.server.port,
        )
        await sync_engine.start()
        logger.info("SyncEngine started")

        # Initialize BackendClient for operator authentication
        _backend_client = BackendClient(config=config.backend)
        await _backend_client.connect()

        # Connect TokenManager for automatic token refresh
        from station_service.core.token_manager import get_token_manager
        from station_service.api.routes.system import update_operator_tokens
        token_manager = get_token_manager()
        _backend_client.set_token_manager(token_manager)
        _backend_client.set_token_update_callback(update_operator_tokens)
        logger.info("BackendClient initialized with TokenManager")

        # Initialize AutoSyncService for automatic sequence updates
        sync_service = SequenceSyncService(
            backend_config=config.backend,
            sequences_dir=str(sequences_dir),
        )
        auto_sync_config = AutoSyncConfig(
            enabled=config.git_sync.enabled,
            poll_interval=config.git_sync.poll_interval,
            auto_pull=config.git_sync.auto_pull,
        )
        auto_sync_service = AutoSyncService(
            sync_service=sync_service,
            config=auto_sync_config,
        )
        set_auto_sync_service(auto_sync_service)

        # Start auto-sync if enabled
        if config.git_sync.enabled:
            auto_sync_service.start()
            logger.info(f"AutoSyncService started with interval {config.git_sync.poll_interval}s")
        else:
            logger.info("AutoSyncService initialized (disabled)")

        # Store components in app state for route access
        app.state.config = config
        app.state.database = _container.database
        app.state.batch_manager = _container.batch_manager
        app.state.sync_engine = sync_engine
        app.state.backend_client = _backend_client
        app.state.event_emitter = _container.event_emitter
        app.state.sequence_loader = _container.sequence_loader

        logger.info("Station Service ready")

        yield

    except Exception as e:
        logger.exception(f"Startup error: {e}")
        raise

    finally:
        # Shutdown
        logger.info("Station Service shutting down...")

        if _backend_client:
            await _backend_client.disconnect()
            logger.info("BackendClient disconnected")

        # Shutdown container (handles all other services)
        if _container:
            await _container.shutdown()
            _container = None

        logger.info("Station Service stopped")


def get_cors_origins() -> list[str]:
    """
    Get CORS allowed origins from environment variable.

    Returns:
        List of allowed origins
    """
    cors_origins_env = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    if cors_origins_env:
        return [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    # Default origins for development
    return [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    # Create base app with routers
    app = create_app(
        title="Station Service API",
        description="REST API for Station Service - Test Sequence Execution and Management",
        version="1.0.0",
    )

    # Add lifespan
    app.router.lifespan_context = lifespan

    # Add CORS middleware with configurable origins
    cors_origins = get_cors_origins()
    logger.info(f"CORS allowed origins: {cors_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    # Add WebSocket endpoint
    app.add_api_websocket_route("/ws", websocket_endpoint)

    # Mount static files for UI (if directory exists)
    # NOTE: Static files mounted at /ui to avoid conflict with /api routes
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        from fastapi.responses import RedirectResponse, FileResponse

        # Serve static assets (js, css, images, etc.)
        app.mount("/ui/assets", StaticFiles(directory=str(static_dir / "assets")), name="static-assets")

        # Serve favicon
        @app.get("/ui/favicon.svg", include_in_schema=False)
        async def serve_favicon():
            return FileResponse(static_dir / "favicon.svg")

        # SPA fallback: serve index.html for all /ui/* routes
        @app.get("/ui/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            """Serve index.html for SPA client-side routing."""
            file_path = static_dir / full_path
            # If it's a real file, serve it
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            # Otherwise, serve index.html for client-side routing
            return FileResponse(static_dir / "index.html")

        @app.get("/ui", include_in_schema=False)
        async def serve_ui_root():
            """Serve index.html for /ui (without trailing slash)."""
            return FileResponse(static_dir / "index.html")

        logger.info(f"Serving static files from: {static_dir}")

        # Add redirect from root to /ui
        @app.get("/", include_in_schema=False)
        async def redirect_to_ui():
            return RedirectResponse(url="/ui/")

    return app


# Create application instance
app = create_application()


def main():
    """Main entry point for running the service."""
    import uvicorn

    # Load config for server settings
    try:
        cfg = load_config()
        host = cfg.server.host
        port = cfg.server.port
    except Exception:
        host = "0.0.0.0"
        port = 8080

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "station_service.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
