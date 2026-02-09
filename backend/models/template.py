"""
Resume Template Model
======================
Database model for resume templates.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ResumeTemplate(db.Model):
    """Resume template model."""

    __tablename__ = 'resume_templates'

    id = db.Column(db.Integer, primary_key=True)
    
    # Template identification
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=True)  # modern, professional, creative, ats, dark
    
    # Template details
    description = db.Column(db.Text, nullable=True)
    preview_image = db.Column(db.String(500), nullable=True)
    thumbnail_image = db.Column(db.String(500), nullable=True)
    
    # Template structure
    template_html = db.Column(db.Text, nullable=True)
    template_css = db.Column(db.Text, nullable=True)
    template_config = db.Column(db.JSON, nullable=True)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    
    # Usage stats
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Customization options
    color_options = db.Column(db.JSON, nullable=True)
    font_options = db.Column(db.JSON, nullable=True)
    layout_options = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ResumeTemplate {self.name}>'

    def to_dict(self, include_template=False):
        """Convert template to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'category': self.category,
            'description': self.description,
            'preview_image': self.preview_image,
            'thumbnail_image': self.thumbnail_image,
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'is_default': self.is_default,
            'usage_count': self.usage_count,
            'color_options': self.color_options,
            'font_options': self.font_options,
            'layout_options': self.layout_options,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_template:
            data['template_html'] = self.template_html
            data['template_css'] = self.template_css
            data['template_config'] = self.template_config
        
        return data

    def increment_usage(self):
        """Increment usage counter."""
        self.usage_count += 1
        db.session.commit()

    @staticmethod
    def get_active_templates():
        """Get all active templates."""
        return ResumeTemplate.query.filter_by(is_active=True).order_by(ResumeTemplate.name).all()

    @staticmethod
    def get_default_template():
        """Get default template."""
        return ResumeTemplate.query.filter_by(is_default=True, is_active=True).first()


class AdminSettings(db.Model):
    """Admin settings model."""

    __tablename__ = 'admin_settings'

    id = db.Column(db.Integer, primary_key=True)
    
    # Settings
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(20), default='string')
    
    # Description
    category = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AdminSettings {self.key}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'value_type': self.value_type,
            'category': self.category,
            'description': self.description,
        }

    @staticmethod
    def get(key, default=None):
        """Get setting value."""
        setting = AdminSettings.query.filter_by(key=key).first()
        if setting:
            if setting.value_type == 'boolean':
                return setting.value.lower() in ('true', '1', 'yes')
            elif setting.value_type == 'integer':
                return int(setting.value)
            elif setting.value_type == 'json':
                import json
                return json.loads(setting.value) if setting.value else None
            return setting.value
        return default

    @staticmethod
    def set(key, value, value_type='string', category=None, description=None):
        """Set setting value."""
        setting = AdminSettings.query.filter_by(key=key).first()
        if not setting:
            setting = AdminSettings(key=key)
        
        setting.value = str(value) if value_type == 'string' else value
        setting.value_type = value_type
        setting.category = category
        setting.description = description
        db.session.add(setting)
        db.session.commit()
        return setting


class Analytics(db.Model):
    """Analytics model for tracking metrics."""

    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    
    # Metric data
    date = db.Column(db.Date, nullable=False, index=True)
    metric_type = db.Column(db.String(50), nullable=False)
    metric_value = db.Column(db.Integer, default=0)
    metric_data = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Analytics {self.date} - {self.metric_type}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'metric_data': self.metric_data,
        }

    @staticmethod
    def record_metric(date, metric_type, value, data=None):
        """Record a metric."""
        analytics = Analytics(
            date=date,
            metric_type=metric_type,
            metric_value=value,
            metric_data=data
        )
        db.session.add(analytics)
        db.session.commit()
        return analytics
