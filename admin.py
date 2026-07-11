from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, SentEmail, Attachment
from datetime import datetime, timedelta
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def format_file_size(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1048576:
        return f"{bytes / 1024:.1f} KB"
    elif bytes < 1073741824:
        return f"{bytes / 1048576:.1f} MB"
    else:
        return f"{bytes / 1073741824:.1f} GB"

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('routes.dashboard'))
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_emails = SentEmail.query.count()
    total_attachments = Attachment.query.count()
    
    total_storage = db.session.query(db.func.sum(Attachment.file_size)).scalar() or 0
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_emails = SentEmail.query.order_by(SentEmail.sent_at.desc()).limit(5).all()
    
    return render_template('dashboard/admin.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_emails=total_emails,
                         total_attachments=total_attachments,
                         total_storage=total_storage,
                         recent_users=recent_users,
                         recent_emails=recent_emails)

@admin_bp.route('/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('routes.dashboard'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('dashboard/admin_users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle')
@login_required
def toggle_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({'active': user.is_active})

@admin_bp.route('/users/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/users/<int:user_id>/details')
@login_required
def user_details(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    
    sent_emails = SentEmail.query.filter_by(sender_id=user.id, is_sent=True).count()
    total_attachments = Attachment.query.join(SentEmail).filter(SentEmail.sender_id == user.id).count()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'email_verified': user.email_verified,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'storage_used': user.storage_used,
        'max_storage': user.max_storage,
        'storage_percentage': user.get_storage_usage_percentage(),
        'sent_emails': sent_emails,
        'total_attachments': total_attachments
    })

@admin_bp.route('/storage-stats')
@login_required
def storage_stats():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    users = User.query.all()
    stats = []
    for user in users:
        stats.append({
            'username': user.username,
            'storage_used': user.storage_used,
            'max_storage': user.max_storage,
            'percentage': user.get_storage_usage_percentage()
        })
    
    return jsonify(stats)

@admin_bp.route('/activity-logs')
@login_required
def activity_logs():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('routes.dashboard'))
    
    days = request.args.get('days', 7, type=int)
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    emails = SentEmail.query.filter(SentEmail.sent_at >= cutoff).count()
    new_users = User.query.filter(User.created_at >= cutoff).count()
    
    return jsonify({
        'emails': emails,
        'new_users': new_users,
        'days': days
    })

@admin_bp.route('/emails')
@login_required
def admin_emails():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('routes.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    
    query = SentEmail.query.filter_by(is_sent=True)
    
    if search:
        query = query.filter(
            SentEmail.subject.contains(search) | 
            SentEmail.recipient.contains(search) |
            SentEmail.body.contains(search)
        )
    
    pagination = query.order_by(SentEmail.sent_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('dashboard/admin_emails.html', emails=pagination)

@admin_bp.route('/emails/<int:email_id>/delete', methods=['POST'])
@login_required
def admin_delete_email(email_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    email = SentEmail.query.get_or_404(email_id)
    
    for attachment in email.attachments:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
        user = User.query.get(email.sender_id)
        if user:
            user.storage_used -= attachment.file_size
    
    db.session.delete(email)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/attachments')
@login_required
def admin_attachments():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    attachments = Attachment.query.all()
    
    stats = {
        'total': len(attachments),
        'images': sum(1 for a in attachments if a.is_image),
        'videos': sum(1 for a in attachments if a.is_video),
        'audio': sum(1 for a in attachments if a.is_audio),
        'documents': sum(1 for a in attachments if a.is_document),
        'archives': sum(1 for a in attachments if a.is_archive),
        'code': sum(1 for a in attachments if a.is_code),
        'other': sum(1 for a in attachments if not any([a.is_image, a.is_video, a.is_audio, a.is_document, a.is_archive, a.is_code]))
    }
    
    total_size = sum(a.file_size for a in attachments)
    
    return jsonify({
        'stats': stats,
        'total_size': total_size,
        'total_size_formatted': format_file_size(total_size),
        'attachments': [{
            'id': a.id,
            'filename': a.original_filename,
            'size': a.file_size,
            'size_formatted': format_file_size(a.file_size),
            'type': a.file_type,
            'mime_type': a.mime_type,
            'email_id': a.email_id,
            'uploaded_at': a.uploaded_at.isoformat()
        } for a in attachments[:50]]
    })