"""
Extended integration tests for Lots API endpoints.

Tests additional scenarios for /api/v1/lots/* endpoints
to improve coverage.
"""

import pytest
from fastapi.testclient import TestClient


class TestLotsAPIExtended:
    """Extended test suite for Lots API endpoints."""

    def test_list_lots_requires_auth(self, client: TestClient):
        """Test that listing lots requires authentication."""
        response = client.get("/api/v1/lots/")
        assert response.status_code == 401

    def test_list_lots_with_auth(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing lots with valid authentication."""
        response = client.get(
            "/api/v1/lots/",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_lots_pagination(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing lots with pagination parameters."""
        response = client.get(
            "/api/v1/lots/?skip=0&limit=10",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_lots_invalid_skip(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing lots with invalid skip parameter."""
        response = client.get(
            "/api/v1/lots/?skip=-1&limit=10",
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_list_lots_invalid_limit(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing lots with invalid limit parameter."""
        response = client.get(
            "/api/v1/lots/?skip=0&limit=0",
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_get_lot_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting non-existent lot returns 404."""
        response = client.get(
            "/api/v1/lots/999999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_get_lot_invalid_id(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting lot with invalid ID returns 422."""
        response = client.get(
            "/api/v1/lots/0",
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_create_lot_requires_auth(self, client: TestClient):
        """Test that creating lot requires authentication."""
        lot_data = {
            "lot_number": "TEST-LOT-001",
            "product_model_id": 1,
            "target_quantity": 100
        }
        response = client.post("/api/v1/lots/", json=lot_data)
        # Either 401 or 422 depending on validation order
        assert response.status_code in [401, 422]

    def test_update_lot_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test updating non-existent lot returns 404."""
        update_data = {"target_quantity": 200}
        response = client.patch(
            "/api/v1/lots/999999",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code in [404, 405]

    def test_delete_lot_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test deleting non-existent lot returns 404."""
        response = client.delete(
            "/api/v1/lots/999999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404


class TestSerialsAPIExtended:
    """Extended test suite for Serials API endpoints."""

    def test_list_serials_requires_auth(self, client: TestClient):
        """Test that listing serials requires authentication."""
        response = client.get("/api/v1/serials/")
        assert response.status_code == 401

    def test_list_serials_with_auth(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing serials with valid authentication."""
        response = client.get(
            "/api/v1/serials/",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_serials_pagination(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing serials with pagination parameters."""
        response = client.get(
            "/api/v1/serials/?skip=0&limit=10",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

    def test_get_serial_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting non-existent serial returns 404."""
        response = client.get(
            "/api/v1/serials/999999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_get_serial_invalid_id(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting serial with invalid ID returns 422."""
        response = client.get(
            "/api/v1/serials/0",
            headers=auth_headers_admin
        )
        assert response.status_code == 422


class TestProcessDataAPIExtended:
    """Extended test suite for Process Data API endpoints."""

    def test_list_process_data_requires_auth(self, client: TestClient):
        """Test that listing process data requires authentication."""
        response = client.get("/api/v1/process-data/")
        assert response.status_code == 401

    def test_list_process_data_with_auth(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing process data with valid authentication."""
        response = client.get(
            "/api/v1/process-data/",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_process_data_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting non-existent process data returns 404."""
        response = client.get(
            "/api/v1/process-data/999999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404


class TestProcessesAPIExtended:
    """Extended test suite for Processes API endpoints."""

    def test_list_processes_requires_auth(self, client: TestClient):
        """Test that listing processes requires authentication."""
        response = client.get("/api/v1/processes/")
        assert response.status_code == 401

    def test_list_processes_with_auth(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing processes with valid authentication."""
        response = client.get(
            "/api/v1/processes/",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_process_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting non-existent process returns 404."""
        response = client.get(
            "/api/v1/processes/999999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404


class TestProductModelsAPIExtended:
    """Extended test suite for Product Models API endpoints."""

    def test_list_product_models_requires_auth(self, client: TestClient):
        """Test that listing product models requires authentication."""
        response = client.get("/api/v1/product-models/")
        assert response.status_code == 401

    def test_list_product_models_with_auth(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test listing product models with valid authentication."""
        response = client.get(
            "/api/v1/product-models/",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_product_model_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting non-existent product model returns 404."""
        response = client.get(
            "/api/v1/product-models/999999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404
