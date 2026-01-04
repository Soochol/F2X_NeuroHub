"""
Integration tests for API routes.

Tests the FastAPI endpoints with real HTTP requests.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from station_service.api import create_app
from station_service.batch.manager import BatchManager
from station_service.core.events import EventEmitter
from station_service.models.config import (
    BackendConfig,
    BatchConfig,
    LoggingConfig,
    ServerConfig,
    StationConfig,
    StationInfo,
    WorkflowConfig,
)
from station_service.storage.database import Database


class TestSystemRoutes:
    """Test suite for system routes."""

    @pytest.fixture
    def station_config(self) -> StationConfig:
        """Create test config."""
        return StationConfig(
            station=StationInfo(
                id="test_station",
                name="Test Station",
                description="Integration test station",
            ),
            server=ServerConfig(),
            backend=BackendConfig(),
            batches=[
                BatchConfig(
                    id="batch_001",
                    name="Test Batch 1",
                    sequence_package="test_sequence",
                    hardware={},
                ),
                BatchConfig(
                    id="batch_002",
                    name="Test Batch 2",
                    sequence_package="test_sequence_2",
                    hardware={},
                ),
            ],
        )

    @pytest_asyncio.fixture
    async def database(self) -> Database:
        """Create test database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = await Database.create(db_path)
            await db.init_db()
            yield db
            await db.close()

    @pytest.fixture
    def mock_ipc_server(self) -> MagicMock:
        """Create mock IPC server."""
        mock = MagicMock()
        mock.router_address = "tcp://127.0.0.1:5555"
        mock.sub_address = "tcp://127.0.0.1:5557"
        mock.is_running = True
        mock.is_worker_connected = MagicMock(return_value=False)
        mock.send_command = AsyncMock()
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.on_event = MagicMock()
        mock.unregister_worker = MagicMock()
        return mock

    @pytest.fixture
    def mock_sync_engine(self) -> MagicMock:
        """Create mock sync engine."""
        mock = MagicMock()
        mock.is_running = True
        mock.is_connected = True
        mock.backend_url = "http://localhost:8000"
        return mock

    @pytest.fixture
    def mock_sequence_loader(self) -> MagicMock:
        """Create mock sequence loader."""
        mock = MagicMock()
        mock.discover_packages = AsyncMock(return_value=[])
        mock.list_packages = MagicMock(return_value=[])
        mock.load_package = AsyncMock(return_value=None)
        mock.get_package = MagicMock(return_value=None)
        return mock

    @pytest.fixture
    def app(
        self,
        station_config: StationConfig,
        database: Database,
        mock_ipc_server: MagicMock,
        mock_sync_engine: MagicMock,
        mock_sequence_loader: MagicMock,
    ):
        """Create test FastAPI app."""
        app = create_app()
        event_emitter = EventEmitter()

        batch_manager = BatchManager(
            config=station_config,
            ipc_server=mock_ipc_server,
            event_emitter=event_emitter,
        )

        app.state.config = station_config
        app.state.database = database
        app.state.batch_manager = batch_manager
        app.state.event_emitter = event_emitter
        app.state.sync_engine = mock_sync_engine
        app.state.sequence_loader = mock_sequence_loader

        return app

    @pytest.fixture
    def client(self, app) -> TestClient:
        """Create test client."""
        return TestClient(app)

    # ============================================================
    # System Endpoints
    # ============================================================

    def test_health_check(self, client: TestClient):
        """Test /api/system/health endpoint."""
        response = client.get("/api/system/health")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == "healthy"

    def test_station_info(self, client: TestClient):
        """Test /api/system/info endpoint."""
        response = client.get("/api/system/info")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # JSON uses camelCase via APIBaseModel
        assert data["data"]["stationId"] == "test_station"
        assert data["data"]["stationName"] == "Test Station"


class TestBatchRoutes:
    """Test suite for batch routes."""

    @pytest.fixture
    def station_config(self) -> StationConfig:
        """Create test config."""
        return StationConfig(
            station=StationInfo(
                id="test_station",
                name="Test Station",
            ),
            workflow=WorkflowConfig(
                enabled=False,  # Disable workflow for batch route tests
                require_operator_login=False,
            ),
            server=ServerConfig(),
            backend=BackendConfig(),
            batches=[
                BatchConfig(
                    id="batch_001",
                    name="Test Batch",
                    sequence_package="test_sequence",
                    hardware={},
                ),
            ],
        )

    @pytest_asyncio.fixture
    async def database(self) -> Database:
        """Create test database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = await Database.create(db_path)
            await db.init_db()
            yield db
            await db.close()

    @pytest.fixture
    def mock_ipc_server(self) -> MagicMock:
        """Create mock IPC server."""
        mock = MagicMock()
        mock.router_address = "tcp://127.0.0.1:5555"
        mock.sub_address = "tcp://127.0.0.1:5557"
        mock.is_running = True
        mock.is_worker_connected = MagicMock(return_value=True)
        mock.send_command = AsyncMock()
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.wait_for_worker = AsyncMock()
        mock.on_event = MagicMock()
        mock.unregister_worker = MagicMock()
        return mock

    @pytest.fixture
    def mock_sync_engine(self) -> MagicMock:
        """Create mock sync engine."""
        mock = MagicMock()
        mock.is_running = True
        mock.is_connected = True
        mock.backend_url = "http://localhost:8000"
        return mock

    @pytest.fixture
    def mock_sequence_loader(self) -> MagicMock:
        """Create mock sequence loader."""
        mock = MagicMock()
        mock.discover_packages = AsyncMock(return_value=[])
        mock.list_packages = MagicMock(return_value=[])
        mock.load_package = AsyncMock(return_value=None)
        mock.get_package = MagicMock(return_value=None)
        return mock

    @pytest.fixture
    def app(
        self,
        station_config: StationConfig,
        database: Database,
        mock_ipc_server: MagicMock,
        mock_sync_engine: MagicMock,
        mock_sequence_loader: MagicMock,
    ):
        """Create test FastAPI app."""
        app = create_app()
        event_emitter = EventEmitter()

        batch_manager = BatchManager(
            config=station_config,
            ipc_server=mock_ipc_server,
            event_emitter=event_emitter,
        )

        app.state.config = station_config
        app.state.database = database
        app.state.batch_manager = batch_manager
        app.state.event_emitter = event_emitter
        app.state.sync_engine = mock_sync_engine
        app.state.sequence_loader = mock_sequence_loader

        return app

    @pytest.fixture
    def client(self, app) -> TestClient:
        """Create test client."""
        return TestClient(app)

    # ============================================================
    # List Batches
    # ============================================================

    def test_list_batches(self, client: TestClient):
        """Test GET /api/batches returns all batches."""
        response = client.get("/api/batches")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "batch_001"

    # ============================================================
    # Get Batch
    # ============================================================

    def test_get_batch_success(self, client: TestClient):
        """Test GET /api/batches/{id} returns batch details."""
        response = client.get("/api/batches/batch_001")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "batch_001"
        assert data["data"]["name"] == "Test Batch"

    def test_get_batch_not_found(self, client: TestClient):
        """Test GET /api/batches/{id} returns 404 for unknown batch."""
        response = client.get("/api/batches/nonexistent")

        assert response.status_code == 404

    # ============================================================
    # Start Batch
    # ============================================================

    def test_start_batch_not_running(self, client: TestClient):
        """Test POST /api/batches/{id}/start starts batch."""
        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            MockBatchProcess.return_value = mock_process

            response = client.post("/api/batches/batch_001/start")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # JSON uses camelCase via APIBaseModel
            assert data["data"]["batchId"] == "batch_001"
            assert data["data"]["status"] == "started"
            assert data["data"]["pid"] == 12345

    def test_start_batch_not_found(self, client: TestClient):
        """Test POST /api/batches/{id}/start returns 404 for unknown batch."""
        response = client.post("/api/batches/nonexistent/start")

        assert response.status_code == 404

    def test_start_batch_already_running(self, client: TestClient):
        """Test POST /api/batches/{id}/start returns 409 if already running."""
        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            MockBatchProcess.return_value = mock_process

            # Start once
            client.post("/api/batches/batch_001/start")

            # Try to start again
            response = client.post("/api/batches/batch_001/start")

            assert response.status_code == 409

    # ============================================================
    # Stop Batch
    # ============================================================

    def test_stop_batch_not_running(self, client: TestClient):
        """Test POST /api/batches/{id}/stop returns 409 if not running."""
        response = client.post("/api/batches/batch_001/stop")

        assert response.status_code == 409

    def test_stop_batch_success(self, client: TestClient):
        """Test POST /api/batches/{id}/stop stops running batch."""
        with patch(
            "station_service.batch.manager.BatchProcess"
        ) as MockBatchProcess:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.start = AsyncMock()
            mock_process.stop = AsyncMock()
            mock_process.is_alive = True
            MockBatchProcess.return_value = mock_process

            # Start first
            client.post("/api/batches/batch_001/start")

            # Stop
            response = client.post("/api/batches/batch_001/stop")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "stopped"

    # ============================================================
    # Sequence Control
    # ============================================================

    def test_start_sequence_not_running(self, client: TestClient):
        """Test POST /api/batches/{id}/sequence/start returns 409 if batch not running."""
        response = client.post("/api/batches/batch_001/sequence/start")

        assert response.status_code == 409

    def test_stop_sequence_not_running(self, client: TestClient):
        """Test POST /api/batches/{id}/sequence/stop returns 409 if batch not running."""
        response = client.post("/api/batches/batch_001/sequence/stop")

        assert response.status_code == 409


class TestSequenceRoutes:
    """Test suite for sequence routes."""

    @pytest.fixture
    def station_config(self) -> StationConfig:
        """Create test config."""
        return StationConfig(
            station=StationInfo(
                id="test_station",
                name="Test Station",
            ),
            server=ServerConfig(),
            backend=BackendConfig(),
            batches=[
                BatchConfig(
                    id="batch_001",
                    name="Test Batch",
                    sequence_package="test_sequence",
                    hardware={},
                ),
            ],
        )

    @pytest_asyncio.fixture
    async def database(self) -> Database:
        """Create test database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = await Database.create(db_path)
            await db.init_db()
            yield db
            await db.close()

    @pytest.fixture
    def mock_ipc_server(self) -> MagicMock:
        """Create mock IPC server."""
        mock = MagicMock()
        mock.router_address = "tcp://127.0.0.1:5555"
        mock.sub_address = "tcp://127.0.0.1:5557"
        return mock

    @pytest.fixture
    def mock_sync_engine(self) -> MagicMock:
        """Create mock sync engine."""
        mock = MagicMock()
        mock.is_running = True
        mock.is_connected = True
        mock.backend_url = "http://localhost:8000"
        return mock

    @pytest.fixture
    def mock_sequence_loader(self) -> MagicMock:
        """Create mock sequence loader."""
        from station_service.sdk.exceptions import PackageError

        mock = MagicMock()
        mock.discover_packages = AsyncMock(return_value=[])
        mock.list_packages = MagicMock(return_value=[])
        mock.load_package = AsyncMock(side_effect=PackageError("nonexistent_sequence", "Package not found"))
        mock.get_package = MagicMock(return_value=None)
        return mock

    @pytest.fixture
    def app(
        self,
        station_config: StationConfig,
        database: Database,
        mock_ipc_server: MagicMock,
        mock_sync_engine: MagicMock,
        mock_sequence_loader: MagicMock,
    ):
        """Create test FastAPI app."""
        app = create_app()
        event_emitter = EventEmitter()

        batch_manager = BatchManager(
            config=station_config,
            ipc_server=mock_ipc_server,
            event_emitter=event_emitter,
        )

        app.state.config = station_config
        app.state.database = database
        app.state.batch_manager = batch_manager
        app.state.event_emitter = event_emitter
        app.state.sync_engine = mock_sync_engine
        app.state.sequence_loader = mock_sequence_loader

        return app

    @pytest.fixture
    def client(self, app) -> TestClient:
        """Create test client."""
        return TestClient(app)

    # ============================================================
    # List Sequences
    # ============================================================

    def test_list_sequences(self, client: TestClient):
        """Test GET /api/sequences returns available sequences."""
        response = client.get("/api/sequences")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should have at least the sequence from batch config
        assert len(data["data"]) >= 0

    # ============================================================
    # Get Sequence
    # ============================================================

    def test_get_sequence_not_found(self, client: TestClient):
        """Test GET /api/sequences/{name} returns 404 for unknown sequence."""
        response = client.get("/api/sequences/nonexistent_sequence")

        assert response.status_code == 404
