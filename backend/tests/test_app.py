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

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "chai-politics-backend"

def test_indian_phone_validation():
    assert is_valid_indian_phone("9876543210") is True
    assert is_valid_indian_phone("5876543210") is False
    assert is_valid_indian_phone("987654321") is False

def test_login_invalid_phone(client):
    response = client.post('/api/login', json={"phone": "123"})
    assert response.status_code == 400