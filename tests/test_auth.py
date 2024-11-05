# tests/test_auth.py

import pytest
from flask import url_for
from server.database import db, User
from server.auth import AuthManager, AuthenticationError

def test_create_user(app):
    """Test user creation"""
    with app.app_context():
        user = AuthManager.create_user('testuser', 'password123')
        assert user.username == 'testuser'
        assert user.check_password('password123')

def test_create_duplicate_user(app):
    """Test creating user with existing username"""
    with app.app_context():
        AuthManager.create_user('testuser', 'password123')
        with pytest.raises(AuthenticationError):
            AuthManager.create_user('testuser', 'newpassword')

def test_authenticate_user(app):
    """Test user authentication"""
    with app.app_context():
        AuthManager.create_user('testuser', 'password123')
        user = AuthManager.authenticate_user('testuser', 'password123')
        assert user.username == 'testuser'

def test_authenticate_invalid_credentials(app):
    """Test authentication with invalid credentials"""
    with app.app_context():
        AuthManager.create_user('testuser', 'password123')
        with pytest.raises(AuthenticationError):
            AuthManager.authenticate_user('testuser', 'wrongpassword')

def test_login_route(client):
    """Test login route"""
    with client:
        # Create test user
        AuthManager.create_user('testuser', 'password123')
        
        # Test GET request
        response = client.get('/login')
        assert response.status_code == 200
        
        # Test successful login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Chat' in response.data
        
        # Test invalid login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert b'Invalid username or password' in response.data

def test_logout_route(client):
    """Test logout route"""
    with client:
        # Create and login test user
        AuthManager.create_user('testuser', 'password123')
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Test logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

@pytest.fixture
def app():
    """Create test app"""
    from server.app import create_app
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-key'
    })
    
    with app.app_context():
        db.create_all()
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
