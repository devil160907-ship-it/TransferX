import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///transferx.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 104857600)
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', '').split(','))
    
    PERMANENT_SESSION_LIFETIME = 3600
    
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-key'
    
    VERIFICATION_TOKEN_EXPIRY = 86400
    RESET_TOKEN_EXPIRY = 3600
    
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'
    
    TWO_FACTOR_ATTEMPT_LIMIT = 5
    TWO_FACTOR_LOCKOUT_MINUTES = 5
    TWO_FACTOR_OTP_EXPIRY_SECONDS = 300
    TWO_FACTOR_RESEND_COOLDOWN_SECONDS = 30
    TWO_FACTOR_REMEMBER_DAYS = 30