"""
Admin Routes
============
API endpoints for admin panel functionality.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import limiter
from datetime import datetime, timedelta
from sqlalchemy import func

from models.user import User, UserActivity
from models.resume import Resume, Experience, Education, Skill
from models.template import ResumeTemplate, AdminSettings, Analytics
from models.admin import Admin, AuditLog, SystemSettings
from utils.auth_guard import admin_required, APIResponse
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required()
@limiter.limit('100 per hour')
def dashboard():
    """Get admin dashboard statistics."""
    try:
        user_id = get_jwt_identity()
        
        # Get counts
        total_users = User.query.count()
        total_resumes = Resume.query.count()
        total_downloads = db.session.query(
            func.sum(Resume.pdf_downloads + Resume.docx_downloads + Resume.png_downloads)
        ).scalar() or 0
        
        # Get today's stats
        today = datetime.utcnow().date()
        new_users_today = User.query.filter(
            func.date(User.created_at) == today
        ).count()
        
        new_resumes_today = Resume.query.filter(
            func.date(Resume.created_at) == today
        ).count()
        
        # Get recent activities
        recent_activities = UserActivity.query.order_by(
            UserActivity.created_at.desc()
        ).limit(20).all()
        
        # Get user growth data (last 30 days)
        growth_data = []
        for i in range(30):
            date = today - timedelta(days=i)
            count = User.query.filter(func.date(User.created_at) == date).count()
            growth_data.insert(0, {
                'date': date.isoformat(),
                'count': count
            })
        
        # Get top templates
        top_templates = ResumeTemplate.query.order_by(
            ResumeTemplate.usage_count.desc()
        ).limit(5).all()
        
        return APIResponse.success({
            'stats': {
                'total_users': total_users,
                'total_resumes': total_resumes,
                'total_downloads': total_downloads,
                'new_users_today': new_users_today,
                'new_resumes_today': new_resumes_today
            },
            'recent_activities': [a.to_dict() for a in recent_activities],
            'growth_data': growth_data,
            'top_templates': [t.to_dict() for t in top_templates]
        })
        
    except Exception as e:
        import logging
        logging.error(f"Admin dashboard error: {e}")
        return APIResponse.error('Failed to load dashboard', 500)


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
@limiter.limit('50 per hour')
def list_users():
    """List all users with pagination and filters."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        query = User.query
        
        # Apply search
        if search:
            query = query.filter(
                (User.email.contains(search)) |
                (User.name.contains(search))
            )
        
        # Apply status filter
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        elif status == 'admin':
            query = query.filter_by(is_admin=True)
        
        # Apply sorting
        if sort_order == 'desc':
            query = query.order_by(getattr(User, sort_by).desc())
        else:
            query = query.order_by(getattr(User, sort_by).asc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return APIResponse.success({
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        import logging
        logging.error(f"List users error: {e}")
        return APIResponse.error('Failed to list users', 500)


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_user(user_id):
    """Get user details."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return APIResponse.error('User not found', 404)
        
        # Get user resumes
        resumes = Resume.query.filter_by(user_id=user_id).all()
        
        # Get user activities
        activities = UserActivity.query.filter_by(
            user_id=user_id
        ).order_by(UserActivity.created_at.desc()).limit(50).all()
        
        return APIResponse.success({
            'user': user.to_dict(include_sensitive=True),
            'resumes': [r.to_dict() for r in resumes],
            'activities': [a.to_dict() for a in activities]
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get user error: {e}")
        return APIResponse.error('Failed to get user', 500)


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@admin_required()
def toggle_user_status(user_id):
    """Toggle user active status."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return APIResponse.error('User not found', 404)
        
        # Prevent self-deactivation
        current_user_id = get_jwt_identity()
        if user_id == current_user_id:
            return APIResponse.error('Cannot change your own status', 400)
        
        user.is_active = not user.is_active
        db.session.commit()
        
        # Log admin action
        admin_user = User.query.get(current_user_id)
        AuditLog.log_action(
            admin_id=admin_user.id if hasattr(admin_user, 'id') else None,
            action_type='user_status_change',
            resource_type='user',
            resource_id=user_id,
            old_value=str(not user.is_active),
            new_value=str(user.is_active),
            description=f"User status changed to {user.is_active}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return APIResponse.success({
            'is_active': user.is_active
        }, f'User {"activated" if user.is_active else "deactivated"}')
        
    except Exception as e:
        import logging
        logging.error(f"Toggle user status error: {e}")
        return APIResponse.error('Failed to update user status', 500)


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_user(user_id):
    """Delete a user and all their data."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return APIResponse.error('User not found', 404)
        
        # Prevent self-deletion
        current_user_id = get_jwt_identity()
        if user_id == current_user_id:
            return APIResponse.error('Cannot delete your own account', 400)
        
        user_name = user.email
        
        # Delete all user data
        db.session.delete(user)
        db.session.commit()
        
        # Log admin action
        admin_user = User.query.get(current_user_id)
        AuditLog.log_action(
            admin_id=admin_user.id if hasattr(admin_user, 'id') else None,
            action_type='user_delete',
            resource_type='user',
            resource_id=user_id,
            description=f"User {user_name} deleted",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return APIResponse.success(message='User deleted successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Delete user error: {e}")
        return APIResponse.error('Failed to delete user', 500)


@admin_bp.route('/resumes', methods=['GET'])
@jwt_required()
@admin_required()
def list_all_resumes():
    """List all resumes with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        query = Resume.query
        
        if search:
            query = query.filter(
                (Resume.title.contains(search)) |
                (Resume.full_name.contains(search))
            )
        
        if status == 'public':
            query = query.filter_by(is_public=True)
        elif status == 'private':
            query = query.filter_by(is_public=False)
        
        pagination = query.order_by(Resume.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return APIResponse.success({
            'resumes': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        import logging
        logging.error(f"List all resumes error: {e}")
        return APIResponse.error('Failed to list resumes', 500)


@admin_bp.route('/templates', methods=['GET'])
@jwt_required()
@admin_required()
def list_templates():
    """List all resume templates."""
    try:
        templates = ResumeTemplate.query.order_by(ResumeTemplate.name).all()
        
        return APIResponse.success({
            'templates': [t.to_dict(include_template=False) for t in templates]
        })
        
    except Exception as e:
        import logging
        logging.error(f"List templates error: {e}")
        return APIResponse.error('Failed to list templates', 500)


@admin_bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_template(template_id):
    """Update template settings."""
    try:
        template = ResumeTemplate.query.get(template_id)
        
        if not template:
            return APIResponse.error('Template not found', 404)
        
        data = request.get_json()
        
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        if 'is_premium' in data:
            template.is_premium = data['is_premium']
        
        if 'is_default' in data:
            template.is_default = data['is_default']
        
        if 'color_options' in data:
            template.color_options = data['color_options']
        
        if 'font_options' in data:
            template.font_options = data['font_options']
        
        if 'layout_options' in data:
            template.layout_options = data['layout_options']
        
        db.session.commit()
        
        return APIResponse.success({
            'template': template.to_dict()
        }, 'Template updated successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Update template error: {e}")
        return APIResponse.error('Failed to update template', 500)


@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
@admin_required()
def get_settings():
    """Get admin settings."""
    try:
        settings = AdminSettings.query.all()
        
        return APIResponse.success({
            'settings': {s.key: s.to_dict() for s in settings}
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get settings error: {e}")
        return APIResponse.error('Failed to get settings', 500)


@admin_bp.route('/settings', methods=['PUT'])
@jwt_required()
@admin_required()
def update_settings():
    """Update admin settings."""
    try:
        data = request.get_json()
        
        if not data:
            return APIResponse.error('No data provided', 400)
        
        for key, value in data.items():
            AdminSettings.set(key, value)
        
        return APIResponse.success(message='Settings updated successfully')
        
    except Exception as e:
        import logging
        logging.error(f"Update settings error: {e}")
        return APIResponse.error('Failed to update settings', 500)


@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required()
def get_analytics():
    """Get analytics data."""
    try:
        days = request.args.get('days', 30, type=int)
        metric_type = request.args.get('metric_type', 'downloads')
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        analytics = Analytics.query.filter(
            Analytics.date >= start_date,
            Analytics.date <= end_date,
            Analytics.metric_type == metric_type
        ).order_by(Analytics.date).all()
        
        return APIResponse.success({
            'analytics': [a.to_dict() for a in analytics]
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get analytics error: {e}")
        return APIResponse.error('Failed to get analytics', 500)


@admin_bp.route('/audit-log', methods=['GET'])
@jwt_required()
@admin_required()
def get_audit_log():
    """Get audit log."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_type = request.args.get('action_type', '')
        
        query = AuditLog.query
        
        if action_type:
            query = query.filter_by(action_type=action_type)
        
        pagination = query.order_by(AuditLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return APIResponse.success({
            'audit_logs': [a.to_dict() for a in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get audit log error: {e}")
        return APIResponse.error('Failed to get audit log', 500)


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required()
def get_stats():
    """Get detailed statistics."""
    try:
        # Downloads by format
        downloads = {
            'pdf': db.session.query(func.sum(Resume.pdf_downloads)).scalar() or 0,
            'docx': db.session.query(func.sum(Resume.docx_downloads)).scalar() or 0,
            'png': db.session.query(func.sum(Resume.png_downloads)).scalar() or 0
        }
        
        # Users by status
        users_active = User.query.filter_by(is_active=True).count()
        users_inactive = User.query.filter_by(is_active=False).count()
        users_admin = User.query.filter_by(is_admin=True).count()
        
        # Resumes by template
        templates = Resume.query.with_entities(
            Resume.template_name, func.count(Resume.id)
        ).group_by(Resume.template_name).all()
        
        template_usage = {t[0] or 'unknown': t[1] for t in templates}
        
        # Activity by day (last 7 days)
        activity_data = []
        for i in range(7):
            date = datetime.utcnow().date() - timedelta(days=6-i)
            count = UserActivity.query.filter(
                func.date(UserActivity.created_at) == date
            ).count()
            activity_data.append({
                'date': date.isoformat(),
                'count': count
            })
        
        return APIResponse.success({
            'downloads': downloads,
            'users': {
                'active': users_active,
                'inactive': users_inactive,
                'admin': users_admin,
                'total': users_active + users_inactive
            },
            'template_usage': template_usage,
            'activity_data': activity_data
        })
        
    except Exception as e:
        import logging
        logging.error(f"Get stats error: {e}")
        return APIResponse.error('Failed to get statistics', 500)
