"""
Validators
==========
Input validation utilities.
"""

import re
from email_validator import validate_email, EmailNotValidError
from flask import current_app


def validate_email(email_str):
    """Validate email address."""
    if not email_str:
        return False, 'Email is required'
    
    try:
        valid = validate_email(email_str)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password):
    """Validate password strength."""
    if not password:
        return False, 'Password is required'
    
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters')
    
    if len(password) > 128:
        errors.append('Password must be less than 128 characters')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    return len(errors) == 0, errors


def validate_phone(phone_str):
    """Validate phone number."""
    if not phone_str:
        return True, None  # Phone is optional
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone_str)
    
    # Check for valid phone formats
    if re.match(r'^\+?[1-9]\d{6,14}$', cleaned):
        return True, None
    
    if re.match(r'^\d{10,15}$', cleaned):
        return True, None
    
    return False, 'Invalid phone number format'


def validate_name(name_str):
    """Validate name field."""
    if not name_str:
        return False, 'Name is required'
    
    if len(name_str) < 2:
        return False, 'Name must be at least 2 characters'
    
    if len(name_str) > 100:
        return False, 'Name must be less than 100 characters'
    
    # Allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", name_str):
        return False, 'Name can only contain letters, spaces, hyphens, and apostrophes'
    
    return True, None


def validate_url(url_str):
    """Validate URL format."""
    if not url_str:
        return True, None  # URL is optional
    
    pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// or https://
        r'([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,6}'  # domain
        r'(:\d+)?'  # optional port
        r'(\/[^\s]*)?$'  # optional path
    )
    
    if not pattern.match(url_str):
        return False, 'Invalid URL format'
    
    return True, None


def validate_resume_title(title_str):
    """Validate resume title."""
    if not title_str:
        return False, 'Title is required'
    
    if len(title_str) < 3:
        return False, 'Title must be at least 3 characters'
    
    if len(title_str) > 200:
        return False, 'Title must be less than 200 characters'
    
    return True, None


def validate_json_content(content):
    """Validate JSON content structure."""
    if not isinstance(content, dict):
        return False, 'Content must be a JSON object'
    
    return True, None


def sanitize_string(text):
    """Sanitize string input."""
    if not text:
        return text
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Strip whitespace
    text = text.strip()
    
    return text


def sanitize_html(text):
    """Remove potentially dangerous HTML."""
    if not text:
        return text
    
    import re
    
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove event handlers
    text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=\s*[^\s>]+', '', text, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    text = re.sub(r'javascript:[^\s>]*', '', text, flags=re.IGNORECASE)
    
    # Remove data: protocol (potential XSS)
    text = re.sub(r'data:[^\s>]*', '', text, flags=re.IGNORECASE)
    
    return text


class ValidationError(Exception):
    """Custom validation error."""
    
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(message)
