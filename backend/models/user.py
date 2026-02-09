"""
User Model
==========
Database model for user accounts.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and profile management."""

    __tablename__ = 'users'

    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile fields
    name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    portfolio = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    
    # Professional summary (for resume)
    summary = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Status fields
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # Preferences
    timezone = db.Column(db.String(50), default='UTC', nullable=True)
    language = db.Column(db.String(10), default='en', nullable=True)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('UserActivity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def password(self):
        """Prevent direct password access."""
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )

    def verify_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Get user ID for Flask-Login."""
        return str(self.id)

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'linkedin': self.linkedin,
            'github': self.github,
            'portfolio': self.portfolio,
            'website': self.website,
            'summary': self.summary,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
        }
        
        if include_sensitive:
            return data
        
        # Remove sensitive fields for non-admin users
        if not include_sensitive:
            data.pop('is_active', None)
            data.pop('is_admin', None)
        
        return data

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
        db.session.commit()

    @property
    def resume_count(self):
        """Get number of resumes."""
        return self.resumes.count()

    @property
    def created_resumes(self):
        """Get all user resumes."""
        return self.resumes.order_by(Resume.created_at.desc()).all()


class UserActivity(db.Model):
    """Track user activities for analytics."""

    __tablename__ = 'user_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Activity details
    activity_type = db.Column(db.String(50), nullable=False)
    activity_details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<UserActivity {self.activity_type}>'

    @staticmethod
    def log_activity(user_id, activity_type, details=None, ip_address=None, user_agent=None):
        """Log a user activity."""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(activity)
        db.session.commit()
        return activity

    def to_dict(self):
        """Convert activity to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'activity_details': self.activity_details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }
