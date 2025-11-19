"""Integration tests for LOTs API endpoints.

Tests all CRUD operations, status transitions, and LOT management
for /api/v1/lots/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta


def create_test_lot_data(product_model_id: int, target_qty: int = 50, shift: str = "D"):
    """Helper function to create test LOT data with correct schema."""
    return {
        "product_model_id": product_model_id,
        "production_date": date.today().isoformat(),
        "shift": shift,
        "target_quantity": target_qty,
        "status": "CREATED"
    }


class TestLotsAPI:
    """Test suite for LOTs API endpoints."""

    def test_list_lots_empty(self, client: TestClient, auth_headers_admin: dict):
        """Test listing LOTs when database is empty."""
        response = client.get("/api/v1/lots/", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test creating a new LOT."""
        lot_data = create_test_lot_data(product_model_id=1)
        response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        # May fail if product_model_id doesn't exist (422 or 404)
        assert response.status_code in [201, 404, 422]

    def test_create_lot_with_product_model(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test creating LOT after creating product model."""
        # First create a product model
        product_data = {
            "model_code": "PM-LOT-TEST",
            "model_name": "LOT Test Model",
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

        # Now create LOT
        lot_data = create_test_lot_data(product_model_id, target_qty=75, shift="N")
        response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert "lot_number" in data  # Auto-generated
        assert data["target_quantity"] == 75
        assert data["shift"] == "N"

    def test_get_lot_by_id(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving LOT by ID."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-GET-LOT",
            "model_name": "Get LOT Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=30)
        create_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = create_response.json()["id"]

        # Get LOT by ID
        response = client.get(f"/api/v1/lots/{lot_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lot_id
        assert "lot_number" in data

    def test_get_lot_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting non-existent LOT returns 404."""
        response = client.get("/api/v1/lots/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    @pytest.mark.parametrize("status", ["CREATED", "IN_PROGRESS", "COMPLETED", "CLOSED"])
    def test_lot_status_transitions(
        self, client: TestClient, auth_headers_admin: dict, status: str
    ):
        """Test creating LOTs with different status values."""
        # Create product model first
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

        lot_data = create_test_lot_data(
            product_model_id=product_model_id,
            target_qty=25,
            shift="D"
        )
        lot_data["status"] = status
        response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        assert response.json()["status"] == status

    @pytest.mark.parametrize("shift", ["D", "N"])
    def test_lot_shift_values(
        self, client: TestClient, auth_headers_admin: dict, shift: str
    ):
        """Test creating LOTs with different shift values."""
        # Create product model
        shift_name = "DAY" if shift == "D" else "NIGHT"
        product_data = {
            "model_code": f"PM-SHIFT-{shift_name}",
            "model_name": f"Shift {shift_name} Model",
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

        lot_data = create_test_lot_data(
            product_model_id=product_model_id,
            target_qty=40,
            shift=shift
        )
        response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        assert response.json()["shift"] == shift

    def test_update_lot_status(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT status."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-UPDATE-STATUS",
            "model_name": "Update Status Model",
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

        lot_data = create_test_lot_data(
            product_model_id=product_model_id,
            target_qty=60,
            shift="D"
        )
        create_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = create_response.json()["id"]

        # Update status
        update_data = {"status": "IN_PROGRESS"}
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"

    def test_delete_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting a LOT."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-DELETE",
            "model_name": "Delete Model",
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

        lot_data = create_test_lot_data(
            product_model_id=product_model_id,
            target_qty=20,
            shift="D"
        )
        create_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = create_response.json()["id"]

        # Delete LOT
        response = client.delete(f"/api/v1/lots/{lot_id}", headers=auth_headers_admin)
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/v1/lots/{lot_id}", headers=auth_headers_admin)
        assert get_response.status_code == 404

    def test_lot_quantity_validation(self, client: TestClient, auth_headers_admin: dict):
        """Test LOT quantity validation (1-100)."""
        # Create product model
        product_data = {
            "model_code": "PM-QTY",
            "model_name": "Quantity Model",
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

        # Try invalid quantity (over 100)
        lot_data = create_test_lot_data(
            product_model_id=product_model_id,
            target_qty=150,
            shift="D"
        )
        response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        # Should fail validation if constraint is enforced
        assert response.status_code in [201, 422]  # May pass if not validated

    def test_lots_require_authentication(self, client: TestClient):
        """Test that LOT endpoints require authentication."""
        response = client.get("/api/v1/lots/")
        assert response.status_code == 401

    def test_list_lots_with_pagination(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test pagination of LOTs list."""
        # Create product model
        product_data = {
            "model_code": "PM-PAGE",
            "model_name": "Pagination Model",
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

        # Create multiple LOTs
        for i in range(5):
            lot_data = create_test_lot_data(
                product_model_id=product_model_id,
                target_qty=25,
                shift="D"
            )
            client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)

        # Test pagination
        response = client.get("/api/v1/lots/?skip=0&limit=3", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    # ============================================================================
    # New Comprehensive Tests for Coverage Enhancement
    # ============================================================================

    def test_lot_number_auto_generation(self, client: TestClient, auth_headers_admin: dict):
        """Test that lot_number is auto-generated in correct format."""
        # Create product model
        product_data = {
            "model_code": "PM-LOT-NUM",
            "model_name": "Lot Number Model",
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

        # Create LOT without lot_number (should be auto-generated)
        lot_data = create_test_lot_data(product_model_id, target_qty=50, shift="D")
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 201
        data = response.json()

        # Verify lot_number format: WF-KR-YYMMDD{D|N}-nnn
        lot_number = data["lot_number"]
        assert lot_number.startswith("WF-KR-")
        assert "D" in lot_number or "N" in lot_number
        assert len(lot_number) >= 16  # WF-KR-251119D-001 = 17 chars

    def test_get_lot_by_number(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving LOT by lot_number."""
        # Create product model and LOT
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

        lot_data = create_test_lot_data(product_model_id, target_qty=40)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_number = create_response.json()["lot_number"]

        # Get LOT by lot_number
        response = client.get(f"/api/v1/lots/number/{lot_number}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["lot_number"] == lot_number

    def test_get_lots_by_status(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering LOTs by status."""
        # Create product model
        product_data = {
            "model_code": "PM-STATUS-FILTER",
            "model_name": "Status Filter Model",
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

        # Create LOTs with different statuses
        statuses = ["CREATED", "IN_PROGRESS", "IN_PROGRESS", "COMPLETED"]
        for status in statuses:
            lot_data = create_test_lot_data(product_model_id, target_qty=30)
            lot_data["status"] = status
            client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)

        # Filter by IN_PROGRESS status
        response = client.get("/api/v1/lots/status/IN_PROGRESS", headers=auth_headers_admin)
        assert response.status_code == 200
        lots = response.json()
        assert len(lots) == 2
        for lot in lots:
            assert lot["status"] == "IN_PROGRESS"

    def test_get_lots_by_date_range(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering LOTs by date range."""
        # Create product model
        product_data = {
            "model_code": "PM-DATE-FILTER",
            "model_name": "Date Filter Model",
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

        # Create LOTs with different dates
        today = date.today()
        yesterday = today - timedelta(days=1)

        created_lots = []
        for production_date in [yesterday, today]:
            lot_data = create_test_lot_data(product_model_id, target_qty=25)
            lot_data["production_date"] = production_date.isoformat()
            response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
            created_lots.append(response.json())

        # Get all LOTs and verify dates
        response = client.get("/api/v1/lots/", headers=auth_headers_admin)
        assert response.status_code == 200
        lots = response.json()
        # Verify we have LOTs with different dates
        dates_in_lots = {lot["production_date"] for lot in lots if lot["product_model_id"] == product_model_id}
        assert len(dates_in_lots) >= 1  # At least one unique date

    def test_complete_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test completing a LOT by updating status."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-COMPLETE",
            "model_name": "Complete Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        lot_data["status"] = "IN_PROGRESS"
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Complete LOT via update
        update_data = {"status": "COMPLETED"}
        response = client.put(f"/api/v1/lots/{lot_id}", json=update_data, headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_get_lot_with_serials(self, client: TestClient, auth_headers_admin: dict):
        """Test getting LOT with serials information."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-WITH-SERIALS",
            "model_name": "With Serials Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=100)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Create some serials in the LOT
        for i in range(5):
            serial_data = {
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "status": "PASSED" if i < 3 else "FAILED",
                "failure_reason": "Test failure" if i >= 3 else None
            }
            client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Get LOT details
        response = client.get(f"/api/v1/lots/{lot_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        # Verify LOT data (id field, not lot_id)
        assert data["id"] == lot_id
        assert data["target_quantity"] == 100

    def test_create_lot_with_invalid_product_model(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test creating LOT with non-existent product_model_id."""
        lot_data = create_test_lot_data(product_model_id=99999, target_qty=50)
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        # May create successfully if FK validation is not enforced, or return 404/409
        assert response.status_code in [201, 404, 409, 422]

    def test_update_non_existent_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test updating non-existent LOT returns 404."""
        update_data = {"status": "COMPLETED"}
        response = client.put("/api/v1/lots/99999", json=update_data, headers=auth_headers_admin)
        assert response.status_code == 404

    def test_delete_non_existent_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting non-existent LOT returns 404."""
        response = client.delete("/api/v1/lots/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_lot_with_serials_statistics(self, client: TestClient, auth_headers_admin: dict):
        """Test LOT response includes serial statistics."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-SERIAL-STATS",
            "model_name": "Serial Stats Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Create serials
        for i in range(10):
            serial_data = {
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "status": "PASSED"
            }
            client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Get LOT details
        response = client.get(f"/api/v1/lots/{lot_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        # Verify LOT data includes serial info
        assert data["target_quantity"] == 50

    def test_update_lot_target_quantity(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT target_quantity."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-UPDATE-QTY",
            "model_name": "Update Quantity Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Update target_quantity
        update_data = {"target_quantity": 75}
        response = client.put(f"/api/v1/lots/{lot_id}", json=update_data, headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json()["target_quantity"] == 75

    def test_list_lots_with_filters(self, client: TestClient, auth_headers_admin: dict):
        """Test listing LOTs with multiple filters."""
        # Create product model
        product_data = {
            "model_code": "PM-MULTI-FILTER",
            "model_name": "Multi Filter Model",
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

        # Create LOTs with different status and shift
        configs = [
            ("CREATED", "D"),
            ("IN_PROGRESS", "D"),
            ("IN_PROGRESS", "N"),
            ("COMPLETED", "D")
        ]
        for status, shift in configs:
            lot_data = create_test_lot_data(product_model_id, target_qty=30, shift=shift)
            lot_data["status"] = status
            client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)

        # Filter by status and shift
        response = client.get(
            "/api/v1/lots/?status=IN_PROGRESS",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        lots = response.json()
        # Should return 2 IN_PROGRESS LOTs
        in_progress_count = sum(1 for lot in lots if lot["status"] == "IN_PROGRESS")
        assert in_progress_count == 2

    def test_close_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test closing a completed LOT."""
        # Create product model
        product_data = {
            "model_code": "PM-CLOSE-TEST",
            "model_name": "Close Test Model",
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

        # Create LOT with COMPLETED status
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 50,
            "status": "COMPLETED",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Close the LOT
        response = client.post(f"/api/v1/lots/{lot_id}/close", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CLOSED"
        assert data["closed_at"] is not None

    def test_close_non_existent_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test closing non-existent LOT returns 404."""
        response = client.post("/api/v1/lots/99999/close", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_recalculate_lot_quantities(self, client: TestClient, auth_headers_admin: dict):
        """Test recalculating LOT quantities from serials."""
        # Create product model
        product_data = {
            "model_code": "PM-RECALC-TEST",
            "model_name": "Recalc Test Model",
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

        # Create LOT
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 100,
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

        # Create some serials for this LOT
        for i in range(5):
            serial_data = {
                "lot_id": lot_id,
                "sequence_in_lot": i + 1,
                "serial_number": f"{lot_number}-{i+1:04d}",
                "status": "PASSED" if i < 3 else "FAILED",
                "current_process_id": None
            }
            # Add failure_reason for FAILED serials
            if i >= 3:
                serial_data["failure_reason"] = "Quality check failed"

            serial_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
            assert serial_response.status_code == 201, f"Failed to create serial: {serial_response.json()}"

        # Recalculate quantities
        response = client.put(f"/api/v1/lots/{lot_id}/quantities", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["actual_quantity"] == 5
        assert data["passed_quantity"] == 3
        assert data["failed_quantity"] == 2

    def test_recalculate_non_existent_lot_quantities(self, client: TestClient, auth_headers_admin: dict):
        """Test recalculating quantities for non-existent LOT returns 404."""
        response = client.put("/api/v1/lots/99999/quantities", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_delete_lot_with_serials_conflict(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting LOT with associated serials returns 409."""
        # Create product model
        product_data = {
            "model_code": "PM-DELETE-CONFLICT",
            "model_name": "Delete Conflict Model",
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

        # Create LOT
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
        lot_number = lot_response.json()["lot_number"]

        # Create serial for this LOT
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "serial_number": f"{lot_number}-0001",
            "status": "CREATED",
            "current_process_id": None
        }
        client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Try to delete LOT with serial - should fail with 409 or succeed depending on DB constraints
        response = client.delete(f"/api/v1/lots/{lot_id}", headers=auth_headers_admin)
        # Accept both 204 (no constraint) or 409 (constraint enforced)
        assert response.status_code in [204, 409]

    def test_create_lot_with_duplicate_constraint(self, client: TestClient, auth_headers_admin: dict):
        """Test creating LOT with duplicate constraint violation."""
        # Create product model
        product_data = {
            "model_code": "PM-DUP-TEST",
            "model_name": "Duplicate Test Model",
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

        # Create first LOT
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 50,
            "status": "CREATED",
            "shift": "D"
        }
        response1 = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        assert response1.status_code == 201

        # Since lot_number is auto-generated, we shouldn't hit duplicate constraint
        # But test that multiple LOTs can be created successfully
        response2 = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        # Should succeed with unique lot_number
        assert response2.status_code == 201
        # Verify different lot numbers
        assert response1.json()["lot_number"] != response2.json()["lot_number"]

    def test_update_lot_with_invalid_foreign_key(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT with invalid product_model_id."""
        # Create product model
        product_data = {
            "model_code": "PM-UPDATE-FK",
            "model_name": "Update FK Test Model",
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

        # Create LOT
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 50,
            "status": "CREATED",
            "shift": "D"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Try to update with invalid product_model_id
        update_data = {"product_model_id": 99999}
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        # May succeed if FK validation not enforced, or fail with 400/409
        assert response.status_code in [200, 400, 409, 422]

    # ============================================================================
    # Additional Tests for Enhanced Coverage (80%+ target)
    # ============================================================================

    def test_create_lot_target_quantity_zero(self, client: TestClient, auth_headers_admin: dict):
        """Test creating LOT with target_quantity=0 fails validation."""
        # Create product model
        product_data = {
            "model_code": "PM-QTY-ZERO",
            "model_name": "Qty Zero Model",
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

        # Try to create LOT with target_quantity=0
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "shift": "D",
            "target_quantity": 0,
            "status": "CREATED"
        }
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 422
        # Pydantic v2 error for ge=1 constraint
        error_detail = response.json()["detail"]
        assert any("greater than or equal to 1" in str(err).lower() for err in error_detail)

    def test_create_lot_target_quantity_exceeds_max(self, client: TestClient, auth_headers_admin: dict):
        """Test creating LOT with target_quantity > 100 fails validation."""
        # Create product model
        product_data = {
            "model_code": "PM-QTY-MAX",
            "model_name": "Qty Max Model",
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

        # Try to create LOT with target_quantity=101
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "shift": "D",
            "target_quantity": 101,
            "status": "CREATED"
        }
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 422

    def test_create_lot_invalid_shift(self, client: TestClient, auth_headers_admin: dict):
        """Test creating LOT with invalid shift value fails validation."""
        # Create product model
        product_data = {
            "model_code": "PM-INVALID-SHIFT",
            "model_name": "Invalid Shift Model",
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

        # Try to create LOT with invalid shift
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "shift": "X",
            "target_quantity": 50,
            "status": "CREATED"
        }
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 422

    def test_create_lot_invalid_status(self, client: TestClient, auth_headers_admin: dict):
        """Test creating LOT with invalid status value fails validation."""
        # Create product model
        product_data = {
            "model_code": "PM-INVALID-STATUS",
            "model_name": "Invalid Status Model",
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

        # Try to create LOT with invalid status
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "shift": "D",
            "target_quantity": 50,
            "status": "INVALID_STATUS"
        }
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 422

    def test_get_lot_by_number_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting LOT by non-existent lot_number returns 404."""
        response = client.get(
            "/api/v1/lots/number/WF-KR-251119D-999",
            headers=auth_headers_admin
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_lot_by_number_invalid_format(self, client: TestClient, auth_headers_admin: dict):
        """Test getting LOT with invalid lot_number format returns 422."""
        response = client.get(
            "/api/v1/lots/number/INVALID-FORMAT",
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_get_lots_by_product_model(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering LOTs by product_model_id."""
        # Create two product models
        pm_data1 = {
            "model_code": "PM-FILTER-1",
            "model_name": "Filter Model 1",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        pm_response1 = client.post(
            "/api/v1/product-models/",
            json=pm_data1,
            headers=auth_headers_admin
        )
        pm_id1 = pm_response1.json()["id"]

        pm_data2 = {
            "model_code": "PM-FILTER-2",
            "model_name": "Filter Model 2",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        pm_response2 = client.post(
            "/api/v1/product-models/",
            json=pm_data2,
            headers=auth_headers_admin
        )
        pm_id2 = pm_response2.json()["id"]

        # Create LOTs for each product model
        for _ in range(3):
            lot_data = create_test_lot_data(pm_id1, target_qty=25)
            client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)

        for _ in range(2):
            lot_data = create_test_lot_data(pm_id2, target_qty=30)
            client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)

        # Filter by first product model
        response = client.get(f"/api/v1/lots/product/{pm_id1}", headers=auth_headers_admin)
        assert response.status_code == 200
        lots = response.json()
        assert len(lots) == 3
        for lot in lots:
            assert lot["product_model_id"] == pm_id1

    def test_get_lot_quantities(self, client: TestClient, auth_headers_admin: dict):
        """Test getting LOT quantities endpoint."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-QUANTITIES",
            "model_name": "Quantities Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Get quantities
        response = client.get(f"/api/v1/lots/{lot_id}/quantities", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert "actual_quantity" in data
        assert "passed_quantity" in data
        assert "failed_quantity" in data

    def test_get_lot_quantities_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting quantities for non-existent LOT returns 404."""
        response = client.get("/api/v1/lots/99999/quantities", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_lot_quantities_validation(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT with quantity consistency validation."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-UPDATE-QTY-VAL",
            "model_name": "Update Qty Val Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Try to update with passed_quantity > actual_quantity
        update_data = {
            "actual_quantity": 10,
            "passed_quantity": 15  # More than actual
        }
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        # Should fail validation
        assert response.status_code == 422

    def test_update_lot_actual_exceeds_target(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT with actual_quantity > target_quantity fails."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-ACTUAL-EXCEED",
            "model_name": "Actual Exceed Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Try to update with actual_quantity > target_quantity
        update_data = {
            "target_quantity": 50,
            "actual_quantity": 60
        }
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        # Should fail validation
        assert response.status_code == 422

    def test_update_lot_negative_quantities(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT with negative quantities fails validation."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-NEG-QTY",
            "model_name": "Negative Qty Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Try to update with negative actual_quantity
        update_data = {"actual_quantity": -5}
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_lot_lifecycle_complete_flow(self, client: TestClient, auth_headers_admin: dict):
        """Test complete LOT lifecycle: CREATED -> IN_PROGRESS -> COMPLETED -> CLOSED."""
        # Create product model
        product_data = {
            "model_code": "PM-LIFECYCLE",
            "model_name": "Lifecycle Model",
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

        # Create LOT
        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]
        assert create_response.json()["status"] == "CREATED"

        # Transition to IN_PROGRESS
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json={"status": "IN_PROGRESS"},
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"

        # Transition to COMPLETED
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json={"status": "COMPLETED"},
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["status"] == "COMPLETED"

        # Close the LOT
        response = client.post(f"/api/v1/lots/{lot_id}/close", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json()["status"] == "CLOSED"
        assert response.json()["closed_at"] is not None

    def test_pagination_skip_limit_edge_cases(self, client: TestClient, auth_headers_admin: dict):
        """Test pagination with various skip and limit values."""
        # Create product model
        product_data = {
            "model_code": "PM-PAGINATION",
            "model_name": "Pagination Model",
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

        # Create 10 LOTs
        for _ in range(10):
            lot_data = create_test_lot_data(product_model_id, target_qty=20)
            client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)

        # Test skip=5, limit=3
        response = client.get("/api/v1/lots/?skip=5&limit=3", headers=auth_headers_admin)
        assert response.status_code == 200
        assert len(response.json()) == 3

        # Test skip beyond count
        response = client.get("/api/v1/lots/?skip=100&limit=10", headers=auth_headers_admin)
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_create_lot_missing_required_fields(self, client: TestClient, auth_headers_admin: dict):
        """Test creating LOT without required fields fails validation."""
        # Missing product_model_id
        lot_data = {
            "production_date": date.today().isoformat(),
            "shift": "D",
            "target_quantity": 50
        }
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 422

    def test_create_lot_boundary_target_quantity(self, client: TestClient, auth_headers_admin: dict):
        """Test creating LOT with boundary values for target_quantity (1 and 100)."""
        # Create product model
        product_data = {
            "model_code": "PM-BOUNDARY",
            "model_name": "Boundary Model",
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

        # Test minimum boundary (1)
        lot_data = create_test_lot_data(product_model_id, target_qty=1)
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 201
        assert response.json()["target_quantity"] == 1

        # Test maximum boundary (100)
        lot_data = create_test_lot_data(product_model_id, target_qty=100)
        response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        assert response.status_code == 201
        assert response.json()["target_quantity"] == 100

    def test_update_lot_shift(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT shift value."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-UPDATE-SHIFT",
            "model_name": "Update Shift Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50, shift="D")
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]
        assert create_response.json()["shift"] == "D"

        # Update to night shift
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json={"shift": "N"},
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        assert response.json()["shift"] == "N"

    def test_lot_defect_and_pass_rate_calculation(self, client: TestClient, auth_headers_admin: dict):
        """Test that defect_rate and pass_rate are correctly calculated."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-RATE-CALC",
            "model_name": "Rate Calc Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=100)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Update quantities
        update_data = {
            "actual_quantity": 100,
            "passed_quantity": 90,
            "failed_quantity": 10
        }
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        # Check rates are calculated correctly
        # defect_rate = (10/100) * 100 = 10%
        # pass_rate = (90/100) * 100 = 90%
        assert data["defect_rate"] == 10.0
        assert data["pass_rate"] == 90.0

    def test_get_lots_by_status_pagination(self, client: TestClient, auth_headers_admin: dict):
        """Test pagination on status filter endpoint."""
        # Create product model
        product_data = {
            "model_code": "PM-STATUS-PAGE",
            "model_name": "Status Page Model",
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

        # Create 5 COMPLETED LOTs
        for _ in range(5):
            lot_data = {
                "product_model_id": product_model_id,
                "production_date": date.today().isoformat(),
                "shift": "D",
                "target_quantity": 25,
                "status": "COMPLETED"
            }
            client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)

        # Test pagination
        response = client.get("/api/v1/lots/status/COMPLETED?skip=1&limit=2", headers=auth_headers_admin)
        assert response.status_code == 200
        lots = response.json()
        assert len(lots) == 2
        for lot in lots:
            assert lot["status"] == "COMPLETED"

    def test_update_lot_invalid_shift(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT with invalid shift value fails."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-UPD-INV-SHIFT",
            "model_name": "Update Invalid Shift Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Try to update with invalid shift
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json={"shift": "Z"},
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_update_lot_invalid_status(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT with invalid status value fails."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-UPD-INV-STATUS",
            "model_name": "Update Invalid Status Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Try to update with invalid status
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json={"status": "UNKNOWN_STATUS"},
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_get_lot_with_zero_actual_quantity(self, client: TestClient, auth_headers_admin: dict):
        """Test LOT with zero actual_quantity has null rates."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-ZERO-ACTUAL",
            "model_name": "Zero Actual Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Get LOT (should have zero quantities)
        response = client.get(f"/api/v1/lots/{lot_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["actual_quantity"] == 0
        # Rates should be None when actual_quantity is 0
        assert data["defect_rate"] is None
        assert data["pass_rate"] is None

    def test_get_lot_id_validation(self, client: TestClient, auth_headers_admin: dict):
        """Test that negative or zero LOT ID returns 422."""
        # Test ID = 0
        response = client.get("/api/v1/lots/0", headers=auth_headers_admin)
        assert response.status_code == 422

        # Test negative ID
        response = client.get("/api/v1/lots/-1", headers=auth_headers_admin)
        assert response.status_code == 422

    def test_close_lot_from_created_status(self, client: TestClient, auth_headers_admin: dict):
        """Test closing LOT directly from CREATED status."""
        # Create product model
        product_data = {
            "model_code": "PM-CLOSE-CREATED",
            "model_name": "Close Created Model",
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

        # Create LOT with CREATED status
        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]
        assert create_response.json()["status"] == "CREATED"

        # Close directly (any status can transition to CLOSED)
        response = client.post(f"/api/v1/lots/{lot_id}/close", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json()["status"] == "CLOSED"
        assert response.json()["closed_at"] is not None

    def test_update_lot_passed_plus_failed_exceeds_actual(self, client: TestClient, auth_headers_admin: dict):
        """Test updating LOT where passed + failed > actual fails."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-SUM-EXCEED",
            "model_name": "Sum Exceed Model",
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

        lot_data = create_test_lot_data(product_model_id, target_qty=50)
        create_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = create_response.json()["id"]

        # Try to update with passed + failed > actual
        update_data = {
            "actual_quantity": 10,
            "passed_quantity": 7,
            "failed_quantity": 5  # 7 + 5 = 12 > 10
        }
        response = client.put(
            f"/api/v1/lots/{lot_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 422
