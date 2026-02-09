"""
Admin Model
===========
Database model for admin-related functionality.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Admin(db.Model):
    """Admin user model - extends User for admin-specific functionality."""

    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Admin role and permissions
    role = db.Column(db.String(50), default='admin')  # super_admin, admin, moderator
    permissions = db.Column(db.JSON, nullable=True)
    
    # Admin details
    last_activity = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Admin {self.role}>'

    def has_permission(self, permission):
        """Check if admin has specific permission."""
        if not self.permissions:
            return False
        return permission in self.permissions

    def to_dict(self):
        """Convert admin to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'permissions': self.permissions,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """Audit log for admin actions."""

    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    # Action details
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    action_type = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.Integer, nullable=True)
    
    # Action data
    old_value = db.Column(db.JSON, nullable=True)
    new_value = db.Column(db.JSON, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Request metadata
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<AuditLog {self.action_type}>'

    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action_type': self.action_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def log_action(admin_id, action_type, resource_type=None, resource_id=None, 
                   old_value=None, new_value=None, description=None,
                   ip_address=None, user_agent=None):
        """Log an admin action."""
        audit = AuditLog(
            admin_id=admin_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(audit)
        db.session.commit()
        return audit


class SystemSettings(db.Model):
    """System-wide settings model."""

    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    
    # Settings
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(20), default='string')
    
    # Metadata
    category = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SystemSettings {self.key}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'value_type': self.value_type,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
