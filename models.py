from datetime import datetime
import secrets
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    storage_used = db.Column(db.BigInteger, default=0)
    max_storage = db.Column(db.BigInteger, default=1073741824)
    
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_method = db.Column(db.String(20), nullable=True)
    totp_secret = db.Column(db.String(100), nullable=True)
    otp_code = db.Column(db.String(10), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    remember_device_token = db.Column(db.String(100), nullable=True)
    
    sent_emails = db.relationship('SentEmail', backref='sender', lazy=True)
    drafts = db.relationship('Draft', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_storage_usage_percentage(self):
        if self.max_storage > 0:
            return (self.storage_used / self.max_storage) * 100
        return 0
    
    def generate_otp(self):
        import random
        self.otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.otp_expiry = datetime.utcnow()
        return self.otp_code
    
    def is_otp_valid(self, code):
        if not self.otp_code or not self.otp_expiry:
            return False
        if self.otp_code != code:
            return False
        if (datetime.utcnow() - self.otp_expiry).total_seconds() > 300:
            return False
        return True
    
    def clear_otp(self):
        self.otp_code = None
        self.otp_expiry = None

class SentEmail(db.Model):
    __tablename__ = 'sent_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient = db.Column(db.String(500), nullable=False)
    cc = db.Column(db.String(500))
    bcc = db.Column(db.String(500))
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    is_draft = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    public_token = db.Column(db.String(100), unique=True, nullable=True)
    
    attachments = db.relationship('Attachment', backref='email', lazy=True, cascade='all, delete-orphan')
    
    def get_attachment_count(self):
        return len(self.attachments)
    
    def get_total_size(self):
        return sum(attachment.file_size for attachment in self.attachments)
    
    def generate_public_token(self):
        self.public_token = secrets.token_urlsafe(32)
        return self.public_token

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('sent_emails.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_type = db.Column(db.String(50))
    mime_type = db.Column(db.String(100))
    is_image = db.Column(db.Boolean, default=False)
    is_video = db.Column(db.Boolean, default=False)
    is_audio = db.Column(db.Boolean, default=False)
    is_document = db.Column(db.Boolean, default=False)
    is_archive = db.Column(db.Boolean, default=False)
    is_code = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Draft(db.Model):
    __tablename__ = 'drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient = db.Column(db.String(500))
    cc = db.Column(db.String(500))
    bcc = db.Column(db.String(500))
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

class TwoFactorAttempt(db.Model):
    __tablename__ = 'two_factor_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)