"""
Rate Limiter
============
Rate limiting utilities for API protection.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps


def rate_limit(max_requests=100, per_seconds=3600, message="Rate limit exceeded"):
    """
    Simple rate limiting decorator using Flask-Limiter.
    
    Args:
        max_requests: Maximum number of requests allowed
        per_seconds: Time window in seconds
        message: Error message
    """
    def decorator(f):
        # This is handled by Flask-Limiter globally
        # This decorator is for reference and custom logic
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Custom rate limiting logic can be added here
            return f(*args, **kwargs)
        return wrapped
    return decorator


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    'auth': {
        'register': '5 per hour',
        'login': '10 per minute',
        'logout': '30 per minute',
        'profile': '60 per minute'
    },
    'resume': {
        'list': '100 per hour',
        'create': '50 per hour',
        'update': '100 per hour',
        'delete': '20 per hour',
        'export': '30 per hour'
    },
    'ai': {
        'generate': '10 per hour',
        'suggest': '30 per hour',
        'ats_check': '20 per hour'
    },
    'admin': {
        'default': '100 per hour',
        'users': '50 per hour',
        'settings': '20 per hour'
    }
}


# Default rate limits
DEFAULT_RATE_LIMITS = {
    'default': '200 per day',
    'minimum': '10 per minute',
    'strict': '5 per minute'
}
