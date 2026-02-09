"""
API Routes Package
==================
Imports and exposes all API route blueprints.
"""

from routes.auth import auth_bp
from routes.resume import resume_bp
from routes.ai_tools import ai_bp
from routes.admin import admin_bp

__all__ = [
    'auth_bp',
    'resume_bp',
    'ai_bp',
    'admin_bp'
]
