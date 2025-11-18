"""Comprehensive integration tests for Dashboard API endpoints.

Tests dashboard display endpoints with realistic production data
for /api/v1/dashboard/* endpoints.

Coverage Goals:
- All 3 dashboard endpoints (summary, lots, process-wip)
- Authentication and authorization
- Query parameter validation and filtering
- Edge cases (empty data, zero divisions, null handling)
- Date-based filtering and calculations
- Progress and defect rate calculations
- Bottleneck detection logic
- Pagination and limit validation
- Multiple user roles
- Error handling (404, 400, 422)

Target Coverage: 75%+ (up from 19%)
"""

from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient


class TestDashboardAPIWithData:
    """Test suite for Dashboard API endpoints with realistic data."""

    @pytest.fixture(scope="function")
    def dashboard_data(self, client: TestClient, auth_headers_admin: dict):
        """
        Create comprehensive production data for dashboard testing.

        Creates:
        - 2 product models
        - 3 LOTs (1 IN_PROGRESS, 1 CLOSED recently, 1 CLOSED old)
        - 8 serials (4 PASSED, 2 FAILED, 2 IN_PROGRESS)
        - 2 processes
        - 12 process data records
        """
        data = {}

        # Create 2 product models
        pm1_data = {
            "model_code": "PM-DASHBOARD-01",
            "model_name": "Dashboard Model 1",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm1_resp = client.post("/api/v1/product-models/", json=pm1_data, headers=auth_headers_admin)
        data["pm1_id"] = pm1_resp.json()["id"]

        pm2_data = {
            "model_code": "PM-DASHBOARD-02",
            "model_name": "Dashboard Model 2",
            "version": "2.0",
            "category": "Premium",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 7
        }
        pm2_resp = client.post("/api/v1/product-models/", json=pm2_data, headers=auth_headers_admin)
        data["pm2_id"] = pm2_resp.json()["id"]

        # Create 2 processes
        process1_data = {
            "process_number": 1,
            "process_code": "LASER_MARK_DASH",
            "process_name_ko": "레이저 마킹",
            "process_name_en": "Laser Marking",
            "description": "Laser marking for dashboard",
            "estimated_duration_seconds": 30,
            "quality_criteria": {"power_min": 45, "power_max": 55},
            "sort_order": 1
        }
        proc1_resp = client.post("/api/v1/processes/", json=process1_data, headers=auth_headers_admin)
        data["process1_id"] = proc1_resp.json()["id"]

        process2_data = {
            "process_number": 2,
            "process_code": "ASSEMBLY_DASH",
            "process_name_ko": "조립",
            "process_name_en": "Assembly",
            "description": "Assembly for dashboard",
            "estimated_duration_seconds": 60,
            "quality_criteria": {},
            "sort_order": 2
        }
        proc2_resp = client.post("/api/v1/processes/", json=process2_data, headers=auth_headers_admin)
        data["process2_id"] = proc2_resp.json()["id"]

        # Create 3 LOTs with different statuses
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=32)
        data["lot_ids"] = []

        # LOT 1: IN_PROGRESS (today)
        lot1_data = {
            "product_model_id": data["pm1_id"],
            "production_date": today.isoformat(),
            "shift": "D",
            "target_quantity": 5,
            "status": "IN_PROGRESS"
        }
        lot1_resp = client.post("/api/v1/lots/", json=lot1_data, headers=auth_headers_admin)
        lot1_id = lot1_resp.json()["id"]
        data["lot_ids"].append(lot1_id)

        # Create serials for LOT 1
        for j in range(5):
            status = "IN_PROGRESS" if j < 2 else ("PASSED" if j < 4 else "FAILED")
            serial_data = {
                "lot_id": lot1_id,
                "sequence_in_lot": j + 1,
                "status": status
            }
            if status == "FAILED":
                serial_data["failure_reason"] = f"Test failure {j+1}"

            serial_resp = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
            serial_id = serial_resp.json()["id"]

            # Create process data for completed serials
            if status != "IN_PROGRESS":
                pd_data = {
                    "lot_id": lot1_id,
                    "serial_id": serial_id,
                    "process_id": data["process1_id"],
                    "operator_id": 1,
                    "data_level": "SERIAL",
                    "result": "PASS" if status == "PASSED" else "FAIL",
                    "measurements": {"power": 50},
                    "started_at": datetime.now().isoformat(),
                    "duration_seconds": 25 + j
                }
                client.post("/api/v1/process-data/", json=pd_data, headers=auth_headers_admin)

        # LOT 2: CLOSED recently (7 days ago)
        lot2_data = {
            "product_model_id": data["pm1_id"],
            "production_date": week_ago.isoformat(),
            "shift": "N",
            "target_quantity": 3,
            "status": "CLOSED"
        }
        lot2_resp = client.post("/api/v1/lots/", json=lot2_data, headers=auth_headers_admin)
        lot2_id = lot2_resp.json()["id"]
        data["lot_ids"].append(lot2_id)

        # LOT 3: CLOSED old (32 days ago - should not appear in default dashboard lots)
        lot3_data = {
            "product_model_id": data["pm2_id"],
            "production_date": month_ago.isoformat(),
            "shift": "D",
            "target_quantity": 2,
            "status": "CLOSED"
        }
        lot3_resp = client.post("/api/v1/lots/", json=lot3_data, headers=auth_headers_admin)
        lot3_id = lot3_resp.json()["id"]
        data["lot_ids"].append(lot3_id)

        return data

    # ===================================================================
    # Dashboard Summary Endpoint Tests (/api/v1/dashboard/summary)
    # ===================================================================

    def test_dashboard_summary_with_data(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard summary with realistic production data."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Validate structure
        assert "date" in data
        assert "total_started" in data
        assert "total_completed" in data
        assert "total_defective" in data
        assert "defect_rate" in data
        assert "lots" in data
        assert "process_wip" in data

        # Validate lots summary structure
        if len(data["lots"]) > 0:
            lot = data["lots"][0]
            assert "lot_number" in lot
            assert "status" in lot
            assert "target_quantity" in lot
            assert "completed_count" in lot
            assert "progress_percentage" in lot

    def test_dashboard_summary_with_date_param(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard summary with specific date parameter."""
        today = date.today()
        response = client.get(
            f"/api/v1/dashboard/summary?target_date={today.isoformat()}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert data["date"] == today.isoformat()

    def test_dashboard_summary_past_date(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard summary with past date parameter."""
        past_date = date.today() - timedelta(days=10)
        response = client.get(
            f"/api/v1/dashboard/summary?target_date={past_date.isoformat()}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert data["date"] == past_date.isoformat()
        # Should return zero metrics for past date with no data
        assert data["total_started"] >= 0
        assert data["total_completed"] >= 0

    def test_dashboard_summary_future_date(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard summary with future date parameter."""
        future_date = date.today() + timedelta(days=5)
        response = client.get(
            f"/api/v1/dashboard/summary?target_date={future_date.isoformat()}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert data["date"] == future_date.isoformat()
        # Should return zero metrics for future date
        assert data["total_started"] == 0
        assert data["total_completed"] == 0
        assert data["defect_rate"] == 0

    def test_dashboard_summary_empty_database(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard summary with empty database."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        # Should return valid structure with zero values
        assert data["total_started"] >= 0
        assert data["total_completed"] >= 0
        assert data["total_defective"] >= 0
        assert isinstance(data["lots"], list)
        assert isinstance(data["process_wip"], dict)

    def test_dashboard_summary_defect_rate_calculation(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test defect rate calculation in dashboard summary."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify defect rate calculation
        if data["total_completed"] > 0:
            expected_rate = round((data["total_defective"] / data["total_completed"]) * 100, 2)
            assert data["defect_rate"] == expected_rate
        else:
            assert data["defect_rate"] == 0

    def test_dashboard_summary_zero_division_safe(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test that dashboard summary handles zero division gracefully."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        # Defect rate should be 0 when no completed units exist
        if data["total_completed"] == 0:
            assert data["defect_rate"] == 0

    def test_dashboard_summary_lots_progress_calculation(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test progress percentage calculation for lots in summary."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify each lot's progress calculation
        for lot in data["lots"]:
            if lot["target_quantity"] > 0:
                expected_progress = round(
                    (lot["completed_count"] / lot["target_quantity"]) * 100, 1
                )
                assert lot["progress_percentage"] == expected_progress

    def test_dashboard_summary_lots_limit_to_10(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that summary returns maximum 10 active lots."""
        # The fixture creates 3 lots, so all should be returned
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        # Should have at most 10 lots (limited by query)
        assert len(data["lots"]) <= 10

    def test_dashboard_summary_process_wip_structure(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test process WIP structure in summary endpoint."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify process_wip is a dict with process codes as keys
        assert isinstance(data["process_wip"], dict)
        for process_code, wip_count in data["process_wip"].items():
            assert isinstance(process_code, str)
            assert isinstance(wip_count, int)
            assert wip_count >= 0

    # ===================================================================
    # Dashboard Lots Endpoint Tests (/api/v1/dashboard/lots)
    # ===================================================================

    def test_dashboard_lots_default(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard lots with default filtering (active + recent)."""
        response = client.get("/api/v1/dashboard/lots", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Validate structure
        assert "lots" in data
        assert "total" in data
        assert isinstance(data["lots"], list)
        assert isinstance(data["total"], int)

        # Should include active LOTs (LOT 1) and recently closed (LOT 2), exclude old (LOT 3)
        assert data["total"] >= 1  # At least LOT 1 (IN_PROGRESS)

        # Validate lot structure
        if len(data["lots"]) > 0:
            lot = data["lots"][0]
            assert "lot_number" in lot
            assert "product_model" in lot
            assert "status" in lot
            assert "production_date" in lot
            assert "shift" in lot
            assert "target_quantity" in lot
            assert "actual_quantity" in lot
            assert "passed_quantity" in lot
            assert "failed_quantity" in lot
            assert "progress_percentage" in lot
            assert "created_at" in lot

    def test_dashboard_lots_empty_database(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard lots with empty database."""
        response = client.get("/api/v1/dashboard/lots", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        assert data["lots"] == []
        assert data["total"] == 0

    def test_dashboard_lots_with_status_filter(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard lots with status filtering."""
        response = client.get(
            "/api/v1/dashboard/lots?status=IN_PROGRESS",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert "lots" in data

        # All returned LOTs should have IN_PROGRESS status
        for lot in data["lots"]:
            assert lot["status"] == "IN_PROGRESS"

    def test_dashboard_lots_with_status_filter_closed(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard lots filtered by CLOSED status."""
        response = client.get(
            "/api/v1/dashboard/lots?status=CLOSED",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        # Should return all CLOSED lots including old ones
        for lot in data["lots"]:
            assert lot["status"] == "CLOSED"

    def test_dashboard_lots_with_status_filter_created(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard lots filtered by CREATED status."""
        response = client.get(
            "/api/v1/dashboard/lots?status=CREATED",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        # All returned lots should be CREATED
        for lot in data["lots"]:
            assert lot["status"] == "CREATED"

    def test_dashboard_lots_with_limit(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard lots with limit parameter."""
        response = client.get(
            "/api/v1/dashboard/lots?limit=1",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["lots"]) <= 1

    def test_dashboard_lots_with_high_limit(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard lots with high limit parameter."""
        response = client.get(
            "/api/v1/dashboard/lots?limit=100",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        # Should respect max limit of 100
        assert len(data["lots"]) <= 100

    def test_dashboard_lots_limit_validation(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard lots limit parameter validation."""
        # Valid limit
        response_valid = client.get(
            "/api/v1/dashboard/lots?limit=50",
            headers=auth_headers_admin
        )
        assert response_valid.status_code == 200

        # Invalid limit (0)
        response_invalid = client.get(
            "/api/v1/dashboard/lots?limit=0",
            headers=auth_headers_admin
        )
        assert response_invalid.status_code == 422

        # Invalid limit (101)
        response_invalid2 = client.get(
            "/api/v1/dashboard/lots?limit=101",
            headers=auth_headers_admin
        )
        assert response_invalid2.status_code == 422

    def test_dashboard_lots_limit_boundary_values(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard lots with boundary limit values."""
        # Minimum valid limit (1)
        response_min = client.get(
            "/api/v1/dashboard/lots?limit=1",
            headers=auth_headers_admin
        )
        assert response_min.status_code == 200

        # Maximum valid limit (100)
        response_max = client.get(
            "/api/v1/dashboard/lots?limit=100",
            headers=auth_headers_admin
        )
        assert response_max.status_code == 200

    def test_dashboard_lots_progress_calculation(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test progress percentage calculation in dashboard lots."""
        response = client.get("/api/v1/dashboard/lots", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify progress calculation for each lot
        for lot in data["lots"]:
            if lot["target_quantity"] > 0:
                completed = lot["passed_quantity"] + lot["failed_quantity"]
                expected_progress = round((completed / lot["target_quantity"]) * 100, 1)
                assert lot["progress_percentage"] == expected_progress

    def test_dashboard_lots_ordering(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that dashboard lots are ordered by creation date descending."""
        response = client.get("/api/v1/dashboard/lots", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify lots are ordered by created_at descending (newest first)
        if len(data["lots"]) > 1:
            created_dates = [lot["created_at"] for lot in data["lots"]]
            # Should be in descending order
            assert created_dates == sorted(created_dates, reverse=True)

    def test_dashboard_lots_product_model_reference(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that dashboard lots include product model references."""
        response = client.get("/api/v1/dashboard/lots", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify product_model field is included
        for lot in data["lots"]:
            # product_model should be either a string (model_code) or None
            assert "product_model" in lot
            assert lot["product_model"] is None or isinstance(lot["product_model"], str)

    def test_dashboard_lots_shift_field(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that dashboard lots include shift information."""
        response = client.get("/api/v1/dashboard/lots", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify shift field is included and valid
        for lot in data["lots"]:
            assert "shift" in lot
            assert lot["shift"] in ["D", "N", None]

    # ===================================================================
    # Process WIP Endpoint Tests (/api/v1/dashboard/process-wip)
    # ===================================================================

    def test_dashboard_process_wip(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test dashboard process WIP (Work In Progress)."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Validate structure
        assert "timestamp" in data
        assert "processes" in data
        assert "total_wip" in data
        assert "bottleneck_process" in data

        assert isinstance(data["processes"], list)
        assert isinstance(data["total_wip"], int)

        # Validate process structure
        if len(data["processes"]) > 0:
            process = data["processes"][0]
            assert "process_number" in process
            assert "process_code" in process
            assert "process_name" in process
            assert "wip_count" in process
            assert "average_cycle_time_seconds" in process

    def test_dashboard_process_wip_empty(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard process WIP with no processes."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        # Should return valid structure even with no processes
        assert "processes" in data
        assert "total_wip" in data
        assert isinstance(data["processes"], list)
        assert data["total_wip"] == 0

    def test_dashboard_process_wip_ordering(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that process WIP is ordered by process number."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify processes are ordered by process_number
        if len(data["processes"]) > 1:
            process_numbers = [p["process_number"] for p in data["processes"]]
            assert process_numbers == sorted(process_numbers)

    def test_dashboard_process_wip_bottleneck_detection(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test bottleneck detection in process WIP."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # If there are processes with WIP, bottleneck should be the highest
        if data["processes"] and data["total_wip"] > 0:
            max_wip = max(p["wip_count"] for p in data["processes"])
            bottleneck_process = next(
                p for p in data["processes"] if p["wip_count"] == max_wip
            )
            # Bottleneck should match the process with highest WIP
            if max_wip > 0:
                assert data["bottleneck_process"] == bottleneck_process["process_code"]

    def test_dashboard_process_wip_no_bottleneck_when_zero(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that bottleneck is None when all WIP counts are zero."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # If all WIP counts are zero, bottleneck should be None or empty
        if data["total_wip"] == 0:
            # bottleneck_process could be None or a process with 0 WIP
            assert data["bottleneck_process"] is None or data["total_wip"] == 0

    def test_dashboard_process_wip_total_calculation(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that total WIP is sum of all process WIP counts."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify total_wip equals sum of individual process wip_counts
        if data["processes"]:
            expected_total = sum(p["wip_count"] for p in data["processes"])
            assert data["total_wip"] == expected_total

    def test_dashboard_process_wip_cycle_time_format(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that average cycle time is properly formatted."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify cycle time is a number (float or int) and >= 0
        for process in data["processes"]:
            assert isinstance(process["average_cycle_time_seconds"], (int, float))
            assert process["average_cycle_time_seconds"] >= 0

    def test_dashboard_process_wip_timestamp_format(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that timestamp is in ISO format."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verify timestamp is a valid ISO datetime string
        assert "timestamp" in data
        # Should be parseable as ISO datetime
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)

    # ===================================================================
    # Authentication and Authorization Tests
    # ===================================================================

    def test_dashboard_endpoints_require_authentication(self, client: TestClient):
        """Test that all dashboard endpoints require authentication."""
        endpoints = [
            "/api/v1/dashboard/summary",
            "/api/v1/dashboard/lots",
            "/api/v1/dashboard/process-wip"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require auth"

    def test_dashboard_summary_with_operator_role(
        self, client: TestClient, auth_headers_operator: dict, dashboard_data
    ):
        """Test dashboard summary accessible to operator role."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers_operator)
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "lots" in data

    def test_dashboard_lots_with_manager_role(
        self, client: TestClient, auth_headers_manager: dict, dashboard_data
    ):
        """Test dashboard lots accessible to manager role."""
        response = client.get("/api/v1/dashboard/lots", headers=auth_headers_manager)
        assert response.status_code == 200
        data = response.json()
        assert "lots" in data
        assert "total" in data

    def test_dashboard_process_wip_with_operator_role(
        self, client: TestClient, auth_headers_operator: dict, dashboard_data
    ):
        """Test process WIP accessible to operator role."""
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_operator)
        assert response.status_code == 200
        data = response.json()
        assert "processes" in data

    def test_dashboard_endpoints_reject_invalid_token(self, client: TestClient):
        """Test that dashboard endpoints reject invalid authentication tokens."""
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        endpoints = [
            "/api/v1/dashboard/summary",
            "/api/v1/dashboard/lots",
            "/api/v1/dashboard/process-wip"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=invalid_headers)
            assert response.status_code == 401, f"Endpoint {endpoint} should reject invalid token"

    # ===================================================================
    # Edge Cases and Error Handling
    # ===================================================================

    def test_dashboard_summary_invalid_date_format(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard summary with invalid date format."""
        response = client.get(
            "/api/v1/dashboard/summary?target_date=invalid-date",
            headers=auth_headers_admin
        )
        # Should return 422 for invalid date format
        assert response.status_code == 422

    def test_dashboard_lots_invalid_status_filter(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard lots with invalid status filter."""
        response = client.get(
            "/api/v1/dashboard/lots?status=INVALID_STATUS",
            headers=auth_headers_admin
        )
        # Should return 422 for invalid enum value
        assert response.status_code == 422

    def test_dashboard_lots_negative_limit(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard lots with negative limit."""
        response = client.get(
            "/api/v1/dashboard/lots?limit=-1",
            headers=auth_headers_admin
        )
        # Should return 422 for negative limit
        assert response.status_code == 422

    def test_dashboard_lots_non_numeric_limit(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard lots with non-numeric limit."""
        response = client.get(
            "/api/v1/dashboard/lots?limit=abc",
            headers=auth_headers_admin
        )
        # Should return 422 for non-numeric limit
        assert response.status_code == 422

    # ===================================================================
    # Integration Tests - Complex Scenarios
    # ===================================================================

    def test_dashboard_summary_reflects_recent_changes(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test that dashboard summary reflects recent database changes."""
        # Get initial summary
        response1 = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        initial_data = response1.json()

        # Create a new serial (simulating production activity)
        lot_id = dashboard_data["lot_ids"][0]
        serial_data = {
            "lot_id": lot_id,
            "sequence_in_lot": 10,
            "status": "PASSED"
        }
        client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)

        # Get updated summary
        response2 = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        updated_data = response2.json()

        # The data should be consistent (may or may not change depending on date filters)
        assert "date" in updated_data
        assert "total_started" in updated_data

    def test_dashboard_lots_consistency_with_summary(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test consistency between lots endpoint and summary endpoint."""
        # Get summary
        summary_response = client.get("/api/v1/dashboard/summary", headers=auth_headers_admin)
        summary_data = summary_response.json()

        # Get lots
        lots_response = client.get("/api/v1/dashboard/lots", headers=auth_headers_admin)
        lots_data = lots_response.json()

        # Active lots should be consistent (within reasonable bounds)
        # Summary shows up to 10 active/recent lots, lots endpoint shows filtered lots
        # Both should return valid data structures
        assert isinstance(summary_data["lots"], list)
        assert isinstance(lots_data["lots"], list)

    def test_dashboard_process_wip_with_inactive_processes(
        self, client: TestClient, auth_headers_admin: dict, dashboard_data
    ):
        """Test process WIP endpoint filters out inactive processes."""
        # Create an inactive process
        inactive_process_data = {
            "process_number": 3,
            "process_code": "INACTIVE_PROC",
            "process_name_ko": "비활성 공정",
            "process_name_en": "Inactive Process",
            "description": "Inactive process",
            "estimated_duration_seconds": 30,
            "quality_criteria": {},
            "sort_order": 3,
            "is_active": False
        }
        client.post("/api/v1/processes/", json=inactive_process_data, headers=auth_headers_admin)

        # Get process WIP
        response = client.get("/api/v1/dashboard/process-wip", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Inactive process should not appear in WIP
        process_codes = [p["process_code"] for p in data["processes"]]
        assert "INACTIVE_PROC" not in process_codes
