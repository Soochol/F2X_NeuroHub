"""Integration tests for Process Data API endpoints.

Tests process execution data recording and analysis
for /api/v1/process-data/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestProcessDataAPI:
    """Test suite for Process Data API endpoints."""

    def test_list_process_data_empty(self, client: TestClient, auth_headers_admin: dict):
        """Test listing process data when database is empty."""
        response = client.get("/api/v1/process-data/", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_process_data(self, client: TestClient, auth_headers_admin: dict):
        """Test recording process execution data."""
        # Create required entities: product model, process, LOT, serial
        product_data = {
            "model_code": "PM-PD-001",
            "model_name": "Process Data Model",
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

        process_data = {
            "process_name": "LASER_MARKING",
            "process_order": 1,
            "description": "Laser marking process",
            "standard_duration_seconds": 30,
            "validation_rules": {}
        }
        proc_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = proc_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-PD-001",
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
            "serial_number": "SN-PD-001",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        # Create process data record
        pd_data = {
            "serial_id": serial_id,
            "process_id": process_id,
            "result": "PASS",
            "measurement_data": {"power": 50, "speed": 100},
            "duration_seconds": 28
        }
        response = client.post(
            "/api/v1/process-data/",
            json=pd_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == "PASS"
        assert "id" in data

    @pytest.mark.parametrize("result", ["PASS", "FAIL", "REWORK"])
    def test_process_data_result_values(
        self, client: TestClient, auth_headers_admin: dict, result: str
    ):
        """Test process data with different result values."""
        # Create product model
        product_data = {
            "model_code": f"PM-RESULT-{result}",
            "model_name": f"Result {result} Model",
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

        # Create process
        process_data = {
            "process_name": "SENSOR_INSPECTION",
            "process_order": 3,
            "description": "Sensor inspection",
            "standard_duration_seconds": 45,
            "validation_rules": {}
        }
        proc_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = proc_response.json()["id"]

        # Create LOT
        lot_data = {
            "lot_number": f"LOT-RESULT-{result}",
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

        # Create serial
        serial_data = {
            "serial_number": f"SN-RESULT-{result}",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        # Create process data with result
        pd_data = {
            "serial_id": serial_id,
            "process_id": process_id,
            "result": result,
            "measurement_data": {"test": True},
            "duration_seconds": 40
        }
        response = client.post(
            "/api/v1/process-data/",
            json=pd_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        assert response.json()["result"] == result

    def test_get_process_data_by_id(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving process data by ID."""
        # Create all required entities (simplified)
        product_data = {
            "model_code": "PM-GET-PD",
            "model_name": "Get PD Model",
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

        process_data = {
            "process_name": "LMA_ASSEMBLY",
            "process_order": 2,
            "description": "LMA assembly",
            "standard_duration_seconds": 120,
            "validation_rules": {}
        }
        proc_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = proc_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-GET-PD",
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
            "serial_number": "SN-GET-PD",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        pd_data = {
            "serial_id": serial_id,
            "process_id": process_id,
            "result": "PASS",
            "measurement_data": {"voltage": 3.3},
            "duration_seconds": 115
        }
        create_response = client.post(
            "/api/v1/process-data/",
            json=pd_data,
            headers=auth_headers_admin
        )
        pd_id = create_response.json()["id"]

        # Get process data by ID
        response = client.get(f"/api/v1/process-data/{pd_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pd_id

    def test_update_process_data(self, client: TestClient, auth_headers_admin: dict):
        """Test updating process data."""
        # Create entities and process data (simplified creation)
        product_data = {
            "model_code": "PM-UPDATE-PD",
            "model_name": "Update PD Model",
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

        process_data = {
            "process_name": "FIRMWARE_UPLOAD",
            "process_order": 4,
            "description": "Firmware upload",
            "standard_duration_seconds": 90,
            "validation_rules": {}
        }
        proc_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = proc_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-UPDATE-PD",
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
            "serial_number": "SN-UPDATE-PD",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        pd_data = {
            "serial_id": serial_id,
            "process_id": process_id,
            "result": "PASS",
            "measurement_data": {"version": "1.0"},
            "duration_seconds": 85
        }
        create_response = client.post(
            "/api/v1/process-data/",
            json=pd_data,
            headers=auth_headers_admin
        )
        pd_id = create_response.json()["id"]

        # Update process data
        update_data = {"notes": "Firmware uploaded successfully"}
        response = client.put(
            f"/api/v1/process-data/{pd_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200

    def test_delete_process_data(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting process data."""
        # Create entities and process data
        product_data = {
            "model_code": "PM-DEL-PD",
            "model_name": "Delete PD Model",
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

        process_data = {
            "process_name": "ROBOT_ASSEMBLY",
            "process_order": 5,
            "description": "Robot assembly",
            "standard_duration_seconds": 180,
            "validation_rules": {}
        }
        proc_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = proc_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-DEL-PD",
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
            "serial_number": "SN-DEL-PD",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        pd_data = {
            "serial_id": serial_id,
            "process_id": process_id,
            "result": "PASS",
            "measurement_data": {},
            "duration_seconds": 175
        }
        create_response = client.post(
            "/api/v1/process-data/",
            json=pd_data,
            headers=auth_headers_admin
        )
        pd_id = create_response.json()["id"]

        # Delete process data
        response = client.delete(
            f"/api/v1/process-data/{pd_id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/v1/process-data/{pd_id}",
            headers=auth_headers_admin
        )
        assert get_response.status_code == 404

    def test_process_data_requires_authentication(self, client: TestClient):
        """Test that process data endpoints require authentication."""
        response = client.get("/api/v1/process-data/")
        assert response.status_code == 401

    def test_process_data_measurement_jsonb(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test JSONB measurement_data field can store complex data."""
        # Create entities
        product_data = {
            "model_code": "PM-JSONB",
            "model_name": "JSONB Model",
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

        process_data = {
            "process_name": "PERFORMANCE_TEST",
            "process_order": 6,
            "description": "Performance test",
            "standard_duration_seconds": 300,
            "validation_rules": {}
        }
        proc_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = proc_response.json()["id"]

        lot_data = {
            "lot_number": "LOT-JSONB",
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
            "serial_number": "SN-JSONB",
            "lot_id": lot_id,
            "status": "IN_PROGRESS"
        }
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        # Complex measurement data
        complex_measurement = {
            "temperature": {"min": 20, "max": 25, "avg": 22.5},
            "humidity": 45,
            "test_results": [
                {"test_id": 1, "value": 100, "passed": True},
                {"test_id": 2, "value": 95, "passed": True}
            ]
        }

        pd_data = {
            "serial_id": serial_id,
            "process_id": process_id,
            "result": "PASS",
            "measurement_data": complex_measurement,
            "duration_seconds": 295
        }
        response = client.post(
            "/api/v1/process-data/",
            json=pd_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert "measurement_data" in data
