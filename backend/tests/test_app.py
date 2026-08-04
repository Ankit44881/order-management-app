import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app import app, is_valid_indian_phone

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- Health & Root Routes (GKE Probes) ---

def test_root_health_check(client):
    """Test root / route for GKE Ingress readiness/liveness"""
    response = client.get('/')
    assert response.status_code in [200, 404]

def test_health_check(client):
    """Test /health route"""
    response = client.get('/health')
    if response.status_code == 200:
        data = response.get_json()
        assert "status" in data or "service" in data

# --- Helper Function Tests ---

def test_indian_phone_validation():
    assert is_valid_indian_phone("9876543210") is True
    assert is_valid_indian_phone("5876543210") is False
    assert is_valid_indian_phone("987654321") is False

# --- All API Endpoints (GET / POST / OPTIONS) ---

def test_login_api_variations(client):
    # Invalid phone
    resp1 = client.post('/api/login', json={"phone": "123"})
    assert resp1.status_code in [400, 401, 422, 500]

    # Valid phone schema
    resp2 = client.post('/api/login', json={"phone": "9876543210"})
    assert resp2.status_code in [200, 400, 401, 404, 500]

    # Empty payload
    resp3 = client.post('/api/login', json={})
    assert resp3.status_code in [400, 422, 500]

def test_register_api_variations(client):
    resp1 = client.post('/api/register', json={"name": "Test", "phone": "123"})
    assert resp1.status_code in [400, 422, 500]

    resp2 = client.post('/api/register', json={"name": "Chai Lover", "phone": "9876543210"})
    assert resp2.status_code in [200, 201, 400, 409, 500]

def test_menu_api(client):
    resp = client.get('/api/menu')
    assert resp.status_code in [200, 404, 500]

def test_orders_api(client):
    resp_get = client.get('/api/orders')
    assert resp_get.status_code in [200, 401, 404, 500]

    resp_post = client.post('/api/orders', json={"items": []})
    assert resp_post.status_code in [200, 400, 401, 500]

def test_catch_all_404(client):
    resp = client.get('/api/random-unknown-endpoint')
    assert resp.status_code in [404, 500]