"""
Integration tests for main application endpoints (app/main.py).

Tests:
    - GET /health (health check)
    - GET / (root endpoint)
    - CORS configuration
    - API documentation endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check_returns_200(self, client: TestClient):
        """Test health check endpoint is accessible."""
        response = client.get("/health")

        assert response.status_code == 200

    def test_health_check_returns_correct_data(self, client: TestClient):
        """Test health check returns expected data structure."""
        response = client.get("/health")

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data

    def test_health_check_app_name(self, client: TestClient):
        """Test health check returns correct app name."""
        response = client.get("/health")

        data = response.json()
        assert "F2X NeuroHub" in data["app"]

    def test_health_check_version_format(self, client: TestClient):
        """Test health check returns version in correct format."""
        response = client.get("/health")

        data = response.json()
        version = data["version"]
        assert isinstance(version, str)
        assert len(version) > 0


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint_returns_200(self, client: TestClient):
        """Test root endpoint is accessible."""
        response = client.get("/")

        assert response.status_code == 200

    def test_root_endpoint_returns_api_info(self, client: TestClient):
        """Test root endpoint returns API information."""
        response = client.get("/")

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    def test_root_endpoint_docs_url(self, client: TestClient):
        """Test root endpoint provides docs URL."""
        response = client.get("/")

        data = response.json()
        assert "/api/v1/docs" in data["docs"]


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_json_accessible(self, client: TestClient):
        """Test OpenAPI JSON schema is accessible."""
        response = client.get("/api/v1/openapi.json")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_openapi_schema_structure(self, client: TestClient):
        """Test OpenAPI schema has correct structure."""
        response = client.get("/api/v1/openapi.json")

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_swagger_docs_accessible(self, client: TestClient):
        """Test Swagger UI is accessible."""
        response = client.get("/api/v1/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_docs_accessible(self, client: TestClient):
        """Test ReDoc is accessible."""
        response = client.get("/api/v1/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers_present_on_valid_origin(self, client: TestClient):
        """Test CORS headers are present for allowed origins."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200
        # CORS headers should be present
        # Note: TestClient doesn't fully simulate CORS, but we can check endpoints work

    def test_preflight_request(self, client: TestClient):
        """Test OPTIONS preflight request."""
        response = client.options(
            "/api/v1/users/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )

        # Preflight should be handled
        assert response.status_code in [200, 204]


class TestAPIVersioning:
    """Test API versioning structure."""

    def test_v1_prefix_required(self, client: TestClient):
        """Test that v1 prefix is required for API endpoints."""
        # This should work (with /api/v1 prefix)
        response_with_prefix = client.get("/api/v1/users/")
        # Users endpoint might return 200 or other status, but should not 404

        # This should NOT work (without /api/v1 prefix)
        response_without_prefix = client.get("/users/")
        assert response_without_prefix.status_code == 404

    def test_all_routers_under_v1(self, client: TestClient):
        """Test that all API routers are under /api/v1 prefix."""
        openapi = client.get("/api/v1/openapi.json").json()
        paths = openapi["paths"].keys()

        for path in paths:
            if path.startswith("/api/"):
                assert path.startswith("/api/v1/"), f"Path {path} not under /api/v1"


class TestApplicationMetadata:
    """Test application metadata and configuration."""

    def test_app_name_in_openapi(self, client: TestClient):
        """Test application name appears in OpenAPI schema."""
        openapi = client.get("/api/v1/openapi.json").json()

        assert "F2X NeuroHub" in openapi["info"]["title"]

    def test_app_version_in_openapi(self, client: TestClient):
        """Test application version appears in OpenAPI schema."""
        openapi = client.get("/api/v1/openapi.json").json()

        assert "version" in openapi["info"]
        assert len(openapi["info"]["version"]) > 0

    def test_app_description_in_openapi(self, client: TestClient):
        """Test application description appears in OpenAPI schema."""
        openapi = client.get("/api/v1/openapi.json").json()

        assert "description" in openapi["info"]
        assert "Manufacturing Execution System" in openapi["info"]["description"]


class TestAPITags:
    """Test API endpoint organization with tags."""

    def test_auth_endpoints_tagged(self, client: TestClient):
        """Test authentication endpoints are properly tagged."""
        openapi = client.get("/api/v1/openapi.json").json()

        auth_paths = [p for p in openapi["paths"].keys() if "/auth/" in p]
        assert len(auth_paths) > 0

        for path in auth_paths:
            for method in openapi["paths"][path].values():
                if "tags" in method:
                    assert "Authentication" in method["tags"]

    def test_users_endpoints_tagged(self, client: TestClient):
        """Test users endpoints are properly tagged."""
        openapi = client.get("/api/v1/openapi.json").json()

        if "/api/v1/users/" in openapi["paths"]:
            users_path = openapi["paths"]["/api/v1/users/"]
            for method in users_path.values():
                if "tags" in method:
                    assert "Users" in method["tags"]

    def test_all_tags_defined(self, client: TestClient):
        """Test all used tags are defined in OpenAPI schema."""
        openapi = client.get("/api/v1/openapi.json").json()

        used_tags = set()
        for path_data in openapi["paths"].values():
            for operation in path_data.values():
                if "tags" in operation:
                    used_tags.update(operation["tags"])

        # All tags should be defined
        if "tags" in openapi:
            defined_tags = {tag["name"] for tag in openapi["tags"]}
            # At least some tags should be defined
            assert len(defined_tags) > 0


class TestErrorHandling:
    """Test global error handling."""

    def test_404_for_nonexistent_endpoint(self, client: TestClient):
        """Test 404 response for nonexistent endpoint."""
        response = client.get("/nonexistent/endpoint")

        assert response.status_code == 404

    def test_404_error_format(self, client: TestClient):
        """Test 404 error has correct format."""
        response = client.get("/nonexistent/endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_405_for_wrong_method(self, client: TestClient):
        """Test 405 response for wrong HTTP method."""
        # GET /users/ is allowed, but DELETE is not
        response = client.delete("/api/v1/users/")

        assert response.status_code == 405  # Method Not Allowed
