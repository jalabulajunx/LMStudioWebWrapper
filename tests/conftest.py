# tests/conftest.py
import pytest
from server import create_app
from server.database import db as _db
from server.auth import AuthManager

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    return app

@pytest.fixture
def db(app):
    """Create database for testing"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def authenticated_user(db, client):
    """Create and authenticate a test user"""
    user = AuthManager.create_user('testuser', 'password123')
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    return user
