"""Comprehensive integration tests for Analytics API endpoints.

Tests dashboard statistics and analytics with realistic production data
for /api/v1/analytics/* endpoints.
"""

from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient


class TestAnalyticsAPIWithData:
    """Test suite for Analytics API endpoints with realistic data."""

    @pytest.fixture(scope="function")
    def production_data(self, client: TestClient, auth_headers_admin: dict):
        """
        Create comprehensive production data for analytics testing.

        Creates:
        - 2 product models
        - 3 LOTs (2 IN_PROGRESS, 1 CLOSED)
        - 10 serials (6 PASSED, 3 FAILED, 1 IN_PROGRESS)
        - 2 processes
        - 20 process data records (15 PASS, 5 FAIL)
        """
        data = {}

        # Create 2 product models
        pm1_data = {
            "model_code": "PM-ANALYTICS-01",
            "model_name": "Analytics Model 1",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 5
        }
        pm1_resp = client.post("/api/v1/product-models/", json=pm1_data, headers=auth_headers_admin)
        data["pm1_id"] = pm1_resp.json()["id"]

        pm2_data = {
            "model_code": "PM-ANALYTICS-02",
            "model_name": "Analytics Model 2",
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
            "process_code": "LASER_MARK_ANALYTICS",
            "process_name_ko": "레이저 마킹",
            "process_name_en": "Laser Marking",
            "description": "Laser marking for analytics",
            "estimated_duration_seconds": 30,
            "quality_criteria": {"power_min": 45, "power_max": 55},
            "sort_order": 1
        }
        proc1_resp = client.post("/api/v1/processes/", json=process1_data, headers=auth_headers_admin)
        data["process1_id"] = proc1_resp.json()["id"]

        process2_data = {
            "process_number": 2,
            "process_code": "ASSEMBLY_ANALYTICS",
            "process_name_ko": "조립",
            "process_name_en": "Assembly",
            "description": "Assembly for analytics",
            "estimated_duration_seconds": 60,
            "quality_criteria": {},
            "sort_order": 2
        }
        proc2_resp = client.post("/api/v1/processes/", json=process2_data, headers=auth_headers_admin)
        data["process2_id"] = proc2_resp.json()["id"]

        # Create 3 LOTs
        today = date.today()
        data["lot_ids"] = []

        for i in range(3):
            lot_data = {
                "product_model_id": data["pm1_id"] if i < 2 else data["pm2_id"],
                "production_date": today.isoformat(),
                "shift": "D",
                "target_quantity": 5 if i < 2 else 3,
                "status": "CLOSED" if i == 2 else "IN_PROGRESS"
            }
            lot_resp = client.post("/api/v1/lots/", json=lot_data, headers=auth_headers_admin)
            lot_id = lot_resp.json()["id"]
            data["lot_ids"].append(lot_id)

            # Create serials for each LOT
            num_serials = 5 if i < 2 else 3
            for j in range(num_serials):
                status = "IN_PROGRESS" if (i == 0 and j == 0) else ("PASSED" if j < 2 else "FAILED")
                serial_data = {
                    "lot_id": lot_id,
                    "sequence_in_lot": j + 1,
                    "status": status
                }
                # Add failure_reason for FAILED status
                if status == "FAILED":
                    serial_data["failure_reason"] = f"Test failure reason for serial {j+1}"

                serial_resp = client.post("/api/v1/serials/", json=serial_data, headers=auth_headers_admin)
                serial_id = serial_resp.json()["id"]

                # Create process data for each serial (except first which is IN_PROGRESS)
                if not (i == 0 and j == 0):
                    # Process 1
                    pd1_data = {
                        "lot_id": lot_id,
                        "serial_id": serial_id,
                        "process_id": data["process1_id"],
                        "operator_id": 1,
                        "data_level": "SERIAL",
                        "result": "PASS" if j < 2 else "FAIL",
                        "measurements": {"power": 50 if j < 2 else 60},
                        "started_at": datetime.now().isoformat(),
                        "duration_seconds": 25 + j * 2
                    }
                    client.post("/api/v1/process-data/", json=pd1_data, headers=auth_headers_admin)

                    # Process 2
                    pd2_data = {
                        "lot_id": lot_id,
                        "serial_id": serial_id,
                        "process_id": data["process2_id"],
                        "operator_id": 1,
                        "data_level": "SERIAL",
                        "result": "PASS" if j < 3 else "FAIL",
                        "measurements": {"temperature": 25},
                        "started_at": datetime.now().isoformat(),
                        "duration_seconds": 55 + j * 3
                    }
                    client.post("/api/v1/process-data/", json=pd2_data, headers=auth_headers_admin)

        return data

    def test_dashboard_summary_with_data(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test dashboard summary with realistic production data."""
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Validate structure
        assert "lots" in data
        assert "serials" in data
        assert "quality" in data
        assert "processes" in data

        # Validate LOT metrics
        assert data["lots"]["total"] >= 3
        assert data["lots"]["active"] >= 2

        # Validate serial metrics
        assert data["serials"]["total"] >= 13
        assert data["serials"]["in_progress"] >= 1

        # Validate quality metrics exist
        assert "overall_pass_rate" in data["quality"]
        assert "defect_rate" in data["quality"]

    def test_production_statistics_with_date_range(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test production statistics with date range filtering."""
        today = date.today()
        week_ago = today - timedelta(days=7)

        response = client.get(
            f"/api/v1/analytics/production-stats?start_date={week_ago.isoformat()}&end_date={today.isoformat()}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()

        # Validate structure
        assert "date_range" in data
        assert data["date_range"]["start"] == week_ago.isoformat()
        assert data["date_range"]["end"] == today.isoformat()

        assert "lots_by_date" in data
        assert "serials_by_date" in data
        assert isinstance(data["lots_by_date"], list)
        assert isinstance(data["serials_by_date"], list)

    def test_process_performance_metrics(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test process performance metrics calculation."""
        response = client.get("/api/v1/analytics/process-performance", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Validate structure
        assert "processes" in data
        assert "summary" in data

        # Should have at least 2 processes from test data
        processes = data["processes"]
        assert len(processes) >= 2

        # Validate process data structure
        for proc in processes:
            assert "process_number" in proc
            assert "process_code" in proc
            assert "total_executions" in proc
            assert "success_count" in proc
            assert "failure_count" in proc
            assert "success_rate" in proc
            assert "average_cycle_time_seconds" in proc

            # Validate calculations
            if proc["total_executions"] > 0:
                calculated_rate = round(
                    (proc["success_count"] / proc["total_executions"]) * 100, 2
                )
                assert proc["success_rate"] == calculated_rate

    def test_quality_metrics_with_days_param(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test quality metrics with days parameter."""
        response = client.get(
            "/api/v1/analytics/quality-metrics?days=7",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_operator_performance_analytics(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test operator performance analytics."""
        response = client.get(
            "/api/v1/analytics/operator-performance?days=7",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_realtime_status_metrics(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test real-time status metrics."""
        response = client.get("/api/v1/analytics/realtime-status", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_defects_analysis_endpoint(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test defects analysis endpoint."""
        today = date.today()
        week_ago = today - timedelta(days=7)

        response = client.get(
            f"/api/v1/analytics/defects?start_date={week_ago.isoformat()}&end_date={today.isoformat()}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_defect_trends_daily(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test defect trends with daily aggregation."""
        response = client.get(
            "/api/v1/analytics/defect-trends?period=daily&days=7",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.parametrize("period", ["daily", "weekly", "monthly"])
    def test_defect_trends_periods(
        self, client: TestClient, auth_headers_admin: dict, production_data, period: str
    ):
        """Test defect trends with different aggregation periods."""
        response = client.get(
            f"/api/v1/analytics/defect-trends?period={period}&days=30",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

    def test_cycle_time_analysis_all_processes(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test cycle time analysis for all processes."""
        response = client.get(
            "/api/v1/analytics/cycle-time?days=30",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_cycle_time_analysis_specific_process(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test cycle time analysis for specific process."""
        process_id = production_data["process1_id"]

        response = client.get(
            f"/api/v1/analytics/cycle-time?process_id={process_id}&days=30",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_analytics_require_authentication(self, client: TestClient):
        """Test that all analytics endpoints require authentication."""
        endpoints = [
            "/api/v1/analytics/dashboard",
            "/api/v1/analytics/production-stats",
            "/api/v1/analytics/process-performance",
            "/api/v1/analytics/quality-metrics",
            "/api/v1/analytics/operator-performance",
            "/api/v1/analytics/realtime-status",
            "/api/v1/analytics/defects",
            "/api/v1/analytics/defect-trends",
            "/api/v1/analytics/cycle-time"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require auth"

    def test_dashboard_with_empty_database(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard returns valid response with empty database."""
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Should return structure with zero values
        assert isinstance(data, dict)
        assert "lots" in data
        assert "serials" in data

    def test_production_stats_default_date_range(
        self, client: TestClient, auth_headers_admin: dict, production_data
    ):
        """Test production stats with default date range (last 7 days)."""
        response = client.get("/api/v1/analytics/production-stats", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()
        assert "date_range" in data

        # Should default to last 7 days
        end_date = date.fromisoformat(data["date_range"]["end"])
        start_date = date.fromisoformat(data["date_range"]["start"])

        assert (end_date - start_date).days <= 7

    def test_quality_metrics_days_validation(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test quality metrics days parameter validation."""
        # Valid range: 1-90
        response_valid = client.get(
            "/api/v1/analytics/quality-metrics?days=30",
            headers=auth_headers_admin
        )
        assert response_valid.status_code == 200

        # Invalid: days=0
        response_invalid = client.get(
            "/api/v1/analytics/quality-metrics?days=0",
            headers=auth_headers_admin
        )
        assert response_invalid.status_code == 422

        # Invalid: days=100
        response_invalid2 = client.get(
            "/api/v1/analytics/quality-metrics?days=100",
            headers=auth_headers_admin
        )
        assert response_invalid2.status_code == 422

    def test_operator_performance_days_validation(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test operator performance days parameter validation."""
        # Valid
        response = client.get(
            "/api/v1/analytics/operator-performance?days=14",
            headers=auth_headers_admin
        )
        assert response.status_code == 200

        # Invalid: negative
        response_invalid = client.get(
            "/api/v1/analytics/operator-performance?days=-1",
            headers=auth_headers_admin
        )
        assert response_invalid.status_code == 422

    def test_defect_trends_period_validation(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test defect trends period parameter validation."""
        # Valid periods
        for period in ["daily", "weekly", "monthly"]:
            response = client.get(
                f"/api/v1/analytics/defect-trends?period={period}",
                headers=auth_headers_admin
            )
            assert response.status_code == 200
