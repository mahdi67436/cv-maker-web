"""
FreeUltraCV Configuration
=========================
Configuration settings for the application.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///freultracv.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 10,
    }

    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800)))
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = not DEBUG
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'lax'

    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    EXPORT_FOLDER = os.environ.get('EXPORT_FOLDER', 'exports')

    # AI settings
    AI_API_KEY = os.environ.get('AI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4')

    # Security settings
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'

    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day')

    # Admin settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@freultracv.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')

    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create upload and export folders
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///freultracv_dev.db'
    JWT_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///freultracv_test.db'
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        """Initialize production app with additional settings."""
        super().init_app(app)

        # Log production settings
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
