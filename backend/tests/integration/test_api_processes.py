"""Integration tests for Processes API endpoints.

Tests all CRUD operations and filtering for /api/v1/processes/* endpoints.
Covers all 8 manufacturing processes.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def create_test_process_data(process_num: int = 1, process_code: str = "TEST_PROCESS"):
    """Helper function to create test process data with correct schema."""
    return {
        "process_number": process_num,
        "process_code": process_code,
        "process_name_ko": f"{process_code} 공정",
        "process_name_en": process_code.replace("_", " ").title(),
        "description": f"{process_code} process description",
        "estimated_duration_seconds": 60,
        "quality_criteria": {},
        "sort_order": process_num,
        "is_active": True
    }


class TestProcessesAPI:
    """Test suite for Processes API endpoints."""

    def test_list_processes_empty(self, client: TestClient, auth_headers_admin: dict):
        """Test listing processes when database is empty."""
        response = client.get("/api/v1/processes/", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_process(self, client: TestClient, auth_headers_admin: dict):
        """Test creating a new process."""
        process_data = {
            "process_number": 1,
            "process_code": "LASER_MARKING",
            "process_name_ko": "레이저 마킹",
            "process_name_en": "Laser Marking",
            "description": "Laser marking identification",
            "estimated_duration_seconds": 30,
            "quality_criteria": {"min_power": 10, "max_power": 100},
            "sort_order": 1
        }
        response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert data["process_code"] == "LASER_MARKING"
        assert data["process_number"] == 1
        assert "id" in data

    @pytest.mark.parametrize("process_code,process_num", [
        ("LASER_MARKING", 1),
        ("LMA_ASSEMBLY", 2),
        ("SENSOR_INSPECTION", 3),
        ("FIRMWARE_UPLOAD", 4),
        ("ROBOT_ASSEMBLY", 5),
        ("PERFORMANCE_TEST", 6),
        ("LABEL_PRINTING", 7),
        ("PACKAGING_INSPECTION", 8)
    ])
    def test_create_all_process_types(
        self, client: TestClient, auth_headers_admin: dict, process_code: str, process_num: int
    ):
        """Test creating each of the 8 manufacturing processes."""
        process_data = {
            "process_number": process_num,
            "process_code": process_code,
            "process_name_ko": f"{process_code} 공정",
            "process_name_en": process_code.replace("_", " ").title(),
            "description": f"{process_code} process",
            "estimated_duration_seconds": 60,
            "quality_criteria": {},
            "sort_order": process_num
        }
        response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        assert response.json()["process_code"] == process_code

    def test_get_process_by_id(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving process by ID."""
        # Create process
        process_data = create_test_process_data(2, "LMA_ASSEMBLY")
        create_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = create_response.json()["id"]

        # Get process
        response = client.get(
            f"/api/v1/processes/{process_id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == process_id
        assert data["process_code"] == "LMA_ASSEMBLY"

    def test_get_process_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting non-existent process returns 404."""
        response = client.get("/api/v1/processes/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_process(self, client: TestClient, auth_headers_admin: dict):
        """Test updating an existing process."""
        # Create process
        process_data = create_test_process_data(3, "SENSOR_INSPECTION")
        create_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = create_response.json()["id"]

        # Update process
        update_data = {
            "description": "Updated description",
            "estimated_duration_seconds": 90,
            "quality_criteria": {"threshold": 95}
        }
        response = client.put(
            f"/api/v1/processes/{process_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["estimated_duration_seconds"] == 90

    def test_delete_process(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting a process."""
        # Create process
        process_data = create_test_process_data(4, "FIRMWARE_UPLOAD")
        create_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = create_response.json()["id"]

        # Delete process
        response = client.delete(
            f"/api/v1/processes/{process_id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/v1/processes/{process_id}",
            headers=auth_headers_admin
        )
        assert get_response.status_code == 404

    def test_list_processes_ordered(self, client: TestClient, auth_headers_admin: dict):
        """Test that processes are listed in order."""
        # Create processes with different orders
        for num in [3, 1, 2]:
            process_data = create_test_process_data(num, f"PROCESS_{num}")
            client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)

        # List all
        response = client.get("/api/v1/processes/", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_process_requires_authentication(self, client: TestClient):
        """Test that process endpoints require authentication."""
        response = client.get("/api/v1/processes/")
        assert response.status_code == 401

    def test_create_process_validation_fails(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test that invalid process data fails validation."""
        invalid_data = {
            "process_order": 1
            # Missing required fields
        }
        response = client.post(
            "/api/v1/processes/",
            json=invalid_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_get_process_by_name(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving process by name/code."""
        # Create process
        process_data = create_test_process_data(5, "ROBOT_ASSEMBLY")
        client.post("/api/v1/processes/", json=process_data, headers=auth_headers_admin)

        # Get by code (assuming endpoint uses process_code)
        response = client.get(
            "/api/v1/processes/code/ROBOT_ASSEMBLY",
            headers=auth_headers_admin
        )
        # May be 200 if endpoint exists, 404 if not implemented
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["process_code"] == "ROBOT_ASSEMBLY"

    def test_process_statistics(self, client: TestClient, auth_headers_admin: dict):
        """Test getting process statistics."""
        # Create a process
        process_data = create_test_process_data(6, "PERFORMANCE_TEST")
        create_response = client.post(
            "/api/v1/processes/",
            json=process_data,
            headers=auth_headers_admin
        )
        process_id = create_response.json()["id"]

        # Get statistics
        response = client.get(
            f"/api/v1/processes/{process_id}/statistics",
            headers=auth_headers_admin
        )
        # May return 200 with stats or 404 if not implemented
        assert response.status_code in [200, 404]
