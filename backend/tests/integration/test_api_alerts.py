"""Integration tests for Alerts API endpoints.

Tests alert management, filtering, and status transitions
for /api/v1/alerts/* endpoints.
"""

from datetime import date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient


class TestAlertsAPI:
    """Test suite for Alerts API endpoints."""

    def test_list_alerts_empty(self, client: TestClient, auth_headers_admin: dict):
        """Test listing alerts when database is empty."""
        response = client.get("/api/v1/alerts/", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert data["alerts"] == []
        assert data["total"] == 0

    def test_create_alert(self, client: TestClient, auth_headers_admin: dict):
        """Test creating a basic alert."""
        alert_data = {
            "alert_type": "MANUAL",
            "severity": "MEDIUM",
            "title": "Test Alert",
            "message": "This is a test alert message"
        }
        response = client.post("/api/v1/alerts/", json=alert_data, headers=auth_headers_admin)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Alert"
        assert data["severity"] == "MEDIUM"
        assert data["status"] == "UNREAD"

    def test_create_alert_with_lot(self, client: TestClient, auth_headers_admin: dict):
        """Test creating alert with LOT reference."""
        # Create product model and LOT
        product_data = {
            "model_code": "PM-ALERT-TEST",
            "model_name": "Alert Test Model",
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

        # Create alert with LOT reference
        alert_data = {
            "alert_type": "LOT_COMPLETED",
            "severity": "LOW",
            "title": "LOT Completed",
            "message": "LOT production completed successfully",
            "lot_id": lot_id
        }
        response = client.post("/api/v1/alerts/", json=alert_data, headers=auth_headers_admin)
        assert response.status_code == 201
        data = response.json()
        assert data["lot_id"] == lot_id

    def test_get_alert_by_id(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving alert by ID."""
        # Create alert
        alert_data = {
            "alert_type": "SYSTEM_ERROR",
            "severity": "HIGH",
            "title": "System Error",
            "message": "Critical system error occurred"
        }
        create_response = client.post(
            "/api/v1/alerts/",
            json=alert_data,
            headers=auth_headers_admin
        )
        alert_id = create_response.json()["id"]

        # Get alert by ID
        response = client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == alert_id
        assert data["title"] == "System Error"

    def test_update_alert_status(self, client: TestClient, auth_headers_admin: dict):
        """Test updating alert status."""
        # Create alert
        alert_data = {
            "alert_type": "MANUAL",
            "severity": "MEDIUM",
            "title": "Test Update",
            "message": "Testing status update"
        }
        create_response = client.post(
            "/api/v1/alerts/",
            json=alert_data,
            headers=auth_headers_admin
        )
        alert_id = create_response.json()["id"]

        # Update status to READ
        update_data = {"status": "READ"}
        response = client.put(
            f"/api/v1/alerts/{alert_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "READ"

    def test_mark_alert_as_read(self, client: TestClient, auth_headers_admin: dict, test_admin_user):
        """Test marking single alert as read."""
        # Create alert
        alert_data = {
            "alert_type": "MANUAL",
            "severity": "LOW",
            "title": "Mark Read Test",
            "message": "Testing mark as read"
        }
        create_response = client.post(
            "/api/v1/alerts/",
            json=alert_data,
            headers=auth_headers_admin
        )
        alert_id = create_response.json()["id"]

        # Mark as read
        mark_read_data = {"read_by_id": test_admin_user.id}
        response = client.put(
            f"/api/v1/alerts/{alert_id}/read",
            json=mark_read_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "READ"
        assert data["read_at"] is not None

    def test_bulk_mark_alerts_as_read(self, client: TestClient, auth_headers_admin: dict, test_admin_user):
        """Test marking multiple alerts as read."""
        # Create multiple alerts
        alert_ids = []
        for i in range(3):
            alert_data = {
                "alert_type": "MANUAL",
                "severity": "LOW",
                "title": f"Bulk Test {i+1}",
                "message": f"Alert {i+1} for bulk test"
            }
            response = client.post(
                "/api/v1/alerts/",
                json=alert_data,
                headers=auth_headers_admin
            )
            alert_ids.append(response.json()["id"])

        # Bulk mark as read
        bulk_data = {
            "alert_ids": alert_ids,
            "read_by_id": test_admin_user.id
        }
        response = client.put(
            "/api/v1/alerts/bulk-read",
            json=bulk_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 3

    def test_get_unread_count(self, client: TestClient, auth_headers_admin: dict, test_admin_user):
        """Test getting count of unread alerts."""
        # Create mix of read and unread alerts
        for i in range(5):
            alert_data = {
                "alert_type": "MANUAL",
                "severity": "LOW",
                "title": f"Unread Test {i+1}",
                "message": f"Alert {i+1}"
            }
            response = client.post(
                "/api/v1/alerts/",
                json=alert_data,
                headers=auth_headers_admin
            )
            # Mark first 2 as read
            if i < 2:
                alert_id = response.json()["id"]
                mark_read_data = {"read_by_id": test_admin_user.id}
                client.put(
                    f"/api/v1/alerts/{alert_id}/read",
                    json=mark_read_data,
                    headers=auth_headers_admin
                )

        # Get unread count
        response = client.get("/api/v1/alerts/unread/count", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 3

    def test_filter_alerts_by_severity(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering alerts by severity."""
        # Create alerts with different severities
        severities = ["HIGH", "MEDIUM", "LOW", "HIGH"]
        for sev in severities:
            alert_data = {
                "alert_type": "MANUAL",
                "severity": sev,
                "title": f"Severity {sev}",
                "message": f"Alert with {sev} severity"
            }
            client.post("/api/v1/alerts/", json=alert_data, headers=auth_headers_admin)

        # Filter by HIGH severity
        response = client.get("/api/v1/alerts/?severity=HIGH", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) == 2
        for alert in data["alerts"]:
            assert alert["severity"] == "HIGH"

    def test_filter_alerts_by_status(self, client: TestClient, auth_headers_admin: dict, test_admin_user):
        """Test filtering alerts by status."""
        # Create alerts and mark some as read
        for i in range(4):
            alert_data = {
                "alert_type": "MANUAL",
                "severity": "MEDIUM",
                "title": f"Status Test {i+1}",
                "message": f"Alert {i+1}"
            }
            response = client.post(
                "/api/v1/alerts/",
                json=alert_data,
                headers=auth_headers_admin
            )
            # Mark first 2 as read
            if i < 2:
                alert_id = response.json()["id"]
                mark_read_data = {"read_by_id": test_admin_user.id}
                client.put(
                    f"/api/v1/alerts/{alert_id}/read",
                    json=mark_read_data,
                    headers=auth_headers_admin
                )

        # Filter by UNREAD status
        response = client.get("/api/v1/alerts/?status=UNREAD", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) == 2
        for alert in data["alerts"]:
            assert alert["status"] == "UNREAD"

    def test_filter_alerts_by_type(self, client: TestClient, auth_headers_admin: dict):
        """Test filtering alerts by alert type."""
        # Create alerts with different types
        types = ["DEFECT_DETECTED", "MANUAL", "SYSTEM_ERROR", "DEFECT_DETECTED"]
        for alert_type in types:
            alert_data = {
                "alert_type": alert_type,
                "severity": "MEDIUM",
                "title": f"Type {alert_type}",
                "message": f"Alert of type {alert_type}"
            }
            client.post("/api/v1/alerts/", json=alert_data, headers=auth_headers_admin)

        # Filter by DEFECT_DETECTED type
        response = client.get("/api/v1/alerts/?alert_type=DEFECT_DETECTED", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) == 2
        for alert in data["alerts"]:
            assert alert["alert_type"] == "DEFECT_DETECTED"

    def test_delete_alert(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting an alert."""
        # Create alert
        alert_data = {
            "alert_type": "MANUAL",
            "severity": "LOW",
            "title": "Delete Test",
            "message": "Alert to be deleted"
        }
        create_response = client.post(
            "/api/v1/alerts/",
            json=alert_data,
            headers=auth_headers_admin
        )
        alert_id = create_response.json()["id"]

        # Delete alert
        response = client.delete(f"/api/v1/alerts/{alert_id}", headers=auth_headers_admin)
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers_admin)
        assert get_response.status_code == 404

    def test_alerts_require_authentication(self, client: TestClient):
        """Test that alert endpoints require authentication."""
        response = client.get("/api/v1/alerts/")
        assert response.status_code == 401

    def test_pagination(self, client: TestClient, auth_headers_admin: dict):
        """Test alert list pagination."""
        # Create 15 alerts
        for i in range(15):
            alert_data = {
                "alert_type": "MANUAL",
                "severity": "LOW",
                "title": f"Pagination Test {i+1}",
                "message": f"Alert {i+1} for pagination"
            }
            client.post("/api/v1/alerts/", json=alert_data, headers=auth_headers_admin)

        # Get first page (limit 10)
        response = client.get("/api/v1/alerts/?skip=0&limit=10", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) == 10
        assert data["total"] == 15

        # Get second page
        response = client.get("/api/v1/alerts/?skip=10&limit=10", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) == 5

    def test_alert_with_severity_levels(self, client: TestClient, auth_headers_admin: dict):
        """Test creating alerts with different severity levels."""
        severities = ["HIGH", "MEDIUM", "LOW"]
        for severity in severities:
            alert_data = {
                "alert_type": "MANUAL",
                "severity": severity,
                "title": f"Severity {severity}",
                "message": f"Testing {severity} severity"
            }
            response = client.post(
                "/api/v1/alerts/",
                json=alert_data,
                headers=auth_headers_admin
            )
            assert response.status_code == 201
            assert response.json()["severity"] == severity

    def test_alert_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting non-existent alert returns 404."""
        response = client.get("/api/v1/alerts/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_non_existent_alert(self, client: TestClient, auth_headers_admin: dict):
        """Test updating non-existent alert returns 404."""
        update_data = {"status": "READ"}
        response = client.put(
            "/api/v1/alerts/99999",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 404

    def test_delete_non_existent_alert(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting non-existent alert returns 404."""
        response = client.delete("/api/v1/alerts/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_mark_non_existent_alert_as_read(self, client: TestClient, auth_headers_admin: dict, test_admin_user):
        """Test marking non-existent alert as read returns 404."""
        mark_read_data = {"read_by_id": test_admin_user.id}
        response = client.put(
            "/api/v1/alerts/99999/read",
            json=mark_read_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 404
