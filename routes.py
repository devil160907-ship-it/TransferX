from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, SentEmail, Attachment, Draft, Notification
from email_service import send_email_sent_notification, send_contact_email
from notifications import create_notification
from config import Config
import os
import json
import traceback
import mimetypes
from datetime import datetime
import secrets

routes_bp = Blueprint('routes', __name__)

def get_file_category(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'tiff'}
    video_exts = {'mp4', 'avi', 'mkv', 'mov', 'webm', 'wmv', 'mpeg'}
    audio_exts = {'mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a'}
    document_exts = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'rtf', 'odt', 'ods'}
    archive_exts = {'zip', 'rar', '7z', 'tar', 'gz'}
    code_exts = {'html', 'css', 'js', 'json', 'xml', 'py', 'java', 'c', 'cpp', 'cs', 'php', 'go', 'rs', 'sql', 'md'}
    
    if ext in image_exts:
        return 'image'
    elif ext in video_exts:
        return 'video'
    elif ext in audio_exts:
        return 'audio'
    elif ext in document_exts:
        return 'document'
    elif ext in archive_exts:
        return 'archive'
    elif ext in code_exts:
        return 'code'
    else:
        return 'other'

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def format_file_size(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1048576:
        return f"{bytes / 1024:.1f} KB"
    elif bytes < 1073741824:
        return f"{bytes / 1048576:.1f} MB"
    else:
        return f"{bytes / 1073741824:.1f} GB"

@routes_bp.route('/')
def home():
    return render_template('pages.html')

@routes_bp.route('/about')
def about():
    return render_template('pages.html', page='about')

@routes_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            
            if not all([name, email, subject, message]):
                return jsonify({'success': False, 'error': 'All fields are required.'}), 400
            
            import re
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, email):
                return jsonify({'success': False, 'error': 'Invalid email address.'}), 400
            
            success = send_contact_email(name, email, subject, message)
            
            if success:
                return jsonify({'success': True, 'message': 'Your message has been sent successfully!'})
            else:
                return jsonify({'success': False, 'error': 'Failed to send message. Please try again.'}), 500
                
        except Exception:
            traceback.print_exc()
            return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500
    
    return render_template('pages.html', page='contact')

@routes_bp.route('/privacy')
def privacy():
    return render_template('pages.html', page='privacy')

@routes_bp.route('/terms')
def terms():
    return render_template('pages.html', page='terms')

@routes_bp.route('/public/email/<token>')
def public_email_view(token):
    email = SentEmail.query.filter_by(public_token=token, is_sent=True).first_or_404()
    attachments = Attachment.query.filter_by(email_id=email.id).all()
    sender = User.query.get(email.sender_id)
    return render_template('public/email_view.html', email=email, attachments=attachments, sender=sender)

@routes_bp.route('/dashboard')
@login_required
def dashboard():
    total_emails = SentEmail.query.filter_by(sender_id=current_user.id, is_sent=True).count()
    total_drafts = Draft.query.filter_by(user_id=current_user.id).count()
    total_attachments = Attachment.query.join(SentEmail).filter(SentEmail.sender_id == current_user.id).count()
    
    recent_emails = SentEmail.query.filter_by(sender_id=current_user.id, is_sent=True)\
                                 .order_by(SentEmail.sent_at.desc()).limit(5).all()
    
    storage_percentage = current_user.get_storage_usage_percentage()
    unread_notifications_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('dashboard/dashboard.html',
                         total_emails=total_emails,
                         total_drafts=total_drafts,
                         total_attachments=total_attachments,
                         recent_emails=recent_emails,
                         storage_percentage=storage_percentage,
                         unread_notifications_count=unread_notifications_count)

@routes_bp.route('/notifications')
@login_required
def notifications_page():
    notifications = Notification.query.filter_by(user_id=current_user.id)\
                                     .order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('dashboard/notifications_page.html', 
                         notifications=notifications,
                         unread_count=unread_count)

@routes_bp.route('/dashboard/compose', methods=['GET', 'POST'])
@login_required
def compose():
    if request.method == 'POST':
        action = request.form.get('action', 'send')
        recipient = request.form.get('recipient')
        cc = request.form.get('cc')
        bcc = request.form.get('bcc')
        subject = request.form.get('subject', 'No Subject')
        body = request.form.get('body')
        
        if action == 'save_draft':
            draft = Draft(
                user_id=current_user.id,
                recipient=recipient,
                cc=cc,
                bcc=bcc,
                subject=subject,
                body=body
            )
            db.session.add(draft)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Draft saved successfully!'})
            
            flash('Draft saved successfully!', 'success')
            return redirect(url_for('routes.drafts'))
        
        elif action == 'send':
            if not recipient:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Please enter at least one recipient.'})
                flash('Please enter at least one recipient.', 'error')
                return render_template('dashboard/compose.html')
            
            email = SentEmail(
                sender_id=current_user.id,
                recipient=recipient,
                cc=cc,
                bcc=bcc,
                subject=subject,
                body=body,
                is_sent=True
            )
            email.generate_public_token()
            db.session.add(email)
            db.session.flush()
            
            uploaded_files = request.files.getlist('attachments')
            attachment_list = []
            
            for file in uploaded_files:
                if file and file.filename:
                    if not is_allowed_file(file.filename):
                        continue
                    
                    original_filename = secure_filename(file.filename)
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
                    unique_filename = f"{timestamp}_{original_filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    try:
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        file.save(file_path)
                        
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            file_category = get_file_category(original_filename)
                            mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
                            
                            attachment = Attachment(
                                email_id=email.id,
                                filename=unique_filename,
                                original_filename=original_filename,
                                file_path=file_path,
                                file_size=file_size,
                                file_type=file_category,
                                mime_type=mime_type,
                                is_image=file_category == 'image',
                                is_video=file_category == 'video',
                                is_audio=file_category == 'audio',
                                is_document=file_category == 'document',
                                is_archive=file_category == 'archive',
                                is_code=file_category == 'code'
                            )
                            db.session.add(attachment)
                            current_user.storage_used += file_size
                            
                            attachment_list.append({
                                'file_path': file_path,
                                'filename': original_filename,
                                'mime_type': mime_type
                            })
                    except Exception:
                        traceback.print_exc()
                        continue
            
            db.session.commit()
            
            create_notification(
                current_user.id,
                'Email Sent',
                f'Your email "{subject}" has been sent successfully.',
                'success',
                f'/dashboard/email/{email.id}'
            )
            
            try:
                recipient_list = [r.strip() for r in recipient.split(',') if r.strip()]
                for recipient_email in recipient_list:
                    send_email_sent_notification(
                        recipient_email,
                        current_user.username,
                        subject,
                        email.id,
                        current_user.email,
                        body=body,
                        attachments=attachment_list,
                        public_token=email.public_token
                    )
            except Exception:
                traceback.print_exc()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Email sent successfully!',
                    'redirect': url_for('routes.sent_details', email_id=email.id)
                })
            
            flash('Email sent successfully!', 'success')
            return redirect(url_for('routes.sent_details', email_id=email.id))
    
    return render_template('dashboard/compose.html')

@routes_bp.route('/dashboard/sent')
@login_required
def sent():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    
    query = SentEmail.query.filter_by(sender_id=current_user.id, is_sent=True)
    
    if search:
        query = query.filter(
            SentEmail.subject.contains(search) | 
            SentEmail.recipient.contains(search) |
            SentEmail.body.contains(search)
        )
    
    pagination = query.order_by(SentEmail.sent_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('dashboard/sent.html', emails=pagination)

@routes_bp.route('/dashboard/email/<int:email_id>')
@login_required
def sent_details(email_id):
    email = SentEmail.query.filter_by(id=email_id, sender_id=current_user.id).first_or_404()
    attachments = Attachment.query.filter_by(email_id=email_id).all()
    public_url = url_for('routes.public_email_view', token=email.public_token, _external=True) if email.public_token else None
    return render_template('dashboard/email_details.html', email=email, attachments=attachments, public_url=public_url)

@routes_bp.route('/dashboard/delete/<int:email_id>', methods=['POST'])
@login_required
def delete_email(email_id):
    email = SentEmail.query.filter_by(id=email_id, sender_id=current_user.id).first_or_404()
    
    for attachment in email.attachments:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
        current_user.storage_used -= attachment.file_size
    
    db.session.delete(email)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Email deleted successfully.', 'success')
    return redirect(url_for('routes.sent'))

@routes_bp.route('/dashboard/attachment/<int:attachment_id>')
@login_required
def view_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    email = SentEmail.query.get(attachment.email_id)
    
    if email.sender_id != current_user.id:
        abort(403)
    
    if not os.path.exists(attachment.file_path):
        abort(404)
    
    return send_file(
        attachment.file_path, 
        download_name=attachment.original_filename,
        as_attachment=False
    )

@routes_bp.route('/dashboard/download/<int:attachment_id>')
@login_required
def download_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    email = SentEmail.query.get(attachment.email_id)
    
    if email.sender_id != current_user.id:
        abort(403)
    
    if not os.path.exists(attachment.file_path):
        abort(404)
    
    return send_file(
        attachment.file_path, 
        download_name=attachment.original_filename,
        as_attachment=True
    )

@routes_bp.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if full_name:
            current_user.full_name = full_name
        
        if current_password and new_password:
            if not current_user.check_password(current_password):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Current password is incorrect.'})
                flash('Current password is incorrect.', 'error')
                return render_template('dashboard/profile.html')
            
            if len(new_password) < 8:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'New password must be at least 8 characters.'})
                flash('New password must be at least 8 characters.', 'error')
                return render_template('dashboard/profile.html')
            
            if new_password != confirm_password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Passwords do not match.'})
                flash('Passwords do not match.', 'error')
                return render_template('dashboard/profile.html')
            
            current_user.set_password(new_password)
            create_notification(
                current_user.id,
                'Password Changed',
                'Your password has been updated successfully.',
                'success'
            )
            flash('Password updated successfully.', 'success')
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Profile updated successfully!'})
        
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('routes.profile'))
    
    return render_template('dashboard/profile.html')

@routes_bp.route('/dashboard/search')
@login_required
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('routes.sent'))
    
    emails = SentEmail.query.filter(
        SentEmail.sender_id == current_user.id,
        SentEmail.is_sent == True,
        (SentEmail.subject.contains(query) | 
         SentEmail.recipient.contains(query) |
         SentEmail.body.contains(query))
    ).order_by(SentEmail.sent_at.desc()).all()
    
    return render_template('dashboard/search_results.html', emails=emails, query=query)

@routes_bp.route('/dashboard/drafts')
@login_required
def drafts():
    drafts = Draft.query.filter_by(user_id=current_user.id).order_by(Draft.updated_at.desc()).all()
    return render_template('dashboard/drafts.html', drafts=drafts)

@routes_bp.route('/dashboard/draft/<int:draft_id>', methods=['GET', 'POST'])
@login_required
def draft_details(draft_id):
    draft = Draft.query.filter_by(id=draft_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'delete':
            db.session.delete(draft)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            
            flash('Draft deleted successfully.', 'success')
            return redirect(url_for('routes.drafts'))
        
        elif action == 'edit':
            recipient = request.form.get('recipient')
            cc = request.form.get('cc')
            bcc = request.form.get('bcc')
            subject = request.form.get('subject')
            body = request.form.get('body')
            
            if not recipient or not subject or not body:
                flash('Please fill in all required fields.', 'error')
                return render_template('dashboard/draft_details.html', draft=draft)
            
            draft.recipient = recipient
            draft.cc = cc
            draft.bcc = bcc
            draft.subject = subject
            draft.body = body
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Draft updated successfully!'})
            
            flash('Draft updated successfully.', 'success')
            return redirect(url_for('routes.drafts'))
        
        elif action == 'send':
            if not draft.recipient:
                flash('Please add at least one recipient before sending.', 'error')
                return render_template('dashboard/draft_details.html', draft=draft)
            
            email = SentEmail(
                sender_id=current_user.id,
                recipient=draft.recipient,
                cc=draft.cc,
                bcc=draft.bcc,
                subject=draft.subject,
                body=draft.body,
                is_sent=True
            )
            email.generate_public_token()
            db.session.add(email)
            db.session.commit()
            
            db.session.delete(draft)
            db.session.commit()
            
            create_notification(
                current_user.id,
                'Email Sent from Draft',
                f'Your draft "{draft.subject}" has been sent successfully.',
                'success',
                f'/dashboard/email/{email.id}'
            )
            
            try:
                recipient_list = [r.strip() for r in draft.recipient.split(',') if r.strip()]
                for recipient_email in recipient_list:
                    send_email_sent_notification(
                        recipient_email,
                        current_user.username,
                        draft.subject,
                        email.id,
                        current_user.email,
                        body=draft.body,
                        attachments=[],
                        public_token=email.public_token
                    )
            except Exception:
                traceback.print_exc()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Draft sent successfully!',
                    'redirect': url_for('routes.sent_details', email_id=email.id)
                })
            
            flash('Draft sent successfully!', 'success')
            return redirect(url_for('routes.sent_details', email_id=email.id))
    
    return render_template('dashboard/draft_details.html', draft=draft)

@routes_bp.route('/dashboard/drafts/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_drafts():
    draft_ids = request.form.get('draft_ids', '')
    if not draft_ids:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'No drafts selected.'})
        flash('No drafts selected.', 'error')
        return redirect(url_for('routes.drafts'))
    
    ids = [int(id) for id in draft_ids.split(',') if id.isdigit()]
    deleted_count = 0
    
    for draft_id in ids:
        draft = Draft.query.filter_by(id=draft_id, user_id=current_user.id).first()
        if draft:
            db.session.delete(draft)
            deleted_count += 1
    
    db.session.commit()
    
    create_notification(
        current_user.id,
        'Bulk Delete Drafts',
        f'{deleted_count} draft(s) have been deleted.',
        'info'
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'deleted': deleted_count})
    
    flash(f'{deleted_count} draft(s) deleted successfully.', 'success')
    return redirect(url_for('routes.drafts'))

@routes_bp.route('/dashboard/storage')
@login_required
def storage():
    total_used = current_user.storage_used
    total_max = current_user.max_storage
    percentage = current_user.get_storage_usage_percentage()
    
    return jsonify({
        'used': total_used,
        'max': total_max,
        'percentage': percentage,
        'used_formatted': format_file_size(total_used),
        'max_formatted': format_file_size(total_max)
    })

@routes_bp.route('/dashboard/preview/<int:attachment_id>')
@login_required
def preview_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    email = SentEmail.query.get(attachment.email_id)
    
    if email.sender_id != current_user.id:
        abort(403)
    
    if not os.path.exists(attachment.file_path):
        abort(404)
    
    content_type = attachment.mime_type or 'application/octet-stream'
    return send_file(
        attachment.file_path,
        mimetype=content_type,
        download_name=attachment.original_filename,
        as_attachment=False
    )

@routes_bp.route('/dashboard/attachment-info/<int:attachment_id>')
@login_required
def attachment_info(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    email = SentEmail.query.get(attachment.email_id)
    
    if email.sender_id != current_user.id:
        abort(403)
    
    return jsonify({
        'id': attachment.id,
        'filename': attachment.original_filename,
        'size': attachment.file_size,
        'size_formatted': format_file_size(attachment.file_size),
        'type': attachment.file_type,
        'mime_type': attachment.mime_type,
        'is_image': attachment.is_image,
        'is_video': attachment.is_video,
        'is_audio': attachment.is_audio,
        'uploaded_at': attachment.uploaded_at.isoformat()
    })

@routes_bp.route('/dashboard/email/<int:email_id>/resend')
@login_required
def resend_email(email_id):
    email = SentEmail.query.filter_by(id=email_id, sender_id=current_user.id).first_or_404()
    
    attachments = Attachment.query.filter_by(email_id=email_id).all()
    attachment_list = []
    
    for attachment in attachments:
        if os.path.exists(attachment.file_path):
            attachment_list.append({
                'file_path': attachment.file_path,
                'filename': attachment.original_filename,
                'mime_type': attachment.mime_type
            })
    
    try:
        recipient_list = [r.strip() for r in email.recipient.split(',') if r.strip()]
        for recipient_email in recipient_list:
            send_email_sent_notification(
                recipient_email,
                current_user.username,
                email.subject,
                email.id,
                current_user.email,
                body=email.body,
                attachments=attachment_list,
                public_token=email.public_token
            )
        
        create_notification(
            current_user.id,
            'Email Resent',
            f'Your email "{email.subject}" has been resent successfully.',
            'success',
            f'/dashboard/email/{email.id}'
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Email resent successfully!'})
        
        flash('Email resent successfully!', 'success')
    except Exception:
        traceback.print_exc()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Failed to resend email. Please try again.'})
        flash('Failed to resend email. Please try again.', 'error')
    
    return redirect(url_for('routes.sent_details', email_id=email.id))

@routes_bp.route('/dashboard/email/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_emails():
    email_ids = request.form.getlist('email_ids')
    if not email_ids:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'No emails selected.'})
        flash('No emails selected.', 'error')
        return redirect(url_for('routes.sent'))
    
    deleted_count = 0
    for email_id in email_ids:
        email = SentEmail.query.filter_by(id=email_id, sender_id=current_user.id).first()
        if email:
            for attachment in email.attachments:
                if os.path.exists(attachment.file_path):
                    os.remove(attachment.file_path)
                current_user.storage_used -= attachment.file_size
            db.session.delete(email)
            deleted_count += 1
    
    db.session.commit()
    
    create_notification(
        current_user.id,
        'Bulk Delete Emails',
        f'{deleted_count} emails have been deleted.',
        'info'
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'deleted': deleted_count})
    
    flash(f'{deleted_count} emails deleted successfully.', 'success')
    return redirect(url_for('routes.sent'))

@routes_bp.route('/logout-redirect')
def logout_redirect():
    return redirect(url_for('auth.logout'))

@routes_bp.route('/public/attachment/<int:attachment_id>/download')
def public_download_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    email = SentEmail.query.get(attachment.email_id)
    
    if not email or not email.public_token or not email.is_sent:
        abort(404)
    
    if not os.path.exists(attachment.file_path):
        abort(404)
    
    return send_file(
        attachment.file_path,
        download_name=attachment.original_filename,
        as_attachment=True
    )

@routes_bp.route('/public/attachment/<int:attachment_id>/view')
def public_view_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    email = SentEmail.query.get(attachment.email_id)
    
    if not email or not email.public_token or not email.is_sent:
        abort(404)
    
    if not os.path.exists(attachment.file_path):
        abort(404)
    
    content_type = attachment.mime_type or 'application/octet-stream'
    return send_file(
        attachment.file_path,
        mimetype=content_type,
        download_name=attachment.original_filename,
        as_attachment=False
    )
    
@routes_bp.route('/debug/email/<int:email_id>/attachments')
@login_required
def debug_attachments(email_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    email = SentEmail.query.get_or_404(email_id)
    attachments = Attachment.query.filter_by(email_id=email_id).all()
    
    debug_data = {
        'email_id': email_id,
        'email_subject': email.subject,
        'email_sender_id': email.sender_id,
        'email_recipient': email.recipient,
        'email_is_sent': email.is_sent,
        'email_public_token': email.public_token,
        'attachment_count': len(attachments),
        'attachments': []
    }
    
    for att in attachments:
        debug_data['attachments'].append({
            'id': att.id,
            'filename': att.filename,
            'original_filename': att.original_filename,
            'file_path': att.file_path,
            'file_exists': os.path.exists(att.file_path) if att.file_path else False,
            'file_size': att.file_size,
            'file_type': att.file_type,
            'mime_type': att.mime_type,
            'is_image': att.is_image,
            'is_video': att.is_video,
            'is_audio': att.is_audio,
            'is_document': att.is_document,
            'is_archive': att.is_archive,
            'is_code': att.is_code,
            'uploaded_at': att.uploaded_at.isoformat() if att.uploaded_at else None
        })
    
    return jsonify(debug_data)
