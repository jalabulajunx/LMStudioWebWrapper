# config/settings.py

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 1800,
        'pool_timeout': 30,
        'max_overflow': 20
    }
    
    # LM Studio
    LM_STUDIO_URL = os.getenv('LM_STUDIO_URL', 'http://localhost:1234/v1')
    LM_STUDIO_TIMEOUT = 30
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Cache
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # WebSocket
    SOCKETIO_MESSAGE_QUEUE = None
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_PING_TIMEOUT = 10
    SOCKETIO_PING_INTERVAL = 25
    
    # File Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}
    
    # Logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Use secure cookies
    SESSION_COOKIE_SECURE = True
    
    # Stricter security settings
    WTF_CSRF_SSL_STRICT = True
    
    # Production logging
    LOG_LEVEL = 'ERROR'
    
    # Use Redis for rate limiting in production
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Use Redis for caching in production
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    
    # Use Redis for WebSocket message queue
    SOCKETIO_MESSAGE_QUEUE = os.getenv('REDIS_URL', 'redis://localhost:6379/2')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Disable secure cookies for local development
    SESSION_COOKIE_SECURE = False
    
    # More detailed logging
    LOG_LEVEL = 'DEBUG'
    
    # Simplified rate limiting for development
    RATELIMIT_ENABLED = False
    
    # Use filesystem cache for development
    CACHE_TYPE = "filesystem"
    CACHE_DIR = "flask_cache"

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Use in-memory SQLite database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable secure cookies for testing
    SESSION_COOKIE_SECURE = False
    
    # Disable rate limiting for testing
    RATELIMIT_ENABLED = False
    
    # Use simple cache for testing
    CACHE_TYPE = "simple"
    
    # Disable WebSocket message queue for testing
    SOCKETIO_MESSAGE_QUEUE = None

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
