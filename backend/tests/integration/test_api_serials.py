"""Integration tests for Serials API endpoints.

Tests serial number management, tracking, and status transitions
for /api/v1/serials/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestSerialsAPI:
    """Test suite for Serials API endpoints."""

    def test_list_serials_empty(self, client: TestClient, auth_headers_admin: dict):
        """Test listing serials when database is empty."""
        response = client.get("/api/v1/serials/", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_serial_with_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test creating a serial number within a LOT."""
        # Create product model
        product_data = {
            "model_code": "PM-SERIAL-001",
            "model_name": "Serial Test Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        # Create LOT
        lot_data = {
            "lot_number": "LOT-SERIAL-001",
            "product_model_id": product_model_id,
            "planned_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serial
        serial_data = {
            "serial_number": "SN-001-001",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert data["serial_number"] == "SN-001-001"
        assert data["lot_id"] == lot_id
        assert "id" in data

    def test_get_serial_by_id(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving serial by ID."""
        # Setup: Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-GET-SERIAL",
            "model_name": "Get Serial Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-GET-SERIAL",
            "product_model_id": product_model_id,
            "planned_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "serial_number": "SN-GET-001",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        create_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = create_response.json()["id"]

        # Get serial by ID
        response = client.get(f"/api/v1/serials/{serial_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == serial_id
        assert data["serial_number"] == "SN-GET-001"

    @pytest.mark.parametrize("status", [
        "IN_PROGRESS", "PASS", "FAIL", "REWORK", "SCRAPPED"
    ])
    def test_serial_status_values(
        self, client: TestClient, auth_headers_admin: dict, status: str
    ):
        """Test creating serials with different status values."""
        # Create product model and LOT
        product_data = {
            "model_code": f"PM-STATUS-{status}",
            "model_name": f"Status {status} Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 4
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        lot_data = {
            "lot_number": f"LOT-{status}-001",
            "product_model_id": product_model_id,
            "planned_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "serial_number": f"SN-{status}-001",
            "lot_id": lot_id,
            "status": status
        }
        response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        assert response.json()["status"] == status

    def test_update_serial_status(self, client: TestClient, auth_headers_admin: dict):
        """Test updating serial status."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-UPDATE-SERIAL",
            "model_name": "Update Serial Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-UPDATE-SERIAL",
            "product_model_id": product_model_id,
            "planned_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "serial_number": "SN-UPDATE-001",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        create_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = create_response.json()["id"]

        # Update status to PASS
        update_data = {"status": "PASS"}
        response = client.put(
            f"/api/v1/serials/{serial_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["status"] == "PASS"

    def test_serial_rework_handling(self, client: TestClient, auth_headers_admin: dict):
        """Test serial rework tracking."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-REWORK",
            "model_name": "Rework Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-REWORK",
            "product_model_id": product_model_id,
            "planned_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "serial_number": "SN-REWORK-001",
            "lot_id": lot_id,
            "status": "FAIL",
            "failure_reason": "Initial defect"
        }
        create_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = create_response.json()["id"]

        # Update to REWORK
        update_data = {"status": "REWORK", "rework_count": 1}
        response = client.put(
            f"/api/v1/serials/{serial_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200

    def test_delete_serial(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting a serial."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-DEL-SERIAL",
            "model_name": "Delete Serial Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 2
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-DEL-SERIAL",
            "product_model_id": product_model_id,
            "planned_quantity": 3,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "serial_number": "SN-DEL-001",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        create_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = create_response.json()["id"]

        # Delete serial
        response = client.delete(f"/api/v1/serials/{serial_id}", headers=auth_headers_admin)
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/v1/serials/{serial_id}", headers=auth_headers_admin)
        assert get_response.status_code == 404

    def test_get_serial_by_number(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving serial by serial_number."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-BY-NUMBER",
            "model_name": "By Number Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-BY-NUMBER",
            "product_model_id": product_model_id,
            "planned_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "serial_number": "SN-FIND-12345",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Get by serial number
        response = client.get(
            "/api/v1/serials/number/SN-FIND-12345",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["serial_number"] == "SN-FIND-12345"

    def test_serials_require_authentication(self, client: TestClient):
        """Test that serial endpoints require authentication."""
        response = client.get("/api/v1/serials/")
        assert response.status_code == 401

    def test_list_serials_with_pagination(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test pagination of serials list."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-PAGE-SERIAL",
            "model_name": "Page Serial Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        pm_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_model_id = pm_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-PAGE-SERIAL",
            "product_model_id": product_model_id,
            "planned_quantity": 20,
            "status": "IN_PROGRESS",
            "shift": "DAY"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create multiple serials
        for i in range(10):
            serial_data = {
                "serial_number": f"SN-PAGE-{i:05d}",
                "lot_id": lot_id,
                "status": "IN_PROGRESS"
            }
            client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Test pagination
        response = client.get("/api/v1/serials/?skip=0&limit=5", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
