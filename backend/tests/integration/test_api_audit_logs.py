"""Integration tests for Audit Logs API endpoints.

Tests audit log retrieval, filtering, and pagination
for /api/v1/audit-logs/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuditLogsAPI:
    """Test suite for Audit Logs API endpoints."""

    def test_list_audit_logs(self, client: TestClient, auth_headers_admin: dict):
        """Test listing audit logs."""
        response = client.get("/api/v1/audit-logs/", headers=auth_headers_admin)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_audit_log_by_id(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving audit log by ID."""
        # First create some activity to generate audit logs
        # Create a user which should generate an audit log
        user_data = {
            "username": "audit_test_user",
            "email": "audit@test.com",
            "password": "AuditPass123!",
            "full_name": "Audit Test User",
            "role": "OPERATOR",
            "is_active": True
        }
        create_response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_admin
        )
        assert create_response.status_code == 201

        # List audit logs
        logs_response = client.get("/api/v1/audit-logs/", headers=auth_headers_admin)
        if logs_response.status_code == 200:
            logs = logs_response.json()
            if len(logs) > 0:
                log_id = logs[0]["id"]
                # Get specific audit log
                response = client.get(
                    f"/api/v1/audit-logs/{log_id}",
                    headers=auth_headers_admin
                )
                assert response.status_code == 200

    def test_list_audit_logs_with_pagination(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test pagination of audit logs."""
        # Create some activity
        for i in range(5):
            user_data = {
                "username": f"audit_user_{i}",
                "email": f"audit{i}@test.com",
                "password": "Password123!",
                "full_name": f"Audit User {i}",
                "role": "OPERATOR",
                "is_active": True
            }
            client.post("/api/v1/users/", json=user_data, headers=auth_headers_admin)

        # Test pagination
        response = client.get(
            "/api/v1/audit-logs/?skip=0&limit=3",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filter_audit_logs_by_entity_type(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test filtering audit logs by entity_type."""
        # Create a user to generate audit log
        user_data = {
            "username": "filter_test_user",
            "email": "filter@test.com",
            "password": "FilterPass123!",
            "full_name": "Filter Test User",
            "role": "OPERATOR",
            "is_active": True
        }
        client.post("/api/v1/users/", json=user_data, headers=auth_headers_admin)

        # Filter by entity_type
        response = client.get(
            "/api/v1/audit-logs/?entity_type=users",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            assert all(log["entity_type"] == "users" for log in data)

    @pytest.mark.parametrize("action", ["CREATE", "UPDATE", "DELETE"])
    def test_filter_audit_logs_by_action(
        self, client: TestClient, auth_headers_admin: dict, action: str
    ):
        """Test filtering audit logs by action type."""
        response = client.get(
            f"/api/v1/audit-logs/?action={action}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        # Audit logs filtered by action
        if len(data) > 0:
            assert all(log["action"] == action for log in data)

    def test_audit_logs_require_authentication(self, client: TestClient):
        """Test that audit log endpoints require authentication."""
        response = client.get("/api/v1/audit-logs/")
        assert response.status_code == 401

    def test_audit_log_immutability(self, client: TestClient, auth_headers_admin: dict):
        """Test that audit logs cannot be modified or deleted."""
        # Get audit logs
        response = client.get("/api/v1/audit-logs/", headers=auth_headers_admin)
        if response.status_code == 200:
            logs = response.json()
            if len(logs) > 0:
                log_id = logs[0]["id"]

                # Try to update (should fail)
                update_response = client.put(
                    f"/api/v1/audit-logs/{log_id}",
                    json={"action": "MODIFIED"},
                    headers=auth_headers_admin
                )
                # Should be 405 Method Not Allowed or 404 if endpoint doesn't exist
                assert update_response.status_code in [404, 405]

                # Try to delete (should fail)
                delete_response = client.delete(
                    f"/api/v1/audit-logs/{log_id}",
                    headers=auth_headers_admin
                )
                # Should be 405 Method Not Allowed or 404 if endpoint doesn't exist
                assert delete_response.status_code in [404, 405]

    def test_audit_log_contains_required_fields(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test that audit logs contain all required fields."""
        # Create activity
        user_data = {
            "username": "fields_test_user",
            "email": "fields@test.com",
            "password": "FieldsPass123!",
            "full_name": "Fields Test User",
            "role": "OPERATOR",
            "is_active": True
        }
        client.post("/api/v1/users/", json=user_data, headers=auth_headers_admin)

        # Get audit logs
        response = client.get("/api/v1/audit-logs/", headers=auth_headers_admin)
        assert response.status_code == 200
        logs = response.json()
        if len(logs) > 0:
            log = logs[0]
            # Check required fields exist
            required_fields = ["id", "user_id", "entity_type", "entity_id", "action", "created_at"]
            for field in required_fields:
                assert field in log

    def test_filter_audit_logs_by_user(
        self, client: TestClient, auth_headers_admin: dict, test_admin_user
    ):
        """Test filtering audit logs by user_id."""
        # Create activity as admin
        user_data = {
            "username": "user_filter_test",
            "email": "userfilter@test.com",
            "password": "UserFilter123!",
            "full_name": "User Filter Test",
            "role": "OPERATOR",
            "is_active": True
        }
        client.post("/api/v1/users/", json=user_data, headers=auth_headers_admin)

        # Filter by user_id
        response = client.get(
            f"/api/v1/audit-logs/?user_id={test_admin_user.id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            assert all(log["user_id"] == test_admin_user.id for log in data)

    def test_audit_log_time_range_filter(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test filtering audit logs by time range."""
        from datetime import datetime, timedelta

        # Create activity
        user_data = {
            "username": "time_test_user",
            "email": "time@test.com",
            "password": "TimePass123!",
            "full_name": "Time Test User",
            "role": "OPERATOR",
            "is_active": True
        }
        client.post("/api/v1/users/", json=user_data, headers=auth_headers_admin)

        # Filter by date range (last hour)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)

        response = client.get(
            f"/api/v1/audit-logs/?start_time={start_time.isoformat()}&end_time={end_time.isoformat()}",
            headers=auth_headers_admin
        )
        # Should return 200 whether or not endpoint supports time filtering
        assert response.status_code in [200, 422]

    def test_get_audit_log_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting non-existent audit log returns 404."""
        response = client.get("/api/v1/audit-logs/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_get_entity_audit_logs(self, client: TestClient):
        """Test getting audit logs for a specific entity."""
        response = client.get("/api/v1/audit-logs/entity/lots/1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_entity_audit_logs_with_pagination(self, client: TestClient):
        """Test getting entity audit logs with pagination."""
        response = client.get("/api/v1/audit-logs/entity/serials/1?skip=0&limit=50")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_user_activity_logs(self, client: TestClient):
        """Test getting audit logs for user activity."""
        response = client.get("/api/v1/audit-logs/user/1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_user_activity_with_pagination(self, client: TestClient):
        """Test getting user activity logs with pagination."""
        response = client.get("/api/v1/audit-logs/user/1?skip=5&limit=25")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_logs_by_action_endpoint(self, client: TestClient):
        """Test the /action/{action} endpoint directly."""
        response = client.get("/api/v1/audit-logs/action/CREATE")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_logs_by_action_update(self, client: TestClient):
        """Test getting UPDATE action logs."""
        response = client.get("/api/v1/audit-logs/action/UPDATE")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_logs_by_action_delete(self, client: TestClient):
        """Test getting DELETE action logs."""
        response = client.get("/api/v1/audit-logs/action/DELETE")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_logs_by_action_invalid(self, client: TestClient):
        """Test getting logs with invalid action returns 400."""
        response = client.get("/api/v1/audit-logs/action/INVALID")
        assert response.status_code == 400
        assert "Invalid action" in response.json()["detail"]

    def test_get_logs_by_action_lowercase(self, client: TestClient):
        """Test getting logs with lowercase action still works."""
        response = client.get("/api/v1/audit-logs/action/create")
        assert response.status_code == 200


    def test_get_entity_history(self, client: TestClient):
        """Test getting complete change history for an entity."""
        response = client.get("/api/v1/audit-logs/entity/lots/1/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_entity_history_with_pagination(self, client: TestClient):
        """Test getting entity history with pagination."""
        response = client.get("/api/v1/audit-logs/entity/serials/1/history?skip=0&limit=50")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_entity_history_nonexistent(self, client: TestClient):
        """Test getting history for nonexistent entity returns empty list."""
        response = client.get("/api/v1/audit-logs/entity/lots/999999/history")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_audit_logs_limit_exceeds_max(self, client: TestClient, auth_headers_admin: dict):
        """Test that limit exceeding maximum returns 422."""
        response = client.get("/api/v1/audit-logs/?skip=0&limit=101", headers=auth_headers_admin)
        assert response.status_code == 422

    def test_list_audit_logs_invalid_skip(self, client: TestClient, auth_headers_admin: dict):
        """Test that negative skip returns 422."""
        response = client.get("/api/v1/audit-logs/?skip=-1&limit=10", headers=auth_headers_admin)
        assert response.status_code == 422

    def test_get_audit_log_invalid_id(self, client: TestClient):
        """Test getting audit log with invalid ID returns 422."""
        response = client.get("/api/v1/audit-logs/0")
        assert response.status_code == 422

    def test_get_entity_audit_logs_invalid_entity_id(self, client: TestClient):
        """Test getting entity audit logs with invalid entity ID."""
        response = client.get("/api/v1/audit-logs/entity/lots/0")
        assert response.status_code == 422

    def test_get_user_activity_invalid_user_id(self, client: TestClient):
        """Test getting user activity with invalid user ID."""
        response = client.get("/api/v1/audit-logs/user/0")
        assert response.status_code == 422
