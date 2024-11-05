# server/cache.py

from flask_caching import Cache
from functools import wraps
import hashlib
import json

cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

def init_cache(app):
    """Initialize caching with application"""
    cache_config = {
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    }
    
    # Add Redis configuration if specified
    if app.config.get('CACHE_REDIS_URL'):
        cache_config['CACHE_REDIS_URL'] = app.config['CACHE_REDIS_URL']
    
    cache.init_app(app, config=cache_config)

def cache_key(*args, **kwargs):
    """Generate a cache key from function arguments"""
    key_dict = {'args': args, 'kwargs': kwargs}
    return hashlib.md5(json.dumps(key_dict, sort_keys=True).encode()).hexdigest()

def cached_with_key(*cache_args, **cache_kwargs):
    """Custom caching decorator with key generation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_value = cache.get(cache_key(args, kwargs))
            if cache_value is not None:
                return cache_value
            value = f(*args, **kwargs)
            cache.set(cache_key(args, kwargs), value, *cache_args, **cache_kwargs)
            return value
        return decorated_function
    return decorator

# Example cached functions that might be useful
@cache.memoize(300)
def get_user_chats(user_id):
    """Cache user chats for 5 minutes"""
    from .database import Chat
    return Chat.query.filter_by(user_id=user_id).all()

@cache.memoize(3600)
def get_user_preferences(user_id):
    """Cache user preferences for 1 hour"""
    from .database import User
    user = User.query.get(user_id)
    return user.preferences if user else None
