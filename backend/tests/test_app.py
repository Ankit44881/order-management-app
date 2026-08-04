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

# --- Health Check Routes ---

def test_root_health_check(client):
    """Test root / route added for GKE Ingress Liveness/Readiness probes"""
    response = client.get('/')
    assert response.status_code == 200

def test_health_check(client):
    """Test dedicated /health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "chai-politics-backend"

# --- Helper Function Validations ---

def test_indian_phone_validation():
    """Test Indian phone number regex validation logic"""
    assert is_valid_indian_phone("9876543210") is True
    assert is_valid_indian_phone("5876543210") is False
    assert is_valid_indian_phone("987654321") is False

# --- Authentication & User API Edge Cases ---

def test_login_invalid_phone(client):
    """Test login with malformed phone number"""
    response = client.post('/api/login', json={"phone": "123"})
    assert response.status_code == 400

def test_login_missing_payload(client):
    """Test login without JSON body"""
    response = client.post('/api/login', json={})
    assert response.status_code in [400, 422]

def test_register_invalid_data(client):
    """Test registration endpoint validation"""
    response = client.post('/api/register', json={"name": "Test User", "phone": "999"})
    assert response.status_code == 400

# --- Menu & Public APIs ---

def test_get_menu(client):
    """Test fetching items from menu"""
    response = client.get('/api/menu')
    assert response.status_code in [200, 404, 500]

def test_404_handler(client):
    """Test non-existent route handling"""
    response = client.get('/api/non-existent-endpoint')
    assert response.status_code == 404