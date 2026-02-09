"""
Authentication Routes
=====================
API endpoints for user authentication and profile management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, create_access_token,
    create_refresh_token, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, get_jwt
)
from datetime import datetime
import re

from models.user import User, UserActivity
from models.admin import Admin
from utils.validators import validate_email, validate_password, validate_name
from utils.auth_guard import hash_password, verify_password, APIResponse
from flask_limiter import limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@limiter.limit('5 per hour')
def register():
    """Register a new user account."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return APIResponse.error('No data provided', 400)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        name = data.get('name', '').strip()
        
        # Validate email
        valid, email_error = validate_email(email)
        if not valid:
            return APIResponse.error(email_error, 400)
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return APIResponse.error('Email already registered', 400)
        
        # Validate password
        valid, password_error = validate_password(password)
        if not valid:
            return APIResponse.error('Password validation failed', 400, password_error)
        
        # Check password confirmation
        if password != confirm_password:
            return APIResponse.error('Passwords do not match', 400)
        
        # Validate name
        valid, name_error = validate_name(name)
        if not valid:
            return APIResponse.error(name_error, 400)
        
        # Create user
        user = User(
            email=email,
            password=password,
            name=name,
            is_active=True
        )
        
        # Add optional fields
        if data.get('phone'):
            user.phone = data['phone']
        
        # Save to database
        from app import db
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Log activity
        UserActivity.log_activity(
            user.id,
            'register',
            'User registered successfully',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        response = APIResponse.success({
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 'Registration successful', 201)
        
        # Set cookies
        set_access_cookies(response[0], access_token)
        set_refresh_cookies(response[0], refresh_token)
        
        return response
        
    except Exception as e:
        import logging
        logging.error(f"Registration error: {e}")
        return APIResponse.error('Registration failed', 500)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    """Authenticate user and return tokens."""
    try:
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate email format
        valid, email_error = validate_email(email)
        if not valid:
            return APIResponse.error('Invalid email format', 400)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return APIResponse.error('Invalid email or password', 401)
        
        # Check if user is active
        if not user.is_active:
            return APIResponse.error('Account is disabled', 401)
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return APIResponse.error('Invalid email or password', 401)
        
        # Update last login
        user.update_last_login()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Log activity
        UserActivity.log_activity(
            user.id,
            'login',
            'User logged in successfully',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        response = APIResponse.success({
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 'Login successful')
        
        # Set cookies
        set_access_cookies(response[0], access_token)
        set_refresh_cookies(response[0], refresh_token)
        
        return response
        
    except Exception as e:
        import logging
        logging.error(f"Login error: {e}")
        return APIResponse.error('Login failed', 500)


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Log out user and clear cookies."""
    try:
        user_id = get_jwt_identity()
        
        # Log activity
        UserActivity.log_activity(
            user_id,
            'logout',
            'User logged out',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        response = APIResponse.success(message='Logout successful')
        unset_jwt_cookies(response[0])
        
        return response
        
    except Exception as e:
        import logging
        logging.error(f"Logout error: {e}")
        return APIResponse.error('Logout failed', 500)


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token."""
    try:
        refresh_token = request.cookies.get('refresh_token')
        
        if not refresh_token:
            return APIResponse.error('Refresh token required', 401)
        
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        # Verify refresh token
        from utils.auth_guard import decode_token
        payload = decode_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return APIResponse.error('Invalid refresh token', 401)
        
        user_id = payload.get('sub')
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return APIResponse.error('User not found or inactive', 401)
        
        # Generate new tokens
        access_token = create_access_token(identity=user.id)
        
        response = APIResponse.success({
            'access_token': access_token
        })
        
        set_access_cookies(response[0], access_token)
        
        return response
        
    except Exception as e:
        import logging
        logging.error(f"Token refresh error: {e}")
        return APIResponse.error('Token refresh failed', 500)


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return APIResponse.error('User not found', 404)
        
        return APIResponse.success({
            'user': user.to_dict(include_sensitive=True)
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get profile error: {e}")
        return APIResponse.error('Failed to get profile', 500)


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return APIResponse.error('User not found', 404)
        
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        # Update allowed fields
        if 'name' in data:
            valid, error = validate_name(data['name'])
            if not valid:
                return APIResponse.error(error, 400)
            user.name = data['name']
        
        if 'phone' in data:
            user.phone = data.get('phone')
        
        if 'address' in data:
            user.address = data.get('address')
        
        if 'city' in data:
            user.city = data.get('city')
        
        if 'country' in data:
            user.country = data.get('country')
        
        if 'linkedin' in data:
            user.linkedin = data.get('linkedin')
        
        if 'github' in data:
            user.github = data.get('github')
        
        if 'portfolio' in data:
            user.portfolio = data.get('portfolio')
        
        if 'website' in data:
            user.website = data.get('website')
        
        if 'summary' in data:
            user.summary = data.get('summary')
        
        if 'timezone' in data:
            user.timezone = data.get('timezone')
        
        if 'language' in data:
            user.language = data.get('language')
        
        from app import db
        db.session.commit()
        
        # Log activity
        UserActivity.log_activity(
            user_id,
            'profile_update',
            'Profile updated',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return APIResponse.success({
            'user': user.to_dict(include_sensitive=True)
        }, 'Profile updated successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Update profile error: {e}")
        return APIResponse.error('Failed to update profile', 500)


@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return APIResponse.error('User not found', 404)
        
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            return APIResponse.error('Current password is incorrect', 400)
        
        # Validate new password
        valid, password_error = validate_password(new_password)
        if not valid:
            return APIResponse.error('New password validation failed', 400, password_error)
        
        # Check password confirmation
        if new_password != confirm_password:
            return APIResponse.error('Passwords do not match', 400)
        
        # Update password
        user.password = new_password
        from app import db
        db.session.commit()
        
        # Log activity
        UserActivity.log_activity(
            user_id,
            'password_change',
            'Password changed',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return APIResponse.success(message='Password changed successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Change password error: {e}")
        return APIResponse.error('Failed to change password', 500)
