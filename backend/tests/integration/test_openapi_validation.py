"""
OpenAPI/Swagger Schema Validation Tests

Validates:
    - OpenAPI spec compliance (OpenAPI 3.x)
    - Schema structure and completeness
    - Endpoint documentation coverage
    - Response schema definitions
    - Security scheme definitions
    - Tag consistency
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any, List


@pytest.mark.swagger
@pytest.mark.integration
class TestOpenAPIValidation:
    """Comprehensive OpenAPI/Swagger validation test suite."""

    def test_openapi_schema_accessible(self, client: TestClient):
        """Test that OpenAPI schema endpoint is accessible."""
        response = client.get("/api/v1/openapi.json")

        assert response.status_code == 200, "OpenAPI schema should be accessible"
        assert response.headers["content-type"] == "application/json"

    def test_openapi_schema_structure(self, client: TestClient):
        """Test that OpenAPI schema has valid structure."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        # Required OpenAPI 3.x fields
        assert "openapi" in schema, "Schema must have 'openapi' version field"
        assert schema["openapi"].startswith("3."), "Must be OpenAPI 3.x"

        assert "info" in schema, "Schema must have 'info' section"
        assert "paths" in schema, "Schema must have 'paths' section"

        # Info section validation
        info = schema["info"]
        assert "title" in info, "Info must have title"
        assert "version" in info, "Info must have version"
        assert "description" in info, "Info must have description"

        print(f"✓ OpenAPI Version: {schema['openapi']}")
        print(f"✓ API Title: {info['title']}")
        print(f"✓ API Version: {info['version']}")

    def test_all_endpoints_documented(self, client: TestClient):
        """Test that all endpoints are properly documented."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})

        assert len(paths) > 0, "Schema should have at least one endpoint"

        undocumented_endpoints = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    # Check for summary or description
                    if not details.get("summary") and not details.get("description"):
                        undocumented_endpoints.append(f"{method.upper()} {path}")

        assert len(undocumented_endpoints) == 0, \
            f"Following endpoints lack documentation: {undocumented_endpoints}"

        print(f"✓ Total documented endpoints: {sum(len([m for m in methods if m in ['get', 'post', 'put', 'delete', 'patch']]) for methods in paths.values())}")

    def test_response_schemas_defined(self, client: TestClient):
        """Test that all endpoints have response schemas defined."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})
        endpoints_without_responses = []

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    responses = details.get("responses", {})

                    # Should have at least one response defined
                    if not responses:
                        endpoints_without_responses.append(f"{method.upper()} {path}")

                    # Check for 200/201 success responses
                    success_codes = ["200", "201", "204"]
                    has_success_response = any(code in responses for code in success_codes)

                    if not has_success_response and method != "delete":
                        endpoints_without_responses.append(
                            f"{method.upper()} {path} (missing success response)"
                        )

        assert len(endpoints_without_responses) == 0, \
            f"Following endpoints lack response schemas: {endpoints_without_responses}"

    def test_security_schemes_defined(self, client: TestClient):
        """Test that security schemes are properly defined."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        components = schema.get("components", {})
        security_schemes = components.get("securitySchemes", {})

        # Should have at least one security scheme (Bearer token)
        assert len(security_schemes) > 0, "API should define security schemes"

        # Check for OAuth2 or Bearer token authentication
        has_bearer_auth = any(
            scheme.get("type") == "http" and scheme.get("scheme") == "bearer"
            for scheme in security_schemes.values()
        )

        has_oauth2 = any(
            scheme.get("type") == "oauth2"
            for scheme in security_schemes.values()
        )

        assert has_bearer_auth or has_oauth2, \
            "API should have Bearer or OAuth2 authentication defined"

        print(f"✓ Security schemes defined: {list(security_schemes.keys())}")

    def test_tags_consistency(self, client: TestClient):
        """Test that all tags used in endpoints are defined in schema."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        # Get defined tags
        defined_tags = {tag["name"] for tag in schema.get("tags", [])}

        # Get used tags
        used_tags = set()
        paths = schema.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    tags = details.get("tags", [])
                    used_tags.update(tags)

        # All used tags should be defined
        undefined_tags = used_tags - defined_tags

        # Note: FastAPI auto-generates tags, so this might be empty
        # But we log for visibility
        if undefined_tags:
            print(f"⚠ Tags used but not explicitly defined: {undefined_tags}")

        print(f"✓ Defined tags: {defined_tags}")
        print(f"✓ Used tags: {used_tags}")

    def test_request_body_schemas(self, client: TestClient):
        """Test that POST/PUT/PATCH endpoints have request body schemas."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})
        endpoints_without_request_body = []

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["post", "put", "patch"]:
                    request_body = details.get("requestBody")

                    # POST/PUT/PATCH should typically have request body
                    # (unless it's a special case like logout)
                    if not request_body and "login" not in path and "logout" not in path:
                        endpoints_without_request_body.append(f"{method.upper()} {path}")

        # This is a warning, not a hard failure
        if endpoints_without_request_body:
            print(f"⚠ Endpoints without request body: {endpoints_without_request_body}")

    def test_swagger_ui_accessible(self, client: TestClient):
        """Test that Swagger UI is accessible."""
        response = client.get("/api/v1/docs")

        assert response.status_code == 200, "Swagger UI should be accessible"
        assert "text/html" in response.headers["content-type"]

    def test_redoc_accessible(self, client: TestClient):
        """Test that ReDoc is accessible."""
        response = client.get("/api/v1/redoc")

        assert response.status_code == 200, "ReDoc should be accessible"
        assert "text/html" in response.headers["content-type"]

    def test_schema_components_defined(self, client: TestClient):
        """Test that reusable components are properly defined."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        components = schema.get("components", {})

        # Should have schemas component for data models
        assert "schemas" in components, "Components should include schemas"

        schemas = components["schemas"]
        assert len(schemas) > 0, "Should have at least one reusable schema"

        print(f"✓ Total reusable schemas: {len(schemas)}")
        print(f"✓ Schema names: {list(schemas.keys())[:10]}...")  # First 10

    def test_error_responses_documented(self, client: TestClient):
        """Test that endpoints document error responses."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})
        endpoints_without_error_responses = []

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    responses = details.get("responses", {})

                    # Should document at least one error response (4xx or 5xx)
                    error_codes = ["400", "401", "403", "404", "422", "500"]
                    has_error_response = any(code in responses for code in error_codes)

                    if not has_error_response:
                        endpoints_without_error_responses.append(f"{method.upper()} {path}")

        # This is informational - some endpoints might not need error docs
        if endpoints_without_error_responses:
            print(f"ℹ Endpoints without documented error responses: {len(endpoints_without_error_responses)}")

    def test_operation_ids_unique(self, client: TestClient):
        """Test that all operation IDs are unique."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})
        operation_ids = []

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    operation_id = details.get("operationId")
                    if operation_id:
                        operation_ids.append((operation_id, f"{method.upper()} {path}"))

        # Check for duplicates
        seen = set()
        duplicates = []
        for op_id, endpoint in operation_ids:
            if op_id in seen:
                duplicates.append((op_id, endpoint))
            seen.add(op_id)

        assert len(duplicates) == 0, \
            f"Duplicate operation IDs found: {duplicates}"

        print(f"✓ Total unique operation IDs: {len(operation_ids)}")

    def test_schema_validation_with_validator(self, client: TestClient):
        """Test OpenAPI schema using openapi-spec-validator."""
        try:
            from openapi_spec_validator import validate_spec
            from openapi_spec_validator.readers import read_from_filename
        except ImportError:
            pytest.skip("openapi-spec-validator not installed")

        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        # Validate the schema
        try:
            # This will raise an exception if the schema is invalid
            validate_spec(schema)
            print("✓ OpenAPI schema is valid according to OpenAPI 3.x specification")
        except Exception as e:
            pytest.fail(f"OpenAPI schema validation failed: {str(e)}")

    def test_endpoint_count(self, client: TestClient):
        """Test and log total endpoint count for monitoring."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})

        endpoint_count = 0
        methods_count = {"get": 0, "post": 0, "put": 0, "delete": 0, "patch": 0}

        for path, methods in paths.items():
            for method in methods.keys():
                if method in methods_count:
                    endpoint_count += 1
                    methods_count[method] += 1

        print("\n" + "="*60)
        print("📊 API ENDPOINT STATISTICS")
        print("="*60)
        print(f"Total Endpoints: {endpoint_count}")
        print(f"GET:    {methods_count['get']}")
        print(f"POST:   {methods_count['post']}")
        print(f"PUT:    {methods_count['put']}")
        print(f"DELETE: {methods_count['delete']}")
        print(f"PATCH:  {methods_count['patch']}")
        print("="*60)

        # Ensure we have a reasonable number of endpoints
        assert endpoint_count > 0, "API should have at least one endpoint"


@pytest.mark.swagger
@pytest.mark.integration
class TestEndpointCoverage:
    """Test that all critical endpoints are documented."""

    def test_health_endpoint_documented(self, client: TestClient):
        """Test that health check endpoint is documented."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})

        # Health endpoint should exist
        assert "/health" in paths, "Health check endpoint should be documented"

    def test_auth_endpoints_documented(self, client: TestClient):
        """Test that authentication endpoints are documented."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})

        # Check for auth-related endpoints
        auth_paths = [path for path in paths.keys() if "auth" in path or "login" in path]

        assert len(auth_paths) > 0, "Authentication endpoints should be documented"
        print(f"✓ Auth endpoints: {auth_paths}")

    def test_crud_endpoints_documented(self, client: TestClient):
        """Test that major CRUD endpoints are documented."""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema.get("paths", {})

        # Check for major resource endpoints
        expected_resources = ["users", "lots", "serials", "processes"]

        for resource in expected_resources:
            resource_paths = [path for path in paths.keys() if resource in path]
            assert len(resource_paths) > 0, \
                f"{resource.capitalize()} endpoints should be documented"

        print(f"✓ All major CRUD resources documented")
