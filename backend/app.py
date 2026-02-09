"""
FreeUltraCV - Main Application
==============================

A professional CV/resume builder with AI-powered features.
"""

import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import get_config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()


def create_app(config=None):
    """Application factory pattern."""
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure limiter
    limiter.init_app(app)

    # Configure cache
    cache.init_app(app, config={
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 300
    })

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/static/*": {"origins": "*"}
    })

    # Register blueprints
    from routes.auth import auth_bp
    from routes.resume import resume_bp
    from routes.ai_tools import ai_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(resume_bp, url_prefix='/api/resumes')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Register static file serving for exports
    @app.route('/exports/<path:filename>')
    def serve_export(filename):
        """Serve exported files."""
        return send_from_directory(
            app.config['EXPORT_FOLDER'],
            filename,
            as_attachment=True
        )

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'environment': app.config.get('DEBUG', False) and 'development' or 'production'
        })

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': str(error)}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

    # Request logging
    @app.after_request
    def log_request(response):
        if request.path.startswith('/api/'):
            logging.info(f'{request.method} {request.path} - {response.status_code}')
        return response

    # Initialize database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        from models.user import User
        from models.admin import Admin
        from utils.auth_guard import hash_password
        
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@freultracv.com')
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')
        
        if not User.query.filter_by(email=admin_email).first():
            admin_user = User(
                email=admin_email,
                password_hash=hash_password(admin_password),
                name='Admin',
                is_admin=True,
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info(f'Admin user created: {admin_email}')

    return app


# Create application instance
app = create_app()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
