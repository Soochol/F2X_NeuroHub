"""Integration tests for Serials API endpoints.

Tests serial number management, tracking, and status transitions
for /api/v1/serials/* endpoints.
"""

from datetime import date

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
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serial
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert "serial_number" in data  # Auto-generated
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
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        create_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = create_response.json()["id"]
        created_serial_number = create_response.json()["serial_number"]

        # Get serial by ID
        response = client.get(f"/api/v1/serials/{serial_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == serial_id
        assert data["serial_number"] == created_serial_number
        # Verify format: {LOT_NUMBER}-{sequence:04d}
        assert data["serial_number"].endswith("-0001"), f"Expected serial_number to end with -0001, got {data['serial_number']}"
        assert len(data["serial_number"]) > 5, "Serial number should be longer than just sequence"

    @pytest.mark.parametrize("status", [
        "IN_PROGRESS", "PASSED", "FAILED"
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
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": status
        }
        # Add failure_reason if status is FAILED
        if status == "FAILED":
            serial_data["failure_reason"] = "Test failure reason"
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
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        create_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = create_response.json()["id"]

        # Update status to PASSED
        update_data = {"status": "PASSED"}
        response = client.put(
            f"/api/v1/serials/{serial_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["status"] == "PASSED"

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
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "FAILED",
            "failure_reason": "Initial defect"
        }
        create_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = create_response.json()["id"]

        # Test rework by updating rework_count and status to IN_PROGRESS
        # Must clear failure_reason when changing from FAILED to IN_PROGRESS
        update_data = {"status": "IN_PROGRESS", "rework_count": 1, "failure_reason": None}
        response = client.put(
            f"/api/v1/serials/{serial_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["rework_count"] == 1
        assert response.json()["status"] == "IN_PROGRESS"
        assert response.json()["failure_reason"] is None

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
            "production_date": date.today().isoformat(),
            "target_quantity": 3,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
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
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        created_serial = create_response.json()
        serial_number = created_serial["serial_number"]

        # Get by serial number
        response = client.get(
            f"/api/v1/serials/number/{serial_number}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["serial_number"] == serial_number

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
            "production_date": date.today().isoformat(),
            "target_quantity": 20,
            "status": "IN_PROGRESS",
            "shift": "D"
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
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "status": "IN_PROGRESS"
            }
            client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Test pagination
        response = client.get("/api/v1/serials/?skip=0&limit=5", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    # ============================================================================
    # New Comprehensive Tests for Coverage Enhancement
    # ============================================================================

    def test_get_serials_by_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving all serials in a specific lot."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-BY-LOT",
            "model_name": "By Lot Model",
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
            "lot_number": "LOT-FILTER-001",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 15,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create multiple serials in the lot
        created_serials = []
        for i in range(5):
            serial_data = {
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "status": "IN_PROGRESS"
            }
            response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
            created_serials.append(response.json())

        # Get serials by lot
        response = client.get(f"/api/v1/serials/lot/{lot_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        serials = response.json()
        assert len(serials) == 5
        # Verify all serials belong to the lot
        for serial in serials:
            assert serial["lot_id"] == lot_id

    def test_get_serials_by_status(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering serials by status."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-BY-STATUS",
            "model_name": "By Status Model",
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
            "lot_number": "LOT-STATUS-FILTER",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serials with different statuses
        statuses = ["IN_PROGRESS", "IN_PROGRESS", "PASSED", "FAILED"]
        for i, status in enumerate(statuses):
            serial_data = {
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "status": status
            }
            if status == "FAILED":
                serial_data["failure_reason"] = "Test failure"
            client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Filter by IN_PROGRESS status
        response = client.get("/api/v1/serials/status/IN_PROGRESS", headers=auth_headers_admin)
        assert response.status_code == 200
        serials = response.json()
        assert len(serials) == 2
        for serial in serials:
            assert serial["status"] == "IN_PROGRESS"

    def test_get_failed_serials(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving failed serials available for rework."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-FAILED",
            "model_name": "Failed Model",
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
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create failed serials with different rework counts
        for i in range(3):
            serial_data = {
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "status": "FAILED",
                "failure_reason": f"Failure reason {i+1}",
                "rework_count": i if i < 3 else 3
            }
            client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Get failed serials (should only return those with rework_count < 3)
        response = client.get("/api/v1/serials/failed", headers=auth_headers_admin)
        # Debug: print response if it fails
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
        assert response.status_code == 200
        serials = response.json()
        # All serials have rework_count < 3
        for serial in serials:
            assert serial["status"] == "FAILED"
            assert serial["rework_count"] < 3

    def test_check_can_rework(self, client: TestClient, auth_headers_admin: dict):
        """Test checking if serial can be reworked."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-CAN-REWORK",
            "model_name": "Can Rework Model",
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
            "lot_number": "LOT-CAN-REWORK",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create failed serial
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "FAILED",
            "failure_reason": "Initial failure",
            "rework_count": 1
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = create_response.json()["id"]

        # Check if can rework
        response = client.get(f"/api/v1/serials/{serial_id}/can-rework", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert "can_rework" in data
        assert data["can_rework"] is True
        assert data["rework_count"] == 1

    def test_rework_serial(self, client: TestClient, auth_headers_admin: dict):
        """Test reworking a failed serial."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-REWORK-POST",
            "model_name": "Rework Post Model",
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
            "lot_number": "LOT-REWORK-POST",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create failed serial
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "FAILED",
            "failure_reason": "Initial failure"
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = create_response.json()["id"]

        # Start rework
        response = client.post(f"/api/v1/serials/{serial_id}/rework", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
        assert data["rework_count"] == 1

    def test_rework_serial_max_attempts(self, client: TestClient, auth_headers_admin: dict):
        """Test that serial cannot be reworked after max attempts."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-MAX-REWORK",
            "model_name": "Max Rework Model",
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
            "lot_number": "LOT-MAX-REWORK",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create failed serial with max rework count
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "FAILED",
            "failure_reason": "Max attempts",
            "rework_count": 3
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = create_response.json()["id"]

        # Attempt rework (should fail)
        response = client.post(f"/api/v1/serials/{serial_id}/rework", headers=auth_headers_admin)
        assert response.status_code == 400
        assert "Maximum rework count" in response.json()["detail"]

    def test_update_serial_status_endpoint(self, client: TestClient, auth_headers_admin: dict):
        """Test updating serial status via dedicated endpoint."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-STATUS-UPDATE",
            "model_name": "Status Update Model",
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
            "lot_number": "LOT-STATUS-UPDATE",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serial in CREATED status
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "CREATED"
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = create_response.json()["id"]

        # Update to IN_PROGRESS
        status_update = {"status": "IN_PROGRESS"}
        response = client.put(
            f"/api/v1/serials/{serial_id}/status",
            json=status_update,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"

    def test_update_serial_status_to_failed_requires_reason(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test that updating to FAILED status requires failure_reason."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-FAILED-REASON",
            "model_name": "Failed Reason Model",
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
            "lot_number": "LOT-FAILED-REASON",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serial
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = create_response.json()["id"]

        # Try to update to FAILED without failure_reason
        status_update = {"status": "FAILED"}
        response = client.put(
            f"/api/v1/serials/{serial_id}/status",
            json=status_update,
            headers=auth_headers_admin
        )
        assert response.status_code == 400
        assert "failure_reason" in response.json()["detail"].lower()

        # Update with failure_reason (should succeed)
        status_update_with_reason = {
            "status": "FAILED",
            "failure_reason": "Dimension out of tolerance"
        }
        response = client.put(
            f"/api/v1/serials/{serial_id}/status",
            json=status_update_with_reason,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FAILED"
        assert data["failure_reason"] == "Dimension out of tolerance"

    def test_invalid_status_transition(self, client: TestClient, auth_headers_admin: dict):
        """Test that invalid status transitions are rejected."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-INVALID-TRANSITION",
            "model_name": "Invalid Transition Model",
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
            "lot_number": "LOT-INVALID-TRANSITION",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serial in PASSED status
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "PASSED"
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = create_response.json()["id"]

        # Try to transition from PASSED to IN_PROGRESS (should fail)
        status_update = {"status": "IN_PROGRESS"}
        response = client.put(
            f"/api/v1/serials/{serial_id}/status",
            json=status_update,
            headers=auth_headers_admin
        )
        assert response.status_code == 400
        assert "Invalid status transition" in response.json()["detail"]

    def test_get_serial_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting non-existent serial returns 404."""
        response = client.get("/api/v1/serials/99999", headers=auth_headers_admin)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_serial_by_invalid_number(self, client: TestClient, auth_headers_admin: dict):
        """Test getting serial by non-existent serial number."""
        response = client.get(
            "/api/v1/serials/number/INVALID-SERIAL-NUMBER",
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_delete_non_existent_serial(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting non-existent serial returns 404."""
        response = client.delete("/api/v1/serials/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_non_existent_serial(self, client: TestClient, auth_headers_admin: dict):
        """Test updating non-existent serial returns 404."""
        update_data = {"status": "IN_PROGRESS"}
        response = client.put(
            "/api/v1/serials/99999",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_list_serials_with_status_filter(self, client: TestClient, auth_headers_admin: dict):
        """Test listing serials with status query parameter."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-LIST-FILTER",
            "model_name": "List Filter Model",
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
            "lot_number": "LOT-LIST-FILTER",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serials with different statuses
        for i, status in enumerate(["IN_PROGRESS", "PASSED", "IN_PROGRESS"]):
            serial_data = {
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "status": status
            }
            client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Filter by PASSED status
        response = client.get("/api/v1/serials/?status=PASSED", headers=auth_headers_admin)
        assert response.status_code == 200
        serials = response.json()
        assert len(serials) == 1
        assert serials[0]["status"] == "PASSED"

    def test_create_serial_with_invalid_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test creating serial with non-existent lot_id."""
        serial_data = {
            "lot_id": 99999,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        assert response.status_code in [400, 409]

    def test_serial_number_auto_generation(self, client: TestClient, auth_headers_admin: dict):
        """Test that serial_number is auto-generated correctly."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-AUTOGEN",
            "model_name": "Auto Gen Model",
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
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]
        lot_number = lot_response.json()["lot_number"]

        # Create serial
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 5,
            "status": "IN_PROGRESS"
        }
        response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        assert response.status_code == 201
        data = response.json()
        # Verify serial_number format: {LOT_NUMBER}-{sequence:04d}
        assert data["serial_number"] == f"{lot_number}-0005"
        assert data["serial_number"].endswith("-0005")

    def test_serial_multiple_rework_cycles(self, client: TestClient, auth_headers_admin: dict):
        """Test serial going through multiple rework cycles."""
        # Create product model, LOT, and serial
        product_data = {
            "model_code": "PM-MULTI-REWORK",
            "model_name": "Multi Rework Model",
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
            "lot_number": "LOT-MULTI-REWORK",
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 5,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Create serial
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        create_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = create_response.json()["id"]

        # Cycle 1: Fail -> Rework -> Fail
        # Fail first time
        fail_update = {
            "status": "FAILED",
            "failure_reason": "First failure"
        }
        response = client.put(
            f"/api/v1/serials/{serial_id}/status",
            json=fail_update,
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        # Rework
        response = client.post(f"/api/v1/serials/{serial_id}/rework", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json()["rework_count"] == 1

        # Fail second time
        fail_update2 = {
            "status": "FAILED",
            "failure_reason": "Second failure"
        }
        response = client.put(
            f"/api/v1/serials/{serial_id}/status",
            json=fail_update2,
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        # Rework again
        response = client.post(f"/api/v1/serials/{serial_id}/rework", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json()["rework_count"] == 2

        # Final attempt - Pass
        pass_update = {"status": "PASSED"}
        response = client.put(
            f"/api/v1/serials/{serial_id}/status",
            json=pass_update,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PASSED"
        assert data["rework_count"] == 2
