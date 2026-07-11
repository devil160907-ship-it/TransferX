document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggle();
    initPasswordStrength();
    initPasswordConfirmation();
    initUsernameValidation();
    initEmailValidation();
});

function initPasswordToggle() {
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const input = document.getElementById(targetId);
            if (!input) return;
            
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.className = type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
        });
    });
}

function initPasswordStrength() {
    const passwordInputs = document.querySelectorAll('#password, #new_password');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            const container = this.closest('.form-group').querySelector('.password-strength');
            if (!container) return;
            
            const bar = container.querySelector('.strength-level');
            const text = container.querySelector('.strength-text');
            
            if (this.value.length === 0) {
                bar.style.width = '0%';
                bar.style.background = '#e2e8f0';
                text.textContent = 'Weak';
                text.style.color = '#a0aec0';
                return;
            }
            
            bar.style.width = strength.percentage + '%';
            bar.style.background = strength.color;
            text.textContent = strength.label;
            text.style.color = strength.color;
        });
    });
}

function calculatePasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    const percentage = Math.min((score / 6) * 100, 100);
    let label, color;
    
    if (percentage < 30) {
        label = 'Weak';
        color = '#fc8181';
    } else if (percentage < 55) {
        label = 'Fair';
        color = '#f6ad55';
    } else if (percentage < 80) {
        label = 'Good';
        color = '#68d391';
    } else {
        label = 'Strong';
        color = '#48bb78';
    }
    
    return { percentage, label, color };
}

function initPasswordConfirmation() {
    const password = document.getElementById('password') || document.getElementById('new_password');
    const confirm = document.getElementById('confirm_password');
    
    if (password && confirm) {
        const validate = debounce(function() {
            const match = password.value === confirm.value && password.value.length > 0;
            const feedback = confirm.closest('.form-group').querySelector('.validation-feedback');
            
            if (feedback) {
                if (confirm.value.length === 0) {
                    feedback.textContent = '';
                    feedback.className = 'validation-feedback';
                } else if (match) {
                    feedback.textContent = '✓ Passwords match';
                    feedback.className = 'validation-feedback success';
                } else {
                    feedback.textContent = '✗ Passwords do not match';
                    feedback.className = 'validation-feedback error';
                }
            }
        }, 300);
        
        password.addEventListener('input', validate);
        confirm.addEventListener('input', validate);
    }
}

function initUsernameValidation() {
    const username = document.getElementById('username');
    if (!username) return;
    
    const validate = debounce(function() {
        const value = this.value.trim();
        const feedback = this.closest('.form-group').querySelector('.validation-feedback');
        if (!feedback || value.length < 3) return;
        
        fetch('/auth/check-username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ username: value })
        })
        .then(response => response.json())
        .then(data => {
            if (data.available) {
                feedback.textContent = '✓ Username available';
                feedback.className = 'validation-feedback success';
            } else {
                feedback.textContent = '✗ Username already taken';
                feedback.className = 'validation-feedback error';
            }
        });
    }, 500);
    
    username.addEventListener('input', validate);
}

function initEmailValidation() {
    const email = document.getElementById('email');
    if (!email) return;
    
    const validate = debounce(function() {
        const value = this.value.trim();
        const feedback = this.closest('.form-group').querySelector('.validation-feedback');
        if (!feedback || value.length < 5 || !value.includes('@')) return;
        
        fetch('/auth/check-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ email: value })
        })
        .then(response => response.json())
        .then(data => {
            if (data.available) {
                feedback.textContent = '✓ Email available';
                feedback.className = 'validation-feedback success';
            } else {
                feedback.textContent = '✗ Email already registered';
                feedback.className = 'validation-feedback error';
            }
        });
    }, 500);
    
    email.addEventListener('input', validate);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}