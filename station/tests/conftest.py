"""
Pytest configuration and fixtures for Station Service tests.

Provides shared fixtures for database, event emitters, batch managers,
and other commonly used test dependencies.
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

# Add parent path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from station_service.core.events import Event, EventEmitter, EventType
from station_service.models.config import (
    BackendConfig,
    BatchConfig,
    LoggingConfig,
    ServerConfig,
    StationConfig,
    StationInfo,
)
from station_service.storage.database import Database


# ============================================================
# Event Loop Configuration
# ============================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ============================================================
# Configuration Fixtures
# ============================================================


@pytest.fixture
def station_info() -> StationInfo:
    """Create a test station info."""
    return StationInfo(
        id="test_station_001",
        name="Test Station",
        description="A test station for unit tests",
    )


@pytest.fixture
def server_config() -> ServerConfig:
    """Create a test server config."""
    return ServerConfig(
        host="127.0.0.1",
        port=8080,
    )


@pytest.fixture
def backend_config() -> BackendConfig:
    """Create a test backend config."""
    return BackendConfig(
        url="http://localhost:8000",
        api_key="test_api_key_12345",
        sync_interval=60,
    )


@pytest.fixture
def batch_config() -> BatchConfig:
    """Create a test batch config."""
    return BatchConfig(
        id="batch_001",
        name="Test Batch",
        sequence_package="test_sequence",
        hardware={
            "power_supply": {
                "type": "mock",
                "port": "/dev/ttyUSB0",
            },
        },
        auto_start=False,
    )


@pytest.fixture
def station_config(
    station_info: StationInfo,
    server_config: ServerConfig,
    backend_config: BackendConfig,
    batch_config: BatchConfig,
) -> StationConfig:
    """Create a complete test station config."""
    return StationConfig(
        station=station_info,
        server=server_config,
        backend=backend_config,
        batches=[batch_config],
        logging=LoggingConfig(),
    )


# ============================================================
# Database Fixtures
# ============================================================


@pytest_asyncio.fixture
async def temp_db_path() -> AsyncGenerator[Path, None]:
    """Create a temporary database file path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_station.db"
        yield db_path


@pytest_asyncio.fixture
async def database(temp_db_path: Path) -> AsyncGenerator[Database, None]:
    """Create and initialize a test database."""
    db = await Database.create(temp_db_path)
    await db.init_db()
    yield db
    await db.close()


# ============================================================
# Event System Fixtures
# ============================================================


@pytest.fixture
def event_emitter() -> EventEmitter:
    """Create a fresh event emitter for testing."""
    return EventEmitter()


@pytest.fixture
def sample_event() -> Event:
    """Create a sample event for testing."""
    return Event(
        type=EventType.BATCH_STARTED,
        batch_id="batch_001",
        data={"pid": 12345},
    )


# ============================================================
# Mock Fixtures
# ============================================================


@pytest.fixture
def mock_ipc_server() -> MagicMock:
    """Create a mock IPC server."""
    mock = MagicMock()
    mock.router_address = "tcp://127.0.0.1:5555"
    mock.sub_address = "tcp://127.0.0.1:5557"
    mock.is_running = True
    mock.is_worker_connected = MagicMock(return_value=True)
    mock.send_command = AsyncMock(return_value=MagicMock(
        status="ok",
        data={"status": "running"},
        error=None,
    ))
    mock.start = AsyncMock()
    mock.stop = AsyncMock()
    mock.on_event = MagicMock()
    mock.unregister_worker = MagicMock()
    return mock


@pytest.fixture
def mock_batch_process() -> MagicMock:
    """Create a mock batch process."""
    mock = MagicMock()
    mock.batch_id = "batch_001"
    mock.pid = 12345
    mock.is_alive = True
    mock.exit_code = None
    mock.start = AsyncMock()
    mock.stop = AsyncMock()
    return mock


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Create a mock HTTP client for sync engine tests."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=MagicMock(status_code=200))
    mock.post = AsyncMock(return_value=MagicMock(status_code=201))
    mock.put = AsyncMock(return_value=MagicMock(status_code=200))
    mock.aclose = AsyncMock()
    return mock


# ============================================================
# Sequence Testing Fixtures
# ============================================================


@pytest.fixture
def sample_step_meta() -> Dict[str, Any]:
    """Create sample step metadata."""
    return {
        "order": 1,
        "timeout": 30.0,
        "retry": 2,
        "cleanup": False,
        "condition": None,
        "name": "test_step",
        "description": "A test step",
    }


@pytest.fixture
def sample_sequence_manifest() -> Dict[str, Any]:
    """Create a sample sequence manifest."""
    return {
        "name": "test_sequence",
        "version": "1.0.0",
        "display_name": "Test Sequence",
        "description": "A test sequence for unit tests",
        "entry_point": {
            "module": "sequence",
            "class_name": "TestSequence",
        },
        "hardware": {},
        "parameters": {},
        "steps": [
            {
                "name": "step_1",
                "order": 1,
                "timeout": 30.0,
            },
            {
                "name": "step_2",
                "order": 2,
                "timeout": 60.0,
            },
        ],
    }


# ============================================================
# FastAPI Test Client Fixture
# ============================================================


@pytest_asyncio.fixture
async def test_app(
    station_config: StationConfig,
    database: Database,
    event_emitter: EventEmitter,
    mock_ipc_server: MagicMock,
):
    """Create a test FastAPI application with mocked dependencies."""
    from fastapi.testclient import TestClient
    from station_service.api import create_app
    from station_service.batch.manager import BatchManager

    app = create_app()

    # Create batch manager with mock IPC
    batch_manager = BatchManager(
        config=station_config,
        ipc_server=mock_ipc_server,
        event_emitter=event_emitter,
    )

    # Set up app state
    app.state.config = station_config
    app.state.database = database
    app.state.batch_manager = batch_manager
    app.state.event_emitter = event_emitter
    app.state.sync_engine = None

    yield app

    # Cleanup
    if batch_manager.is_running:
        await batch_manager.stop()


@pytest.fixture
def test_client(test_app) -> Generator:
    """Create a test client for API testing."""
    from fastapi.testclient import TestClient

    with TestClient(test_app) as client:
        yield client


# ============================================================
# Helper Functions
# ============================================================


def assert_event_emitted(
    event_emitter: EventEmitter,
    event_type: EventType,
    handler_mock: MagicMock,
) -> None:
    """Assert that an event of the specified type was emitted."""
    calls = handler_mock.call_args_list
    event_types = [call[0][0].type for call in calls]
    assert event_type in event_types, f"Event {event_type} was not emitted"


async def wait_for_condition(
    condition_func,
    timeout: float = 5.0,
    interval: float = 0.1,
) -> bool:
    """Wait for a condition to become true."""
    elapsed = 0.0
    while elapsed < timeout:
        if condition_func():
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False


# ============================================================
# Manual Sequence Testing Fixtures
# ============================================================


@pytest.fixture
def mock_driver():
    """Mock 드라이버."""
    driver = AsyncMock()
    driver.connect = AsyncMock(return_value=True)
    driver.disconnect = AsyncMock()
    driver.connected = True
    driver.ping = AsyncMock(return_value={"status": "ok"})
    driver.get_sensor_list = AsyncMock(return_value=["sensor1", "sensor2"])
    return driver


@pytest.fixture
def mock_sequence():
    """Mock 시퀀스 클래스."""
    class MockSequence:
        async def setup(self, hw):
            pass

        async def teardown(self, hw):
            pass

        async def initialize(self, hw):
            return {"initialized": True}

        async def test_step(self, hw):
            return {"test": "passed", "value": 42}

        async def finalize(self, hw):
            return {"finalized": True}

    return MockSequence


@pytest.fixture
def mock_manifest():
    """Mock manifest for manual sequence."""
    return {
        "name": "test_sequence",
        "display_name": "Test Sequence",
        "version": "1.0.0",
        "hardware": {
            "test_device": {
                "display_name": "Test Device",
                "driver": "test_driver.TestDriver",
                "config": {"port": "/dev/ttyUSB0"},
            }
        },
        "steps": [
            {
                "name": "initialize",
                "display_name": "Initialize",
                "method": "initialize",
                "order": 1,
                "skippable": False,
            },
            {
                "name": "test_step",
                "display_name": "Test Step",
                "method": "test_step",
                "order": 2,
                "skippable": True,
            },
            {
                "name": "finalize",
                "display_name": "Finalize",
                "method": "finalize",
                "order": 3,
                "skippable": False,
            },
        ],
    }


@pytest.fixture
def mock_executor():
    """Mock ManualSequenceExecutor."""
    from station_service.sdk.manual_executor import (
        ManualSession,
        ManualSessionStatus,
        ManualStepState,
        ManualStepStatus,
        HardwareState,
        CommandResult,
    )

    executor = MagicMock()

    # Default session
    mock_session = ManualSession(
        id="test-session-123",
        sequence_name="test_sequence",
        sequence_version="1.0.0",
        status=ManualSessionStatus.CREATED,
        steps=[
            ManualStepState(
                name="initialize",
                display_name="Initialize",
                order=1,
                skippable=False,
            ),
            ManualStepState(
                name="test_step",
                display_name="Test Step",
                order=2,
                skippable=True,
            ),
        ],
        hardware=[
            HardwareState(
                id="test_device",
                display_name="Test Device",
            )
        ],
    )

    executor.create_session = AsyncMock(return_value=mock_session)
    executor.get_session = AsyncMock(return_value=mock_session)
    executor.list_sessions = AsyncMock(return_value=[mock_session])
    executor.delete_session = AsyncMock(return_value=True)
    executor.initialize_session = AsyncMock(return_value=mock_session)
    executor.finalize_session = AsyncMock(return_value=mock_session)
    executor.abort_session = AsyncMock(return_value=mock_session)
    executor.run_step = AsyncMock(
        return_value=ManualStepState(
            name="test_step",
            display_name="Test Step",
            order=1,
            skippable=True,
            status=ManualStepStatus.PASSED,
            duration=0.5,
            result={"test": "passed"},
        )
    )
    executor.skip_step = AsyncMock(
        return_value=ManualStepState(
            name="test_step",
            display_name="Test Step",
            order=1,
            skippable=True,
            status=ManualStepStatus.SKIPPED,
        )
    )
    executor.execute_hardware_command = AsyncMock(
        return_value=CommandResult(
            success=True,
            hardware_id="test_device",
            command="ping",
            result={"status": "ok"},
            duration=0.05,
        )
    )
    executor.get_hardware_commands = AsyncMock(
        return_value=[
            {"name": "ping", "display_name": "Ping", "parameters": []},
            {"name": "reset", "display_name": "Reset", "parameters": []},
        ]
    )

    return executor


@pytest_asyncio.fixture
async def async_client(test_app):
    """비동기 테스트 클라이언트."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
