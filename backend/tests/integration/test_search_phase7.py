import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.saved_filter import SavedFilter

client = TestClient(app)

def test_search_process_data(db, normal_user_token_headers):
    # Note: Full-text search might return empty if no data matches or index not built.
    # We test the endpoint connectivity and parameter handling.
    response = client.get(
        "/api/v1/search/process-data?q=test",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_dynamic_filter(db, normal_user_token_headers):
    payload = {
        "filters": [
            {"field": "result", "operator": "eq", "value": "PASS"},
            {"field": "process_id", "operator": "gt", "value": 0}
        ],
        "limit": 10
    }
    
    response = client.post(
        "/api/v1/search/process-data/filter",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_saved_filters(db, normal_user_token_headers):
    # 1. Save a filter
    payload = {
        "name": "My Test Filter",
        "description": "Filters for passing items",
        "filters": [
            {"field": "result", "operator": "eq", "value": "PASS"}
        ]
    }
    
    response = client.post(
        "/api/v1/search/filters/save",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    filter_id = data["id"]
    assert data["name"] == "My Test Filter"
    
    # 2. List filters
    response = client.get(
        "/api/v1/search/filters/my-filters",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    filters = response.json()
    assert len(filters) >= 1
    assert any(f["id"] == filter_id for f in filters)
    
    # 3. Apply saved filter
    response = client.post(
        f"/api/v1/search/filters/{filter_id}/apply",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
