# config/__init__.py

from .settings import config

def get_config(env='default'):
    """Get configuration based on environment"""
    return config[env]
