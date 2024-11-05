# server/security.py

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from functools import wraps
from flask import request, abort
import re

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def init_security(app):
    """Initialize security features"""
    # Rate limiting
    limiter.init_app(app)
    
    # Security headers
    Talisman(app,
        force_https=app.config['ENV'] == 'production',
        strict_transport_security=True,
        session_cookie_secure=app.config['SESSION_COOKIE_SECURE'],
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'font-src': ["'self'", "cdnjs.cloudflare.com"],
        }
    )

    @app.after_request
    def add_security_headers(response):
        """Add security headers to each response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    def sanitize_input(func):
        """Decorator to sanitize user input"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in request.form.items():
                if not isinstance(value, str):
                    continue
                # Check for potential XSS or SQL injection patterns
                if re.search(r'[<>]|javascript:|alert\(|SELECT\s+|\bUNION\b', value, re.I):
                    abort(400)
            return func(*args, **kwargs)
        return wrapper
    
    # Make sanitize_input decorator available through security module
    app.sanitize_input = sanitize_input
