"""
Resume Model
============
Database models for resumes and related entities.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


class Resume(db.Model):
    """Main resume model."""

    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Resume identification
    title = db.Column(db.String(200), nullable=False, default='My Resume')
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    
    # Template settings
    template_id = db.Column(db.Integer, db.ForeignKey('resume_templates.id'), nullable=True)
    template_name = db.Column(db.String(50), default='modern')
    template_style = db.Column(db.JSON, nullable=True)
    
    # Personal info (embedded from user or custom)
    full_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    portfolio = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Professional summary
    summary = db.Column(db.Text, nullable=True)
    
    # Resume content stored as JSON for flexibility
    content = db.Column(db.JSON, nullable=True)
    
    # ATS and SEO
    ats_score = db.Column(db.Integer, default=0)
    ats_keywords = db.Column(db.JSON, nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    
    # Sharing and visibility
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    share_token = db.Column(db.String(100), unique=True, nullable=True, index=True)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Export tracking
    pdf_downloads = db.Column(db.Integer, default=0, nullable=False)
    docx_downloads = db.Column(db.Integer, default=0, nullable=False)
    png_downloads = db.Column(db.Integer, default=0, nullable=False)
    
    # Status
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiences = db.relationship('Experience', backref='resume', lazy='dynamic', cascade='all, delete-orphan')
    education = db.relationship('Education', backref='resume', lazy='dynamic', cascade='all, delete-orphan')
    skills = db.relationship('Skill', backref='resume', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='resume', lazy='dynamic', cascade='all, delete-orphan')
    certifications = db.relationship('Certification', backref='resume', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Resume {self.title}>'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug:
            self.slug = self._generate_slug()
        if not self.share_token:
            self.share_token = self._generate_share_token()

    def _generate_slug(self):
        """Generate URL-friendly slug from title."""
        base = self.title.lower().replace(' ', '-')
        return f"{base}-{uuid.uuid4().hex[:8]}"

    def _generate_share_token(self):
        """Generate unique share token."""
        return uuid.uuid4().hex

    def to_dict(self, include_content=True):
        """Convert resume to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'slug': self.slug,
            'template_id': self.template_id,
            'template_name': self.template_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'linkedin': self.linkedin,
            'github': self.github,
            'portfolio': self.portfolio,
            'website': self.website,
            'avatar_url': self.avatar_url,
            'summary': self.summary,
            'is_public': self.is_public,
            'share_token': self.share_token,
            'view_count': self.view_count,
            'pdf_downloads': self.pdf_downloads,
            'docx_downloads': self.docx_downloads,
            'png_downloads': self.png_downloads,
            'ats_score': self.ats_score,
            'is_complete': self.is_complete,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_content:
            data['content'] = self.content or {}
            data['experiences'] = [exp.to_dict() for exp in self.experiences.all()]
            data['education'] = [edu.to_dict() for edu in self.education.all()]
            data['skills'] = [skill.to_dict() for skill in self.skills.all()]
            data['projects'] = [proj.to_dict() for proj in self.projects.all()]
            data['certifications'] = [cert.to_dict() for cert in self.certifications.all()]
        
        return data

    def increment_download(self, format_type):
        """Increment download counter."""
        if format_type == 'pdf':
            self.pdf_downloads += 1
        elif format_type == 'docx':
            self.docx_downloads += 1
        elif format_type == 'png':
            self.png_downloads += 1
        db.session.commit()

    def increment_view(self):
        """Increment view counter."""
        self.view_count += 1
        db.session.commit()

    def calculate_completeness(self):
        """Calculate resume completeness percentage."""
        fields = [
            self.full_name,
            self.email,
            self.summary,
        ]
        
        # Count filled sections
        filled = sum(1 for f in fields if f)
        
        # Add relationships
        filled += min(1, self.experiences.count())
        filled += min(1, self.education.count())
        filled += min(1, self.skills.count())
        
        total = 5
        return int((filled / total) * 100)


class Experience(db.Model):
    """Work experience model."""

    __tablename__ = 'experiences'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    
    # Experience details
    company = db.Column(db.String(200), nullable=True)
    position = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True, default='Present')
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    
    # AI-generated content
    ai_enhanced = db.Column(db.Boolean, default=False)
    
    # Order
    order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Experience {self.position} at {self.company}>'

    def to_dict(self):
        """Convert experience to dictionary."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'company': self.company,
            'position': self.position,
            'location': self.location,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_current': self.is_current,
            'description': self.description,
            'ai_enhanced': self.ai_enhanced,
            'order': self.order,
        }


class Education(db.Model):
    """Education model."""

    __tablename__ = 'education'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    
    # Education details
    institution = db.Column(db.String(200), nullable=True)
    degree = db.Column(db.String(200), nullable=True)
    field_of_study = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True)
    gpa = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Order
    order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Education {self.degree} at {self.institution}>'

    def to_dict(self):
        """Convert education to dictionary."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'institution': self.institution,
            'degree': self.degree,
            'field_of_study': self.field_of_study,
            'location': self.location,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'gpa': self.gpa,
            'description': self.description,
            'order': self.order,
        }


class Skill(db.Model):
    """Skills model."""

    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    
    # Skill details
    name = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    level = db.Column(db.String(20), nullable=True)  # beginner, intermediate, advanced, expert
    years_of_experience = db.Column(db.Float, nullable=True)
    
    # Order
    order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Skill {self.name}>'

    def to_dict(self):
        """Convert skill to dictionary."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'name': self.name,
            'category': self.category,
            'level': self.level,
            'years_of_experience': self.years_of_experience,
            'order': self.order,
        }


class Project(db.Model):
    """Project model."""

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    
    # Project details
    name = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    technologies = db.Column(db.String(500), nullable=True)
    link = db.Column(db.String(500), nullable=True)
    github_link = db.Column(db.String(500), nullable=True)
    
    # Dates
    start_date = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True)
    
    # Order
    order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.name}>'

    def to_dict(self):
        """Convert project to dictionary."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'name': self.name,
            'description': self.description,
            'technologies': self.technologies,
            'link': self.link,
            'github_link': self.github_link,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'order': self.order,
        }


class Certification(db.Model):
    """Certification model."""

    __tablename__ = 'certifications'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    
    # Certification details
    name = db.Column(db.String(200), nullable=True)
    issuing_organization = db.Column(db.String(200), nullable=True)
    issue_date = db.Column(db.String(50), nullable=True)
    expiry_date = db.Column(db.String(50), nullable=True)
    credential_id = db.Column(db.String(100), nullable=True)
    credential_url = db.Column(db.String(500), nullable=True)
    
    # Order
    order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Certification {self.name}>'

    def to_dict(self):
        """Convert certification to dictionary."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'name': self.name,
            'issuing_organization': self.issuing_organization,
            'issue_date': self.issue_date,
            'expiry_date': self.expiry_date,
            'credential_id': self.credential_id,
            'credential_url': self.credential_url,
            'order': self.order,
        }
