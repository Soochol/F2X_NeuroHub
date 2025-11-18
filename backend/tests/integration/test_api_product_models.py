"""Integration tests for Product Models API endpoints.

Tests all CRUD operations, search, filtering, and validation
for /api/v1/product-models/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestProductModelsAPI:
    """Test suite for Product Models API endpoints."""

    def test_list_product_models_empty(self, client: TestClient, auth_headers_admin: dict):
        """Test listing product models when database is empty."""
        response = client.get("/api/v1/product-models/", headers=auth_headers_admin)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_product_model(self, client: TestClient, auth_headers_admin: dict):
        """Test creating a new product model."""
        product_data = {
            "model_code": "PM-001",
            "model_name": "Test Product Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {"width": 100, "height": 50},
            "status": "DRAFT",
            "production_cycle_days": 5
        }
        response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert data["model_code"] == "PM-001"
        assert data["model_name"] == "Test Product Model"
        assert "id" in data
        assert "created_at" in data

    def test_create_product_model_duplicate_code(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test creating product model with duplicate model_code fails."""
        product_data = {
            "model_code": "PM-DUP",
            "model_name": "First Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "DRAFT",
            "production_cycle_days": 3
        }
        # Create first product model
        response1 = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        assert response1.status_code == 201

        # Try to create duplicate
        product_data["model_name"] = "Second Model"
        response2 = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        assert response2.status_code == 409

    def test_get_product_model_by_id(self, client: TestClient, auth_headers_admin: dict):
        """Test retrieving product model by ID."""
        # Create a product model first
        product_data = {
            "model_code": "PM-GET",
            "model_name": "Get Test Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {"test": True},
            "status": "ACTIVE",
            "production_cycle_days": 4
        }
        create_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]

        # Get product model by ID
        response = client.get(
            f"/api/v1/product-models/{product_id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["model_code"] == "PM-GET"

    def test_get_product_model_not_found(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting non-existent product model returns 404."""
        response = client.get("/api/v1/product-models/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_product_model(self, client: TestClient, auth_headers_admin: dict):
        """Test updating an existing product model."""
        # Create product model
        product_data = {
            "model_code": "PM-UPD",
            "model_name": "Original Name",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "DRAFT",
            "production_cycle_days": 5
        }
        create_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_id = create_response.json()["id"]

        # Update product model
        update_data = {
            "model_name": "Updated Name",
            "status": "ACTIVE",
            "specifications": {"updated": True}
        }
        response = client.put(
            f"/api/v1/product-models/{product_id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == "Updated Name"
        assert data["status"] == "ACTIVE"

    def test_delete_product_model(self, client: TestClient, auth_headers_admin: dict):
        """Test deleting a product model."""
        # Create product model
        product_data = {
            "model_code": "PM-DEL",
            "model_name": "To Delete",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "DRAFT",
            "production_cycle_days": 2
        }
        create_response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        product_id = create_response.json()["id"]

        # Delete product model
        response = client.delete(
            f"/api/v1/product-models/{product_id}",
            headers=auth_headers_admin
        )
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/v1/product-models/{product_id}",
            headers=auth_headers_admin
        )
        assert get_response.status_code == 404

    def test_list_product_models_with_pagination(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test pagination of product models list."""
        # Create multiple product models
        for i in range(5):
            product_data = {
                "model_code": f"PM-PAGE-{i}",
                "model_name": f"Model {i}",
                "version": "1.0",
                "category": "Standard",
                "specifications": {},
                "status": "ACTIVE",
                "production_cycle_days": 3
            }
            client.post(
                "/api/v1/product-models/",
                json=product_data,
                headers=auth_headers_admin
            )

        # Test pagination
        response = client.get(
            "/api/v1/product-models/?skip=0&limit=3",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_product_model_by_code(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test retrieving product model by model_code."""
        # Create product model
        product_data = {
            "model_code": "PM-CODE-123",
            "model_name": "Code Test",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 4
        }
        client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )

        # Get by code
        response = client.get(
            "/api/v1/product-models/code/PM-CODE-123",
            headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_code"] == "PM-CODE-123"

    def test_list_active_product_models(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test filtering product models by active status."""
        # Create active and draft models
        active_data = {
            "model_code": "PM-ACTIVE",
            "model_name": "Active Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "ACTIVE",
            "production_cycle_days": 3
        }
        draft_data = {
            "model_code": "PM-DRAFT",
            "model_name": "Draft Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": "DRAFT",
            "production_cycle_days": 3
        }
        client.post("/api/v1/product-models/", json=active_data, headers=auth_headers_admin)
        client.post("/api/v1/product-models/", json=draft_data, headers=auth_headers_admin)

        # Get active only
        response = client.get("/api/v1/product-models/active", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert all(model["status"] == "ACTIVE" for model in data)

    def test_product_model_requires_authentication(self, client: TestClient):
        """Test that product model endpoints require authentication."""
        # Try to list without auth
        response = client.get("/api/v1/product-models/")
        assert response.status_code == 401

    def test_create_product_model_validation_fails(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test that invalid product model data fails validation."""
        # Missing required field
        invalid_data = {
            "model_name": "No Code Model",
            "version": "1.0"
        }
        response = client.post(
            "/api/v1/product-models/",
            json=invalid_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 422

    @pytest.mark.parametrize("status", ["DRAFT", "ACTIVE", "DEPRECATED"])
    def test_product_model_status_values(
        self, client: TestClient, auth_headers_admin: dict, status: str
    ):
        """Test creating product models with different valid status values."""
        product_data = {
            "model_code": f"PM-STATUS-{status}",
            "model_name": f"{status} Model",
            "version": "1.0",
            "category": "Standard",
            "specifications": {},
            "status": status,
            "production_cycle_days": 3
        }
        response = client.post(
            "/api/v1/product-models/",
            json=product_data,
            headers=auth_headers_admin
        )
        assert response.status_code == 201
        assert response.json()["status"] == status
