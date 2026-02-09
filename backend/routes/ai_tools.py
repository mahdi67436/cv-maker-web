"""
AI Tools Routes
===============
API endpoints for AI-powered resume features.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import limiter
import re

from models.resume import Resume, Experience, Education, Skill
from models.template import ResumeTemplate
from services.ai_writer import AIWriter
from services.ats_score import ATSScorer
from utils.auth_guard import APIResponse
from app import db

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/generate', methods=['POST'])
@jwt_required()
@limiter.limit('10 per hour')
def generate_content():
    """Generate resume content using AI."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        section = data.get('section', '')
        context = data.get('context', {})
        job_description = data.get('job_description', '')
        
        ai_writer = AIWriter()
        
        if section == 'summary':
            result = ai_writer.generate_summary(
                name=context.get('name', ''),
                experience=context.get('experience', []),
                skills=context.get('skills', []),
                job_description=job_description
            )
        elif section == 'experience':
            result = ai_writer.generate_experience_description(
                company=context.get('company', ''),
                position=context.get('position', ''),
                achievements=context.get('achievements', [])
            )
        elif section == 'skills':
            result = ai_writer.suggest_skills(
                job_title=context.get('job_title', ''),
                industry=context.get('industry', '')
            )
        else:
            return APIResponse.error('Invalid section type', 400)
        
        if result['success']:
            return APIResponse.success({
                'generated_content': result['content'],
                'suggestions': result.get('suggestions', [])
            }, 'Content generated successfully')
        else:
            return APIResponse.error(result.get('error', 'Generation failed'), 400)
        
    except Exception as e:
        import logging
        logging.error(f"AI generate error: {e}")
        return APIResponse.error('AI generation failed', 500)


@ai_bp.route('/improve', methods=['POST'])
@jwt_required()
@limiter.limit('20 per hour')
def improve_content():
    """Improve existing resume content using AI."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        content = data.get('content', '')
        content_type = data.get('type', 'general')
        job_description = data.get('job_description', '')
        
        ai_writer = AIWriter()
        result = ai_writer.improve_content(
            content=content,
            content_type=content_type,
            job_description=job_description
        )
        
        if result['success']:
            return APIResponse.success({
                'improved_content': result['content'],
                'changes': result.get('changes', []),
                'score': result.get('score', 0)
            }, 'Content improved successfully')
        else:
            return APIResponse.error(result.get('error', 'Improvement failed'), 400)
        
    except Exception as e:
        import logging
        logging.error(f"AI improve error: {e}")
        return APIResponse.error('AI improvement failed', 500)


@ai_bp.route('/grammar', methods=['POST'])
@jwt_required()
@limiter.limit('30 per hour')
def check_grammar():
    """Check grammar and spelling."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        content = data.get('content', '')
        
        ai_writer = AIWriter()
        result = ai_writer.check_grammar(content)
        
        if result['success']:
            return APIResponse.success({
                'corrected_content': result['corrected'],
                'issues': result.get('issues', []),
                'score': result.get('score', 0)
            })
        else:
            return APIResponse.error(result.get('error', 'Grammar check failed'), 400)
        
    except Exception as e:
        import logging
        logging.error(f"Grammar check error: {e}")
        return APIResponse.error('Grammar check failed', 500)


@ai_bp.route('/ats-check', methods=['POST'])
@jwt_required()
@limiter.limit('20 per hour')
def check_ats():
    """Check ATS compatibility."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', '')
        
        if resume_id:
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            if not resume:
                return APIResponse.error('Resume not found', 404)
            
            ats_scorer = ATSScorer()
            result = ats_scorer.analyze_resume(resume, job_description)
        else:
            resume_data = data.get('resume_data', {})
            ats_scorer = ATSScorer()
            result = ats_scorer.analyze_resume_data(resume_data, job_description)
        
        if result['success']:
            # Update resume ATS score
            if resume_id and 'overall_score' in result:
                resume.ats_score = result['overall_score']
                resume.ats_keywords = result.get('keywords', [])
                db.session.commit()
            
            return APIResponse.success({
                'overall_score': result.get('overall_score', 0),
                'section_scores': result.get('section_scores', {}),
                'missing_keywords': result.get('missing_keywords', []),
                'suggestions': result.get('suggestions', []),
                'formatting_issues': result.get('formatting_issues', []),
                'keyword_analysis': result.get('keyword_analysis', {})
            }, 'ATS analysis completed')
        else:
            return APIResponse.error(result.get('error', 'ATS check failed'), 400)
        
    except Exception as e:
        import logging
        logging.error(f"ATS check error: {e}")
        return APIResponse.error('ATS check failed', 500)


@ai_bp.route('/suggestions', methods=['POST'])
@jwt_required()
@limiter.limit('30 per hour')
def get_suggestions():
    """Get AI-powered suggestions for resume improvement."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', '')
        
        if resume_id:
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            if not resume:
                return APIResponse.error('Resume not found', 404)
            
            # Collect resume data
            resume_data = resume.to_dict()
            experiences = [exp.to_dict() for exp in resume.experiences.all()]
            education = [edu.to_dict() for edu in resume.education.all()]
            skills = [skill.to_dict() for skill in resume.skills.all()]
        else:
            resume_data = data.get('resume_data', {})
            experiences = data.get('experiences', [])
            education = data.get('education', [])
            skills = data.get('skills', [])
        
        ai_writer = AIWriter()
        
        # Generate suggestions
        suggestions = {
            'summary': [],
            'experience': [],
            'skills': [],
            'education': [],
            'overall': []
        }
        
        # Overall suggestions
        if job_description:
            suggestions['overall'].append({
                'type': 'job_match',
                'message': 'Tailor your resume to the specific job description',
                'priority': 'high'
            })
        
        # Summary suggestions
        if not resume_data.get('summary'):
            suggestions['summary'].append({
                'type': 'missing',
                'message': 'Add a professional summary to stand out',
                'priority': 'high'
            })
        elif len(resume_data.get('summary', '')) < 100:
            suggestions['summary'].append({
                'type': 'length',
                'message': 'Consider expanding your professional summary',
                'priority': 'medium'
            })
        
        # Experience suggestions
        if len(experiences) == 0:
            suggestions['experience'].append({
                'type': 'missing',
                'message': 'Add work experience to showcase your background',
                'priority': 'high'
            })
        
        # Skills suggestions
        if len(skills) < 5:
            suggestions['skills'].append({
                'type': 'count',
                'message': 'Consider adding more relevant skills',
                'priority': 'medium'
            })
        
        return APIResponse.success({
            'suggestions': suggestions
        })
        
    except Exception as e:
        import logging
        logging.error(f"Suggestions error: {e}")
        return APIResponse.error('Failed to generate suggestions', 500)


@ai_bp.route('/job-titles', methods=['GET'])
@limiter.limit('50 per hour')
def suggest_job_titles():
    """Get suggested job titles based on skills and experience."""
    try:
        skills = request.args.getlist('skills')
        experience_years = request.args.get('experience_years', '0')
        
        ai_writer = AIWriter()
        result = ai_writer.suggest_job_titles(
            skills=skills,
            experience_years=int(experience_years)
        )
        
        if result['success']:
            return APIResponse.success({
                'job_titles': result.get('job_titles', [])
            })
        else:
            return APIResponse.error(result.get('error', 'Failed to suggest titles'), 400)
        
    except Exception as e:
        import logging
        logging.error(f"Job titles suggestion error: {e}")
        return APIResponse.error('Failed to suggest job titles', 500)


@ai_bp.route('/keywords', methods=['POST'])
@jwt_required()
@limiter.limit('20 per hour')
def extract_keywords():
    """Extract keywords from resume and job description."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        resume_data = data.get('resume_data', {})
        job_description = data.get('job_description', '')
        
        ats_scorer = ATSScorer()
        result = ats_scorer.extract_keywords(resume_data, job_description)
        
        if result['success']:
            return APIResponse.success({
                'resume_keywords': result.get('resume_keywords', []),
                'job_keywords': result.get('job_keywords', []),
                'matched_keywords': result.get('matched_keywords', []),
                'missing_keywords': result.get('missing_keywords', [])
            })
        else:
            return APIResponse.error(result.get('error', 'Keyword extraction failed'), 400)
        
    except Exception as e:
        import logging
        logging.error(f"Keyword extraction error: {e}")
        return APIResponse.error('Failed to extract keywords', 500)
