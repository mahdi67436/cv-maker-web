"""
Resume Routes
=============
API endpoints for resume management.
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import limiter
import os
import uuid
from datetime import datetime

from models.resume import Resume, Experience, Education, Skill, Project, Certification
from models.template import ResumeTemplate
from models.user import UserActivity
from utils.auth_guard import APIResponse
from app import db

resume_bp = Blueprint('resume', __name__, url_prefix='/api/resumes')


@resume_bp.route('', methods=['GET'])
@jwt_required()
@limiter.limit('100 per hour')
def list_resumes():
    """List all resumes for current user."""
    try:
        user_id = get_jwt_identity()
        resumes = Resume.query.filter_by(
            user_id=user_id,
            is_archived=False
        ).order_by(Resume.updated_at.desc()).all()
        
        return APIResponse.success({
            'resumes': [r.to_dict() for r in resumes],
            'total': len(resumes)
        })
        
    except Exception as e:
        import logging
        logging.error(f"List resumes error: {e}")
        return APIResponse.error('Failed to list resumes', 500)


@resume_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit('50 per hour')
def create_resume():
    """Create a new resume."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        title = data.get('title', 'My Resume')
        template_id = data.get('template_id')
        template_name = data.get('template_name', 'modern')
        
        # Get user data
        user = db.session.get(user_id)
        if not user:
            return APIResponse.error('User not found', 404)
        
        # Create resume
        resume = Resume(
            user_id=user_id,
            title=title,
            template_id=template_id,
            template_name=template_name,
            full_name=user.name,
            email=user.email,
            phone=user.phone,
            address=user.address,
            city=user.city,
            country=user.country,
            linkedin=user.linkedin,
            github=user.github,
            portfolio=user.portfolio,
            website=user.website,
            avatar_url=user.avatar_url,
            summary=user.summary,
            content=data.get('content', {})
        )
        
        db.session.add(resume)
        db.session.commit()
        
        # Log activity
        UserActivity.log_activity(
            user_id,
            'resume_create',
            f'Resume "{title}" created',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return APIResponse.success({
            'resume': resume.to_dict()
        }, 'Resume created successfully', 201)
        
    except Exception as e:
        import logging
        logging.error(f"Create resume error: {e}")
        return APIResponse.error('Failed to create resume', 500)


@resume_bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """Get a specific resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        return APIResponse.success({
            'resume': resume.to_dict()
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get resume error: {e}")
        return APIResponse.error('Failed to get resume', 500)


@resume_bp.route('/<int:resume_id>', methods=['PUT'])
@jwt_required()
@limiter.limit('100 per hour')
def update_resume(resume_id):
    """Update a resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        # Update basic fields
        if 'title' in data:
            resume.title = data['title']
        
        if 'template_id' in data:
            resume.template_id = data['template_id']
        
        if 'template_name' in data:
            resume.template_name = data['template_name']
        
        if 'template_style' in data:
            resume.template_style = data['template_style']
        
        # Update personal info
        personal_fields = [
            'full_name', 'email', 'phone', 'address', 'city', 'country',
            'linkedin', 'github', 'portfolio', 'website', 'avatar_url', 'summary'
        ]
        
        for field in personal_fields:
            if field in data:
                setattr(resume, field, data[field])
        
        # Update content
        if 'content' in data:
            resume.content = data['content']
        
        if 'is_public' in data:
            resume.is_public = data['is_public']
        
        resume.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        UserActivity.log_activity(
            user_id,
            'resume_update',
            f'Resume "{resume.title}" updated',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return APIResponse.success({
            'resume': resume.to_dict()
        }, 'Resume updated successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Update resume error: {e}")
        return APIResponse.error('Failed to update resume', 500)


@resume_bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit('20 per hour')
def delete_resume(resume_id):
    """Delete a resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        title = resume.title
        db.session.delete(resume)
        db.session.commit()
        
        # Log activity
        UserActivity.log_activity(
            user_id,
            'resume_delete',
            f'Resume "{title}" deleted',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return APIResponse.success(message='Resume deleted successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Delete resume error: {e}")
        return APIResponse.error('Failed to delete resume', 500)


@resume_bp.route('/<int:resume_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_resume(resume_id):
    """Duplicate a resume."""
    try:
        user_id = get_jwt_identity()
        original = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not original:
            return APIResponse.error('Resume not found', 404)
        
        # Create new resume as copy
        new_resume = Resume(
            user_id=user_id,
            title=f"{original.title} (Copy)",
            template_id=original.template_id,
            template_name=original.template_name,
            template_style=original.template_style,
            full_name=original.full_name,
            email=original.email,
            phone=original.phone,
            address=original.address,
            city=original.city,
            country=original.country,
            linkedin=original.linkedin,
            github=original.github,
            portfolio=original.portfolio,
            website=original.website,
            avatar_url=original.avatar_url,
            summary=original.summary,
            content=original.content.copy() if original.content else {}
        )
        
        db.session.add(new_resume)
        db.session.flush()  # Get ID
        
        # Copy experiences
        for exp in original.experiences.all():
            new_exp = Experience(
                resume_id=new_resume.id,
                company=exp.company,
                position=exp.position,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                order=exp.order
            )
            db.session.add(new_exp)
        
        # Copy education
        for edu in original.education.all():
            new_edu = Education(
                resume_id=new_resume.id,
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                location=edu.location,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa,
                description=edu.description,
                order=edu.order
            )
            db.session.add(new_edu)
        
        # Copy skills
        for skill in original.skills.all():
            new_skill = Skill(
                resume_id=new_resume.id,
                name=skill.name,
                category=skill.category,
                level=skill.level,
                years_of_experience=skill.years_of_experience,
                order=skill.order
            )
            db.session.add(new_skill)
        
        # Copy projects
        for proj in original.projects.all():
            new_proj = Project(
                resume_id=new_resume.id,
                name=proj.name,
                description=proj.description,
                technologies=proj.technologies,
                link=proj.link,
                github_link=proj.github_link,
                start_date=proj.start_date,
                end_date=proj.end_date,
                order=proj.order
            )
            db.session.add(new_proj)
        
        # Copy certifications
        for cert in original.certifications.all():
            new_cert = Certification(
                resume_id=new_resume.id,
                name=cert.name,
                issuing_organization=cert.issuing_organization,
                issue_date=cert.issue_date,
                expiry_date=cert.expiry_date,
                credential_id=cert.credential_id,
                credential_url=cert.credential_url,
                order=cert.order
            )
            db.session.add(new_cert)
        
        db.session.commit()
        
        return APIResponse.success({
            'resume': new_resume.to_dict()
        }, 'Resume duplicated successfully', 201)
        
    except Exception as e:
        import logging
        logging.error(f"Duplicate resume error: {e}")
        return APIResponse.error('Failed to duplicate resume', 500)


@resume_bp.route('/<int:resume_id>/share', methods=['POST'])
@jwt_required()
def toggle_share(resume_id):
    """Toggle resume public sharing."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        resume.is_public = not resume.is_public
        
        if resume.is_public and not resume.share_token:
            resume.share_token = str(uuid.uuid4().hex)
        
        db.session.commit()
        
        return APIResponse.success({
            'is_public': resume.is_public,
            'share_url': f"/preview/{resume.slug}" if resume.is_public else None
        }, 'Sharing settings updated')
        
    except Exception as e:
        import logging
        logging.error(f"Toggle share error: {e}")
        return APIResponse.error('Failed to update sharing settings', 500)


@resume_bp.route('/<int:resume_id>/archive', methods=['POST'])
@jwt_required()
def archive_resume(resume_id):
    """Archive a resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        resume.is_archived = True
        db.session.commit()
        
        return APIResponse.success(message='Resume archived successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Archive resume error: {e}")
        return APIResponse.error('Failed to archive resume', 500)


# Experience endpoints
@resume_bp.route('/<int:resume_id>/experience', methods=['GET'])
@jwt_required()
def get_experiences(resume_id):
    """Get all experiences for a resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        experiences = resume.experiences.order_by(Experience.order).all()
        
        return APIResponse.success({
            'experiences': [e.to_dict() for e in experiences]
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get experiences error: {e}")
        return APIResponse.error('Failed to get experiences', 500)


@resume_bp.route('/<int:resume_id>/experience', methods=['POST'])
@jwt_required()
def add_experience(resume_id):
    """Add experience to resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        data = request.get_json()
        
        experience = Experience(
            resume_id=resume_id,
            company=data.get('company'),
            position=data.get('position'),
            location=data.get('location'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            is_current=data.get('is_current', False),
            description=data.get('description'),
            order=data.get('order', 0)
        )
        
        db.session.add(experience)
        db.session.commit()
        
        return APIResponse.success({
            'experience': experience.to_dict()
        }, 'Experience added successfully', 201)
        
    except Exception as e:
        import logging
        logging.error(f"Add experience error: {e}")
        return APIResponse.error('Failed to add experience', 500)


# Education endpoints
@resume_bp.route('/<int:resume_id>/education', methods=['GET'])
@jwt_required()
def get_education(resume_id):
    """Get all education for a resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        education = resume.education.order_by(Education.order).all()
        
        return APIResponse.success({
            'education': [e.to_dict() for e in education]
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get education error: {e}")
        return APIResponse.error('Failed to get education', 500)


@resume_bp.route('/<int:resume_id>/education', methods=['POST'])
@jwt_required()
def add_education(resume_id):
    """Add education to resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        data = request.get_json()
        
        education = Education(
            resume_id=resume_id,
            institution=data.get('institution'),
            degree=data.get('degree'),
            field_of_study=data.get('field_of_study'),
            location=data.get('location'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            gpa=data.get('gpa'),
            description=data.get('description'),
            order=data.get('order', 0)
        )
        
        db.session.add(education)
        db.session.commit()
        
        return APIResponse.success({
            'education': education.to_dict()
        }, 'Education added successfully', 201)
        
    except Exception as e:
        import logging
        logging.error(f"Add education error: {e}")
        return APIResponse.error('Failed to add education', 500)


# Skills endpoints
@resume_bp.route('/<int:resume_id>/skills', methods=['GET'])
@jwt_required()
def get_skills(resume_id):
    """Get all skills for a resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        skills = resume.skills.order_by(Skill.order).all()
        
        return APIResponse.success({
            'skills': [s.to_dict() for s in skills]
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get skills error: {e}")
        return APIResponse.error('Failed to get skills', 500)


@resume_bp.route('/<int:resume_id>/skills', methods=['POST'])
@jwt_required()
def add_skill(resume_id):
    """Add skill to resume."""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        
        if not resume:
            return APIResponse.error('Resume not found', 404)
        
        data = request.get_json()
        
        skill = Skill(
            resume_id=resume_id,
            name=data.get('name'),
            category=data.get('category'),
            level=data.get('level'),
            years_of_experience=data.get('years_of_experience'),
            order=data.get('order', 0)
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return APIResponse.success({
            'skill': skill.to_dict()
        }, 'Skill added successfully', 201)
        
    except Exception as e:
        import logging
        logging.error(f"Add skill error: {e}")
        return APIResponse.error('Failed to add skill', 500)


# Templates endpoints
@resume_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all available templates."""
    try:
        templates = ResumeTemplate.get_active_templates()
        
        return APIResponse.success({
            'templates': [t.to_dict() for t in templates]
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get templates error: {e}")
        return APIResponse.error('Failed to get templates', 500)
