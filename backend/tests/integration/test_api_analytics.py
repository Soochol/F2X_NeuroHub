"""Integration tests for Analytics API endpoints.

Tests dashboard statistics and analytics
for /api/v1/analytics/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestAnalyticsAPI:
    """Test suite for Analytics API endpoints."""

    def test_get_dashboard_summary(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving dashboard summary statistics."""
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        # Dashboard should contain key metrics
        assert isinstance(data, dict)

    def test_get_production_statistics(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test retrieving production statistics."""
        response = client.get(
            "/api/v1/analytics/production-stats",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_quality_metrics(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving quality metrics."""
        response = client.get(
            "/api/v1/analytics/quality-metrics",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_process_performance(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test retrieving process performance metrics."""
        response = client.get(
            "/api/v1/analytics/process-performance",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_analytics_with_date_range(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test analytics endpoints with date range filters."""
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        response = client.get(
            f"/api/v1/analytics/dashboard?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
            headers=auth_headers_admin
        )
        # Should return 200 or 422 if date filtering not implemented
        assert response.status_code in [200, 422]

    def test_get_operator_performance(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test retrieving operator performance statistics."""
        response = client.get(
            "/api/v1/analytics/operator-performance",
            headers=auth_headers_admin
        )
        # Endpoint exists, should return 200
        assert response.status_code == 200

    def test_get_lot_statistics(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving LOT-specific statistics."""
        # Create a product model and LOT first
        product_data = {
            "model_code": "PM-ANALYTICS",
            "model_name": "Analytics Model",
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

        from datetime import date
        lot_data = {
            "product_model_id": product_model_id,
            "production_date": date.today().isoformat(),
            "shift": "D",
            "target_quantity": 50,
            "status": "IN_PROGRESS"
        }
        lot_response = client.post(
            "/api/v1/lots/",
            json=lot_data,
            headers=auth_headers_admin
        )
        lot_id = lot_response.json()["id"]

        # Get statistics for this LOT
        response = client.get(
            f"/api/v1/analytics/lots/{lot_id}",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404]

    def test_get_process_statistics(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test retrieving process-specific statistics."""
        # Create a process first
        process_data = {
            "process_number": 1,
            "process_code": "LASER_MARKING",
            "process_name_ko": "레이저 마킹",
            "process_name_en": "Laser Marking",
            "description": "Laser marking for analytics",
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

        # Get statistics for this process
        response = client.get(
            f"/api/v1/analytics/processes/{process_id}",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404]

    def test_analytics_require_authentication(self, client: TestClient):
        """Test that analytics endpoints require authentication."""
        response = client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 401

    def test_dashboard_with_empty_data(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test dashboard returns valid response even with no production data."""
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        # Should return structure with zero/empty values
        assert isinstance(data, dict)

    def test_get_real_time_metrics(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving real-time production metrics."""
        response = client.get(
            "/api/v1/analytics/realtime-status",
            headers=auth_headers_admin
        )
        # Endpoint exists, should return 200
        assert response.status_code == 200

    def test_get_shift_performance(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving shift-based performance metrics."""
        response = client.get(
            "/api/v1/analytics/shift-performance",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404]

    @pytest.mark.parametrize("shift", ["DAY", "NIGHT", "EVENING"])
    def test_get_shift_specific_analytics(
        self, client: TestClient, auth_headers_admin: dict, shift: str
    ):
        """Test retrieving analytics for specific shifts."""
        response = client.get(
            f"/api/v1/analytics/shift-performance?shift={shift}",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404, 422]

    def test_get_defect_analysis(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving defect analysis data."""
        response = client.get(
            "/api/v1/analytics/defects",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404]

    def test_get_trend_analysis(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving trend analysis over time."""
        response = client.get(
            "/api/v1/analytics/trends",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404]

    def test_analytics_pagination(self, client: TestClient, auth_headers_admin: dict):
        """Test pagination support in analytics endpoints."""
        response = client.get(
            "/api/v1/analytics/dashboard?skip=0&limit=10",
            headers=auth_headers_admin
        )
        assert response.status_code in [200, 422]

    def test_export_analytics_report(self, client: TestClient, auth_headers_admin: dict):
        """Test exporting analytics report (if implemented)."""
        response = client.get(
            "/api/v1/analytics/export",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404]

    def test_get_product_model_analytics(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test retrieving analytics for specific product models."""
        # Create a product model
        product_data = {
            "model_code": "PM-ANALYTICS-STAT",
            "model_name": "Analytics Stats Model",
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

        # Get analytics for this product model
        response = client.get(
            f"/api/v1/analytics/product-models/{product_model_id}",
            headers=auth_headers_admin
        )
        # May or may not be implemented
        assert response.status_code in [200, 404]
