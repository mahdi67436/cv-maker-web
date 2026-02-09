"""
Authentication Guard
=====================
Security utilities for password hashing and token management.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request


def hash_password(password):
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password, password_hash):
    """Verify password against hash."""
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception:
        return False


def generate_token(user_id, token_type='access', expires_in=None):
    """Generate JWT token."""
    secret = current_app.config.get('JWT_SECRET_KEY')
    
    if token_type == 'access':
        expires = expires_in or current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
    else:
        expires = expires_in or current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=7))
    
    payload = {
        'sub': user_id,
        'type': token_type,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expires
    }
    
    return jwt.encode(payload, secret, algorithm='HS256')


def decode_token(token):
    """Decode and verify JWT token."""
    secret = current_app.config.get('JWT_SECRET_KEY')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def admin_required(fn):
    """Decorator to require admin access."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from models.user import User
        
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_admin:
                return {'error': 'Admin access required', 'status': 403}, 403
            
        except Exception:
            return {'error': 'Authentication required', 'status': 401}, 401
        
        return fn(*args, **kwargs)
    return wrapper


def rate_limit(max_requests=100, per_seconds=3600):
    """Simple rate limiting decorator."""
    from collections import defaultdict
    from time import time
    
    requests = defaultdict(list)
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = time()
            user_ip = request.remote_addr if hasattr(request, 'remote_addr') else 'anonymous'
            
            # Clean old requests
            requests[user_ip] = [t for t in requests[user_ip] if now - t < per_seconds]
            
            if len(requests[user_ip]) >= max_requests:
                return {'error': 'Rate limit exceeded', 'status': 429}, 429
            
            requests[user_ip].append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_input(text):
    """Sanitize user input to prevent XSS."""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    import re
    sanitized = re.sub(r'<[^>]*>', '', str(text))
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+=', '', sanitized)
    
    return sanitized.strip()


def generate_secure_filename(filename):
    """Generate secure filename for uploads."""
    import re
    import uuid
    
    # Get extension
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    # Create safe filename
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', filename.rsplit('.', 1)[0] if '.' in filename else filename)
    safe_name = safe_name[:50]  # Limit length
    
    return f"{uuid.uuid4().hex}_{safe_name}.{ext}"


class APIResponse:
    """Standardized API response format."""
    
    @staticmethod
    def success(data=None, message=None, status=200):
        response = {'success': True}
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
        return response, status
    
    @staticmethod
    def error(message, status=400, errors=None):
        response = {'success': False, 'error': message}
        if errors:
            response['errors'] = errors
        return response, status
