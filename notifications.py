from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import Notification
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

def create_notification(user_id, title, message, type='info', link=None):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        link=link
    )
    db.session.add(notification)
    db.session.commit()
    return notification

@notifications_bp.route('/')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id)\
                                     .order_by(Notification.created_at.desc()).limit(20).all()
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.type,
        'is_read': n.is_read,
        'link': n.link,
        'created_at': n.created_at.isoformat()
    } for n in notifications])

@notifications_bp.route('/unread-count')
@login_required
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

@notifications_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
                     .update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})

@notifications_bp.route('/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'success': True})