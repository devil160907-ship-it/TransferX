import secrets
import traceback
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from extensions import db
from models import User, EmailVerificationToken, PasswordResetToken, TwoFactorAttempt
from email_service import send_verification_email, send_password_reset_email, send_two_factor_otp
from notifications import create_notification
from config import Config
import pyotp
import qrcode
import io
import base64
import random

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def generate_token():
    return secrets.token_urlsafe(32)

def get_token_serializer():
    return URLSafeTimedSerializer(Config.SECRET_KEY)

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def check_two_factor_attempts(user_id):
    ip = get_client_ip()
    attempt = TwoFactorAttempt.query.filter_by(user_id=user_id, ip_address=ip).first()
    
    if attempt and attempt.locked_until and attempt.locked_until > datetime.utcnow():
        return False, attempt.locked_until
    
    return True, None

def record_two_factor_attempt(user_id, success=False):
    ip = get_client_ip()
    attempt = TwoFactorAttempt.query.filter_by(user_id=user_id, ip_address=ip).first()
    
    if not attempt:
        attempt = TwoFactorAttempt(user_id=user_id, ip_address=ip)
        db.session.add(attempt)
    
    if success:
        attempt.attempts = 0
        attempt.locked_until = None
    else:
        attempt.attempts += 1
        if attempt.attempts >= Config.TWO_FACTOR_ATTEMPT_LIMIT:
            attempt.locked_until = datetime.utcnow() + timedelta(minutes=Config.TWO_FACTOR_LOCKOUT_MINUTES)
    
    attempt.updated_at = datetime.utcnow()
    db.session.commit()
    
    return attempt

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/register.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken.', 'error')
            return render_template('auth/register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        token = generate_token()
        expires_at = datetime.utcnow() + timedelta(seconds=Config.VERIFICATION_TOKEN_EXPIRY)
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(verification_token)
        db.session.commit()
        
        try:
            send_verification_email(user.email, user.username, token)
        except Exception:
            traceback.print_exc()
        
        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'error')
            return render_template('auth/login.html')
        
        if not user.email_verified:
            flash('Please verify your email before logging in.', 'warning')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated.', 'error')
            return render_template('auth/login.html')
        
        session['pre_login_user_id'] = user.id
        session['pre_login_remember'] = remember
        
        if user.two_factor_enabled:
            return redirect(url_for('auth.verify_2fa'))
        
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        return redirect(url_for('routes.dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    user_id = session.get('pre_login_user_id')
    if not user_id:
        flash('Please login first.', 'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if not user:
        session.pop('pre_login_user_id', None)
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    if not user.two_factor_enabled:
        session.pop('pre_login_user_id', None)
        return redirect(url_for('auth.login'))
    
    can_attempt, lock_until = check_two_factor_attempts(user.id)
    if not can_attempt:
        remaining = (lock_until - datetime.utcnow()).seconds
        flash(f'Too many failed attempts. Please wait {remaining // 60} minutes.', 'error')
        return render_template('auth/verify_2fa.html', user=user, method=user.two_factor_method, locked=True)
    
    if user.two_factor_method == 'email' and request.method == 'GET':
        otp_code = user.generate_otp()
        user.otp_expiry = datetime.utcnow() + timedelta(seconds=Config.TWO_FACTOR_OTP_EXPIRY_SECONDS)
        db.session.commit()
        
        try:
            send_two_factor_otp(user.email, user.username, otp_code)
        except Exception:
            traceback.print_exc()
            flash('Failed to send verification code. Please try again.', 'error')
    
    if request.method == 'POST':
        code = request.form.get('code')
        remember_device = request.form.get('remember_device') == 'on'
        
        if not code:
            flash('Please enter your verification code.', 'error')
            return render_template('auth/verify_2fa.html', user=user, method=user.two_factor_method)
        
        can_attempt, lock_until = check_two_factor_attempts(user.id)
        if not can_attempt:
            remaining = (lock_until - datetime.utcnow()).seconds
            flash(f'Too many failed attempts. Please wait {remaining // 60} minutes.', 'error')
            return render_template('auth/verify_2fa.html', user=user, method=user.two_factor_method, locked=True)
        
        valid = False
        
        if user.two_factor_method == 'email':
            valid = user.is_otp_valid(code)
            if valid:
                user.clear_otp()
        
        elif user.two_factor_method == 'totp':
            if user.totp_secret:
                totp = pyotp.TOTP(user.totp_secret)
                valid = totp.verify(code)
        
        if valid:
            record_two_factor_attempt(user.id, success=True)
            
            login_user(user, remember=session.get('pre_login_remember', False))
            user.last_login = datetime.utcnow()
            
            if remember_device:
                token = generate_token()
                user.remember_device_token = token
                serializer = get_token_serializer()
                signed_token = serializer.dumps({'user_id': user.id, 'token': token})
                response = redirect(url_for('routes.dashboard'))
                response.set_cookie(
                    'remember_2fa',
                    signed_token,
                    max_age=timedelta(days=Config.TWO_FACTOR_REMEMBER_DAYS),
                    httponly=True,
                    secure=True,
                    samesite='Lax'
                )
                db.session.commit()
                return response
            
            db.session.commit()
            session.pop('pre_login_user_id', None)
            session.pop('pre_login_remember', None)
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            flash('Login successful!', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            record_two_factor_attempt(user.id, success=False)
            flash('Invalid verification code. Please try again.', 'error')
            
            if user.two_factor_method == 'email':
                user.clear_otp()
                db.session.commit()
    
    return render_template('auth/verify_2fa.html', user=user, method=user.two_factor_method)

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    user_id = session.get('pre_login_user_id')
    if not user_id:
        return jsonify({'error': 'Session expired. Please login again.'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    
    if not user.two_factor_enabled or user.two_factor_method != 'email':
        return jsonify({'error': 'Email OTP is not enabled for this account.'}), 400
    
    otp_code = user.generate_otp()
    user.otp_expiry = datetime.utcnow() + timedelta(seconds=Config.TWO_FACTOR_OTP_EXPIRY_SECONDS)
    db.session.commit()
    
    try:
        send_two_factor_otp(user.email, user.username, otp_code)
        return jsonify({'success': True, 'message': 'Verification code resent successfully.'})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Failed to send verification code.'}), 500

@auth_bp.route('/logout')
@login_required
def logout():
    response = redirect(url_for('routes.home'))
    response.delete_cookie('remember_2fa')
    logout_user()
    flash('You have been logged out.', 'info')
    return response

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    verification_token = EmailVerificationToken.query.filter_by(token=token).first()
    
    if not verification_token:
        flash('Invalid verification token.', 'error')
        return redirect(url_for('auth.login'))
    
    if verification_token.expires_at < datetime.utcnow():
        flash('Verification token has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.resend_verification'))
    
    user = User.query.get(verification_token.user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    user.email_verified = True
    db.session.delete(verification_token)
    db.session.commit()
    
    create_notification(user.id, 'Email Verified', 'Your email has been successfully verified!', 'success')
    flash('Email verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user and not user.email_verified:
            EmailVerificationToken.query.filter_by(user_id=user.id).delete()
            
            token = generate_token()
            expires_at = datetime.utcnow() + timedelta(seconds=Config.VERIFICATION_TOKEN_EXPIRY)
            verification_token = EmailVerificationToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(verification_token)
            db.session.commit()
            
            try:
                send_verification_email(user.email, user.username, token)
                flash('Verification email has been resent. Please check your inbox.', 'success')
            except Exception:
                traceback.print_exc()
                flash('Failed to send verification email. Please try again later.', 'error')
        else:
            flash('Email not found or already verified.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/resend_verification.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            PasswordResetToken.query.filter_by(user_id=user.id).delete()
            
            token = generate_token()
            expires_at = datetime.utcnow() + timedelta(seconds=Config.RESET_TOKEN_EXPIRY)
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset_token)
            db.session.commit()
            
            try:
                send_password_reset_email(user.email, user.username, token)
                flash('Password reset instructions have been sent to your email.', 'success')
            except Exception:
                traceback.print_exc()
                flash('Failed to send reset email. Please try again later.', 'error')
        else:
            flash('If your email is registered, you will receive reset instructions.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token or reset_token.is_used:
        flash('Invalid or used reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if reset_token.expires_at < datetime.utcnow():
        flash('Reset token has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        user = User.query.get(reset_token.user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.login'))
        
        user.set_password(password)
        reset_token.is_used = True
        db.session.commit()
        
        create_notification(user.id, 'Password Changed', 'Your password has been successfully changed.', 'success')
        flash('Password has been reset successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/check-username', methods=['POST'])
def check_username():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    return jsonify({'available': user is None})

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    return jsonify({'available': user is None})

@auth_bp.route('/setup-totp', methods=['POST'])
@login_required
def setup_totp():
    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    db.session.commit()
    
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name='TransferX'
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    
    buffered = io.BytesIO()
    img.save(buffered, format='PNG')
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({
        'secret': secret,
        'qr_code': qr_base64,
        'provisioning_uri': provisioning_uri
    })

@auth_bp.route('/verify-totp', methods=['POST'])
@login_required
def verify_totp():
    code = request.json.get('code')
    
    if not code:
        return jsonify({'error': 'Verification code is required.'}), 400
    
    if not current_user.totp_secret:
        return jsonify({'error': 'TOTP not set up.'}), 400
    
    totp = pyotp.TOTP(current_user.totp_secret)
    
    if totp.verify(code):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Invalid verification code.'}), 400

@auth_bp.route('/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    method = request.json.get('method')
    
    if method not in ['email', 'totp']:
        return jsonify({'error': 'Invalid authentication method.'}), 400
    
    if method == 'totp':
        code = request.json.get('code')
        if not code:
            return jsonify({'error': 'Verification code is required.'}), 400
        
        if not current_user.totp_secret:
            return jsonify({'error': 'TOTP not set up. Please set up TOTP first.'}), 400
        
        totp = pyotp.TOTP(current_user.totp_secret)
        if not totp.verify(code):
            return jsonify({'error': 'Invalid verification code.'}), 400
    
    current_user.two_factor_enabled = True
    current_user.two_factor_method = method
    db.session.commit()
    
    if method == 'email':
        create_notification(
            current_user.id,
            'Two-Factor Authentication Enabled',
            'Email OTP has been enabled for your account.',
            'success'
        )
    else:
        create_notification(
            current_user.id,
            'Two-Factor Authentication Enabled',
            'Google Authenticator has been enabled for your account.',
            'success'
        )
    
    return jsonify({'success': True, 'message': 'Two-Factor Authentication enabled successfully.'})

@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    current_user.two_factor_enabled = False
    current_user.two_factor_method = None
    current_user.totp_secret = None
    current_user.otp_code = None
    current_user.otp_expiry = None
    db.session.commit()
    
    create_notification(
        current_user.id,
        'Two-Factor Authentication Disabled',
        'Two-Factor Authentication has been disabled for your account.',
        'info'
    )
    
    return jsonify({'success': True, 'message': 'Two-Factor Authentication disabled successfully.'})

@auth_bp.route('/2fa-status', methods=['GET'])
@login_required
def two_factor_status():
    return jsonify({
        'enabled': current_user.two_factor_enabled,
        'method': current_user.two_factor_method,
        'has_totp_secret': bool(current_user.totp_secret)
    })

@auth_bp.route('/check-remember-token', methods=['GET'])
def check_remember_token():
    token = request.cookies.get('remember_2fa')
    if not token:
        return jsonify({'valid': False})
    
    try:
        serializer = get_token_serializer()
        data = serializer.loads(token, max_age=timedelta(days=Config.TWO_FACTOR_REMEMBER_DAYS))
        user_id = data.get('user_id')
        token_value = data.get('token')
        
        user = User.query.get(user_id)
        if user and user.remember_device_token == token_value:
            return jsonify({'valid': True, 'user_id': user_id})
    except (BadSignature, SignatureExpired):
        pass
    
    return jsonify({'valid': False})