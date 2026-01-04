"""
Unit tests for BackendClient.

Tests WIP lookup, process start/complete, and error handling.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from station_service.core.exceptions import (
    BackendConnectionError,
    BackendError,
    DuplicatePassError,
    PrerequisiteNotMetError,
    WIPNotFoundError,
)
from station_service.models.config import BackendConfig
from station_service.sync.backend_client import BackendClient
from station_service.sync.models import (
    ProcessCompleteRequest,
    ProcessStartRequest,
    SerialConvertRequest,
)


@pytest.fixture
def backend_config():
    """Create test BackendConfig."""
    return BackendConfig(
        url="http://test-backend:8000",
        api_key="test-api-key",
        station_id="station-1",
        equipment_id=1,
        timeout=10.0,
    )


@pytest.fixture
def backend_client(backend_config):
    """Create BackendClient instance."""
    return BackendClient(backend_config)


class TestBackendClientConnection:
    """Tests for BackendClient connection management."""

    @pytest.mark.asyncio
    async def test_connect_creates_http_client(self, backend_client):
        """Test that connect creates HTTP client with proper headers."""
        await backend_client.connect()

        assert backend_client.is_connected
        assert backend_client._client is not None

        # Verify headers
        headers = backend_client._client.headers
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["X-Station-ID"] == "station-1"
        assert headers["X-Equipment-ID"] == "1"

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_cleans_up(self, backend_client):
        """Test that disconnect cleans up resources."""
        await backend_client.connect()
        await backend_client.disconnect()

        assert not backend_client.is_connected
        assert backend_client._client is None

    @pytest.mark.asyncio
    async def test_context_manager(self, backend_client):
        """Test async context manager support."""
        async with backend_client as client:
            assert client.is_connected

        assert not backend_client.is_connected


class TestWIPLookup:
    """Tests for WIP lookup functionality."""

    @pytest.mark.asyncio
    async def test_lookup_wip_success(self, backend_client):
        """Test successful WIP lookup."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "wip_id": "WIP-KR01PSA2511-001",
            "status": "IN_PROGRESS",
            "lot_id": 10,
            "sequence_in_lot": 1,
            "current_process_id": None,
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()
            result = await backend_client.lookup_wip("WIP-KR01PSA2511-001")

            assert result.id == 123
            assert result.wip_id == "WIP-KR01PSA2511-001"
            assert result.status == "IN_PROGRESS"
            assert result.lot_id == 10

            mock_post.assert_called_once()

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_lookup_wip_not_found(self, backend_client):
        """Test WIP lookup when WIP not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": "WIP_NOT_FOUND",
            "message": "WIP not found",
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            with pytest.raises(WIPNotFoundError) as exc_info:
                await backend_client.lookup_wip("WIP-INVALID-999")

            assert "WIP-INVALID-999" in str(exc_info.value)

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_lookup_wip_connection_error(self, backend_client):
        """Test WIP lookup when connection fails."""
        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection refused")

            await backend_client.connect()

            with pytest.raises(BackendConnectionError):
                await backend_client.lookup_wip("WIP-KR01PSA2511-001")

        await backend_client.disconnect()


class TestStartProcess:
    """Tests for start_process (착공) functionality."""

    @pytest.mark.asyncio
    async def test_start_process_success(self, backend_client):
        """Test successful process start."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "wip_item": {"id": 123, "status": "IN_PROGRESS"},
            "message": "Process started successfully",
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            request = ProcessStartRequest(
                process_id=1,
                operator_id=5,
                equipment_id=1,
            )
            result = await backend_client.start_process(123, request)

            assert result["wip_item"]["status"] == "IN_PROGRESS"
            mock_post.assert_called_once()

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_start_process_prerequisite_not_met(self, backend_client):
        """Test start_process when prerequisite not met (BR-003)."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "PREREQUISITE_NOT_MET",
            "message": "Process 1 must be completed first",
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            request = ProcessStartRequest(
                process_id=2,
                operator_id=5,
            )

            with pytest.raises(PrerequisiteNotMetError):
                await backend_client.start_process(123, request)

        await backend_client.disconnect()


class TestCompleteProcess:
    """Tests for complete_process (완공) functionality."""

    @pytest.mark.asyncio
    async def test_complete_process_success(self, backend_client):
        """Test successful process completion."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "process_history": {
                "id": 1,
                "result": "PASS",
                "duration_seconds": 120,
            },
            "wip_item": {"id": 123, "status": "IN_PROGRESS"},
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            request = ProcessCompleteRequest(
                result="PASS",
                measurements={"temperature": 98.5, "cycle_time_ms": 15000},
                defects=[],
            )
            result = await backend_client.complete_process(123, 1, 5, request)

            assert result["process_history"]["result"] == "PASS"
            mock_post.assert_called_once()

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_complete_process_duplicate_pass(self, backend_client):
        """Test complete_process when duplicate PASS (BR-004)."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "DUPLICATE_PASS",
            "message": "Duplicate PASS not allowed",
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            request = ProcessCompleteRequest(result="PASS")

            with pytest.raises(DuplicatePassError):
                await backend_client.complete_process(123, 1, 5, request)

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_complete_process_with_defects(self, backend_client):
        """Test process completion with defects."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "process_history": {"id": 1, "result": "FAIL"},
            "wip_item": {"id": 123, "status": "FAILED"},
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            request = ProcessCompleteRequest(
                result="FAIL",
                measurements={"temperature": 105.0},
                defects=["DEF001", "DEF003"],
                notes="Visual inspection failed",
            )
            result = await backend_client.complete_process(123, 1, 5, request)

            assert result["process_history"]["result"] == "FAIL"
            assert result["wip_item"]["status"] == "FAILED"

        await backend_client.disconnect()


class TestConvertToSerial:
    """Tests for convert_to_serial functionality."""

    @pytest.mark.asyncio
    async def test_convert_to_serial_success(self, backend_client):
        """Test successful serial conversion."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "serial": {
                "id": 1,
                "serial_number": "SN-KR01PSA2511-001",
                "status": "CREATED",
            },
            "wip_item": {"id": 123, "status": "CONVERTED"},
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            request = SerialConvertRequest(
                operator_id=5,
                notes="Final inspection passed",
            )
            result = await backend_client.convert_to_serial(123, request)

            assert result["serial"]["serial_number"] == "SN-KR01PSA2511-001"
            assert result["wip_item"]["status"] == "CONVERTED"

        await backend_client.disconnect()


class TestHealthCheck:
    """Tests for health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, backend_client):
        """Test successful health check."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(
            httpx.AsyncClient, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_response

            await backend_client.connect()
            result = await backend_client.health_check()

            assert result is True

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, backend_client):
        """Test health check when backend is down."""
        with patch.object(
            httpx.AsyncClient, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection refused")

            await backend_client.connect()
            result = await backend_client.health_check()

            assert result is False

        await backend_client.disconnect()


class TestLogin:
    """Tests for login functionality."""

    @pytest.mark.asyncio
    async def test_login_success(self, backend_client):
        """Test successful operator login."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "jwt_token_12345",
            "token_type": "bearer",
            "user": {
                "id": 123,
                "username": "test_operator",
                "name": "Test Operator",
                "role": "OPERATOR",
            },
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()
            result = await backend_client.login(
                username="test_operator",
                password="password123",
            )

            assert result["access_token"] == "jwt_token_12345"
            assert result["user"]["id"] == 123
            assert result["user"]["username"] == "test_operator"
            mock_post.assert_called_once()

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, backend_client):
        """Test login with invalid credentials."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": "AUTH_FAILED",
            "message": "Invalid username or password",
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            await backend_client.connect()

            with pytest.raises(BackendError) as exc_info:
                await backend_client.login(
                    username="wrong_user",
                    password="wrong_pass",
                )

            # Check the error message contains the expected text
            assert "Invalid username or password" in str(exc_info.value)

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_login_connection_error(self, backend_client):
        """Test login when connection fails."""
        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection refused")

            await backend_client.connect()

            with pytest.raises(BackendConnectionError):
                await backend_client.login(
                    username="test",
                    password="password",
                )

        await backend_client.disconnect()

    @pytest.mark.asyncio
    async def test_login_client_not_connected(self, backend_client):
        """Test login when client is not connected."""
        # Don't call connect()
        with pytest.raises(BackendConnectionError):
            await backend_client.login(
                username="test",
                password="password",
            )
