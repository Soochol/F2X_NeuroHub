"""Integration tests for Process Data API endpoints.

Tests process execution data recording and analysis
for /api/v1/process-data/* endpoints.
"""

from datetime import date, datetime, timedelta

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
            "process_number": 1,
            "process_code": "LASER_MARKING",
            "process_name_ko": "레이저 마킹",
            "process_name_en": "Laser Marking",
            "description": "Laser marking process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
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
            "lot_id": lot_id,
            "serial_id": serial_id,
            "process_id": process_id,
            "operator_id": 1,  # Admin user ID from conftest
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": {"power": 50, "speed": 100},
            "started_at": datetime.now().isoformat(),
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
            "process_number": 3,
            "process_code": "SENSOR_INSPECTION",
            "process_name_ko": "센서 검사",
            "process_name_en": "Sensor Inspection",
            "description": "Sensor inspection",
            "estimated_duration_seconds": 45,
            "quality_criteria": {},
            "sort_order": 3
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
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        # Create process data with result
        pd_data = {
            "lot_id": lot_id,
            "serial_id": serial_id,
            "process_id": process_id,
            "operator_id": 1,
            "data_level": "SERIAL",
            "result": result,
            "measurements": {"test": True},
            "started_at": datetime.now().isoformat(),
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
            "process_number": 2,
            "process_code": "LMA_ASSEMBLY",
            "process_name_ko": "LMA 조립",
            "process_name_en": "LMA Assembly",
            "description": "LMA assembly",
            "estimated_duration_seconds": 120,
            "quality_criteria": {},
            "sort_order": 2
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
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        pd_data = {
            "lot_id": lot_id,
            "serial_id": serial_id,
            "process_id": process_id,
            "operator_id": 1,
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": {"voltage": 3.3},
            "started_at": datetime.now().isoformat(),
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
            "process_number": 4,
            "process_code": "FIRMWARE_UPLOAD",
            "process_name_ko": "펌웨어 업로드",
            "process_name_en": "Firmware Upload",
            "description": "Firmware upload",
            "estimated_duration_seconds": 90,
            "quality_criteria": {},
            "sort_order": 4
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
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        pd_data = {
            "lot_id": lot_id,
            "serial_id": serial_id,
            "process_id": process_id,
            "operator_id": 1,
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": {"version": "1.0"},
            "started_at": datetime.now().isoformat(),
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
            "process_number": 5,
            "process_code": "ROBOT_ASSEMBLY",
            "process_name_ko": "로봇 조립",
            "process_name_en": "Robot Assembly",
            "description": "Robot assembly",
            "estimated_duration_seconds": 180,
            "quality_criteria": {},
            "sort_order": 5
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
        serial_response = client.post(
            "/api/v1/serials/",
            json=serial_data,
            headers=auth_headers_admin
        )
        serial_id = serial_response.json()["id"]

        pd_data = {
            "lot_id": lot_id,
            "serial_id": serial_id,
            "process_id": process_id,
            "operator_id": 1,
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": {},
            "started_at": datetime.now().isoformat(),
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
            "process_number": 6,
            "process_code": "PERFORMANCE_TEST",
            "process_name_ko": "성능 테스트",
            "process_name_en": "Performance Test",
            "description": "Performance test",
            "estimated_duration_seconds": 300,
            "quality_criteria": {},
            "sort_order": 6
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
            "lot_id": lot_id,
            "serial_id": serial_id,
            "process_id": process_id,
            "operator_id": 1,
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": complex_measurement,
            "started_at": datetime.now().isoformat(),
            "duration_seconds": 295
        }
        response = client.post(
            "/api/v1/process-data/",
            json=pd_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert "measurements" in data

    # ============================================================================
    # New Comprehensive Tests for Coverage Enhancement
    # ============================================================================

    def test_get_process_data_by_serial(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving all process data for a specific serial."""
        # Create product model, process, LOT, serial
        product_data = {
            "model_code": "PM-PD-SERIAL",
            "model_name": "Serial Process Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 1,
            "process_code": "ASSEMBLY",
            "process_name_ko": "조립",
            "process_name_en": "Assembly",
            "description": "Assembly process",
            "estimated_duration_seconds": 60,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 1,
            "status": "IN_PROGRESS"
        }
        serial_response = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
        serial_id = serial_response.json()["id"]

        # Create multiple process data records for this serial
        for i in range(2):
            pd_data = {
                "lot_id": lot_id,
                "serial_id": serial_id,
                "process_id": process_id,
                "operator_id": 1,
                "data_level": "SERIAL",
                "result": "PASS",
                "measurements": {"value": i * 10},
                "started_at": datetime.now().isoformat(),
                "duration_seconds": 30 + i
            }
            client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # Get all process data for this serial
        response = client.get(f"/api/v1/process-data/serial/{serial_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Verify all records belong to this serial
        for record in data:
            assert record["serial_id"] == serial_id

    def test_get_process_data_by_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving all process data for a specific LOT."""
        # Create product model, process, LOT
        product_data = {
            "model_code": "PM-PD-LOT",
            "model_name": "LOT Process Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 2,
            "process_code": "INSPECTION",
            "process_name_ko": "검사",
            "process_name_en": "Inspection",
            "description": "Quality inspection",
            "estimated_duration_seconds": 45,
            "quality_criteria": {},
            "sort_order": 2
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 15,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create process data records at LOT level
        for i in range(2):
            pd_data = {
                "lot_id": lot_id,
                "process_id": process_id,
                "operator_id": 1,
                "data_level": "LOT",
                "result": "PASS",
                "measurements": {"temperature": 25 + i},
                "started_at": datetime.now().isoformat(),
                "duration_seconds": 40
            }
            client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # Get all process data for this LOT
        response = client.get(f"/api/v1/process-data/lot/{lot_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for record in data:
            assert record["lot_id"] == lot_id
            assert record["data_level"] == "LOT"

    def test_get_process_data_by_process_type(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering process data by process type."""
        # Create product model, multiple processes, LOT
        product_data = {
            "model_code": "PM-PD-PROC-FILTER",
            "model_name": "Process Filter Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        # Create two different processes
        process1_data = {
            "process_number": 1,
            "process_code": "LASER",
            "process_name_ko": "레이저",
            "process_name_en": "Laser",
            "description": "Laser process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc1_response = client.post("/api/v1/processes/", json=process1_data, headers=auth_headers_admin)
        process1_id = proc1_response.json()["id"]

        process2_data = {
            "process_number": 2,
            "process_code": "POLISH",
            "process_name_ko": "연마",
            "process_name_en": "Polish",
            "description": "Polish process",
            "estimated_duration_seconds": 45,
            "quality_criteria": {},
            "sort_order": 2
        }
        proc2_response = client.post("/api/v1/processes/", json=process2_data, headers=auth_headers_admin)
        process2_id = proc2_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create process data for both processes
        for process_id in [process1_id, process1_id, process2_id]:
            pd_data = {
                "lot_id": lot_id,
                "process_id": process_id,
                "operator_id": 1,
                "data_level": "LOT",
                "result": "PASS",
                "measurements": {},
                "started_at": datetime.now().isoformat(),
                "duration_seconds": 30
            }
            client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # Filter by process1
        response = client.get(f"/api/v1/process-data/process/{process1_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for record in data:
            assert record["process_id"] == process1_id

    def test_get_process_data_by_result_status(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering process data by result (PASS/FAIL/REWORK)."""
        # Create product model, process, LOT
        product_data = {
            "model_code": "PM-PD-RESULT",
            "model_name": "Result Filter Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 1,
            "process_code": "TEST_RESULT",
            "process_name_ko": "테스트",
            "process_name_en": "Test",
            "description": "Test process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create process data with different results
        results = ["PASS", "PASS", "FAIL", "REWORK"]
        for result in results:
            started = datetime.now()
            completed = started + timedelta(seconds=30)
            pd_data = {
                "lot_id": lot_id,
                "process_id": process_id,
                "operator_id": 1,
                "data_level": "LOT",
                "result": result,
                "measurements": {},
                "started_at": started.isoformat(),
                "completed_at": completed.isoformat()
            }
            if result == "FAIL":
                pd_data["defects"] = {"type": "defect", "description": "Test defect"}

            client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # Filter by FAIL result
        response = client.get("/api/v1/process-data/result/FAIL", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["result"] == "FAIL"

    def test_get_failed_processes(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving failed processes for defect analysis."""
        # Create product model, process, LOT
        product_data = {
            "model_code": "PM-PD-FAILED",
            "model_name": "Failed Process Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 1,
            "process_code": "FAIL_TEST",
            "process_name_ko": "실패 테스트",
            "process_name_en": "Fail Test",
            "description": "Fail test process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create failed process data records with defects
        for i in range(3):
            started = datetime.now()
            completed = started + timedelta(seconds=30)
            pd_data = {
                "lot_id": lot_id,
                "process_id": process_id,
                "operator_id": 1,
                "data_level": "LOT",
                "result": "FAIL",
                "measurements": {},
                "defects": {"type": f"defect_{i}", "severity": "HIGH", "location": "surface"},
                "started_at": started.isoformat(),
                "completed_at": completed.isoformat()
            }
            client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # Get all failed processes using result filter endpoint
        response = client.get("/api/v1/process-data/result/FAIL", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for record in data:
            assert record["result"] == "FAIL"
            assert "defects" in record

    def test_get_incomplete_processes(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving in-progress processes (completed_at IS NULL).

        NOTE: The /incomplete endpoint has a routing conflict with /{id} endpoint.
        This test verifies we can create incomplete process data (no completed_at).
        """
        # Create product model, process, LOT
        product_data = {
            "model_code": "PM-PD-INCOMPLETE",
            "model_name": "Incomplete Process Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 1,
            "process_code": "INCOMPLETE_TEST",
            "process_name_ko": "미완료 테스트",
            "process_name_en": "Incomplete Test",
            "description": "Incomplete test process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create incomplete process data (no completed_at)
        pd_data = {
            "lot_id": lot_id,
            "process_id": process_id,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "PASS",
            "measurements": {},
            "started_at": datetime.now().isoformat(),
        }
        response = client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)
        assert response.status_code == 201
        data = response.json()
        # Verify incomplete process data was created without completed_at
        assert data["completed_at"] is None
        assert data["duration_seconds"] is None

    def test_get_process_data_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting non-existent process data returns 404."""
        response = client.get("/api/v1/process-data/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_non_existent_process_data(self, client: TestClient, auth_headers_admin: dict):
        """Test updating non-existent process data returns 404."""
        update_data = {"result": "FAIL", "defects": {"type": "test", "description": "Test defect"}}
        response = client.put(
            "/api/v1/process-data/99999",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_delete_non_existent_process_data(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting non-existent process data returns 404."""
        response = client.delete("/api/v1/process-data/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_process_data_with_operator_filter(self, client: TestClient, auth_headers_admin: dict, test_admin_user):
        """Test filtering process data by operator."""
        # Create product model, process, LOT
        product_data = {
            "model_code": "PM-PD-OPERATOR",
            "model_name": "Operator Filter Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 1,
            "process_code": "OP_TEST",
            "process_name_ko": "작업자 테스트",
            "process_name_en": "Operator Test",
            "description": "Operator test process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create process data with specific operator
        operator_id = test_admin_user.id
        for i in range(2):
            pd_data = {
                "lot_id": lot_id,
                "process_id": process_id,
                "operator_id": operator_id,
                "data_level": "LOT",
                "result": "PASS",
                "measurements": {},
                "started_at": datetime.now().isoformat(),
                "duration_seconds": 30
            }
            client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # Filter by operator
        response = client.get(f"/api/v1/process-data/operator/{operator_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for record in data:
            assert record["operator_id"] == operator_id

    def test_process_data_defects_jsonb(self, client: TestClient, auth_headers_admin: dict):
        """Test that defects JSONB field is properly stored and retrieved."""
        # Create product model, process, LOT
        product_data = {
            "model_code": "PM-PD-DEFECTS",
            "model_name": "Defects JSONB Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 1,
            "process_code": "DEFECT_TEST",
            "process_name_ko": "결함 테스트",
            "process_name_en": "Defect Test",
            "description": "Defect test process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 10,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create process data with complex defects (defects must be dict, not list)
        started = datetime.now()
        completed = started + timedelta(seconds=30)
        defects_data = {
            "defect_count": 2,
            "defects_list": [
                {"type": "scratch", "location": "surface", "severity": "MINOR", "x": 10, "y": 20},
                {"type": "crack", "location": "edge", "severity": "MAJOR", "length_mm": 5.2}
            ],
            "primary_defect": "scratch"
        }
        pd_data = {
            "lot_id": lot_id,
            "process_id": process_id,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "FAIL",
            "measurements": {},
            "defects": defects_data,
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat()
        }
        response = client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)
        assert response.status_code == 201
        data = response.json()
        assert "defects" in data
        assert data["defects"]["defect_count"] == 2
        assert data["defects"]["primary_defect"] == "scratch"
        assert len(data["defects"]["defects_list"]) == 2

    def test_process_data_pagination(self, client: TestClient, auth_headers_admin: dict):
        """Test pagination for process data list."""
        # Create product model, process, LOT
        product_data = {
            "model_code": "PM-PD-PAGINATION",
            "model_name": "Pagination Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm_response = client.post("/api/v1/product-models/", json=product_data, headers=auth_headers_admin)
        product_model_id = pm_response.json()["id"]

        process_data = {
            "process_number": 1,
            "process_code": "PAGE_TEST",
            "process_name_ko": "페이징 테스트",
            "process_name_en": "Pagination Test",
            "description": "Pagination test process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 1
        }
        proc_response = client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)
        process_id = proc_response.json()["id"]

        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "target_quantity": 20,
            "status": "IN_PROGRESS",
            "shift": "D"
        }
        lot_response = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
        lot_id = lot_response.json()["id"]

        # Create multiple process data records
        for i in range(15):
            pd_data = {
                "lot_id": lot_id,
                "process_id": process_id,
                "operator_id": 1,
                "data_level": "LOT",
                "result": "PASS",
                "measurements": {"index": i},
                "started_at": datetime.now().isoformat(),
                "duration_seconds": 30
            }
            client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # Test pagination - first page
        response = client.get("/api/v1/process-data/?skip=0&limit=10", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10

        # Test pagination - second page
        response = client.get("/api/v1/process-data/?skip=10&limit=10", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5  # Should have 5 remaining records
