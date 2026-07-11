from flask import render_template
from flask_mail import Message
from extensions import mail
from config import Config
import os
import mimetypes
import traceback

def send_email(to, subject, template, attachments=None, **kwargs):
    try:
        if 'base_url' not in kwargs:
            kwargs['base_url'] = Config.BASE_URL
        
        msg = Message(
            subject=subject,
            sender=Config.MAIL_DEFAULT_SENDER,
            recipients=[to] if isinstance(to, str) else to
        )
        msg.html = render_template(template, **kwargs)
        
        if attachments:
            for attachment in attachments:
                try:
                    file_path = attachment.get('file_path')
                    filename = attachment.get('filename')
                    mime_type = attachment.get('mime_type')
                    
                    if not file_path or not os.path.exists(file_path):
                        continue
                    
                    if not mime_type:
                        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                    
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    msg.attach(
                        filename=filename,
                        content_type=mime_type,
                        data=file_data
                    )
                except Exception:
                    traceback.print_exc()
                    continue
        
        mail.send(msg)
        return True
    except Exception:
        traceback.print_exc()
        return False

def send_email_with_copy(to, subject, template, sender_email=None, attachments=None, **kwargs):
    try:
        if 'base_url' not in kwargs:
            kwargs['base_url'] = Config.BASE_URL
        
        recipients = [to] if isinstance(to, str) else to
        
        if sender_email and sender_email != to:
            recipients.append(sender_email)
        
        msg = Message(
            subject=subject,
            sender=Config.MAIL_DEFAULT_SENDER,
            recipients=recipients
        )
        msg.html = render_template(template, **kwargs)
        
        if attachments:
            for attachment in attachments:
                try:
                    file_path = attachment.get('file_path')
                    filename = attachment.get('filename')
                    mime_type = attachment.get('mime_type')
                    
                    if not file_path or not os.path.exists(file_path):
                        continue
                    
                    if not mime_type:
                        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                    
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    msg.attach(
                        filename=filename,
                        content_type=mime_type,
                        data=file_data
                    )
                except Exception:
                    traceback.print_exc()
                    continue
        
        mail.send(msg)
        return True
    except Exception:
        traceback.print_exc()
        return False

def send_welcome_email(to, username):
    return send_email(
        to=to,
        subject='Welcome to TransferX!',
        template='emails/welcome.html',
        username=username
    )

def send_verification_email(to, username, token):
    verification_url = f"{Config.BASE_URL}/auth/verify-email/{token}"
    return send_email(
        to=to,
        subject='Verify Your Email - TransferX',
        template='emails/verify_email.html',
        username=username,
        verification_url=verification_url
    )

def send_password_reset_email(to, username, token):
    reset_url = f"{Config.BASE_URL}/auth/reset-password/{token}"
    return send_email(
        to=to,
        subject='Reset Your Password - TransferX',
        template='emails/reset_password.html',
        username=username,
        reset_url=reset_url
    )

def send_password_changed_email(to, username):
    return send_email(
        to=to,
        subject='Password Changed - TransferX',
        template='emails/password_changed.html',
        username=username
    )

def send_email_sent_notification(to, sender_name, email_subject, email_id, sender_email=None, body=None, attachments=None, public_token=None):
    view_url = f"{Config.BASE_URL}/dashboard/email/{email_id}"
    public_url = f"{Config.BASE_URL}/public/email/{public_token}" if public_token else None
    
    if sender_email:
        return send_email_with_copy(
            to=to,
            subject=f'New Email from {sender_name}',
            template='emails/email_sent.html',
            sender_email=sender_email,
            attachments=attachments,
            sender_name=sender_name,
            email_subject=email_subject,
            view_url=view_url,
            public_url=public_url,
            body=body
        )
    else:
        return send_email(
            to=to,
            subject=f'New Email from {sender_name}',
            template='emails/email_sent.html',
            attachments=attachments,
            sender_name=sender_name,
            email_subject=email_subject,
            view_url=view_url,
            public_url=public_url,
            body=body
        )

def send_contact_email(name, email, subject, message):
    subject_line = f"Contact Form: {subject} from {name}"
    body = f"""
    <h2>New Contact Form Submission</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Subject:</strong> {subject}</p>
    <p><strong>Message:</strong></p>
    <p>{message}</p>
    <hr>
    <p><small>This message was sent from the TransferX contact form.</small></p>
    """
    
    try:
        msg = Message(
            subject=subject_line,
            sender=Config.MAIL_DEFAULT_SENDER,
            recipients=[Config.MAIL_DEFAULT_SENDER]
        )
        msg.html = body
        if email:
            msg.cc = [email]
        mail.send(msg)
        return True
    except Exception:
        traceback.print_exc()
        return False

def send_notification_email(to, subject, message):
    return send_email(
        to=to,
        subject=subject,
        template='emails/notification.html',
        message=message
    )

def send_two_factor_otp(to, username, otp_code):
    return send_email(
        to=to,
        subject='TransferX Login Verification Code',
        template='emails/two_factor_otp.html',
        username=username,
        otp_code=otp_code,
        expiry_minutes=5
    )