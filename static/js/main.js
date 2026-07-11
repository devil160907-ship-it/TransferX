document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initAutoDismissNotifications();
    initCSRFToken();
    initHamburgerMenu();
    initMobileMenuClose();
    initNavLinkClose();
    initMobileMenuState();
    initViewportFix();
});

function initThemeToggle() {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(toggle, currentTheme);
    
    toggle.addEventListener('click', function() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(this, next);
    });
}

function updateThemeIcon(button, theme) {
    const icon = button.querySelector('i');
    if (theme === 'dark') {
        icon.className = 'bi bi-sun';
    } else {
        icon.className = 'bi bi-moon';
    }
}

function initAutoDismissNotifications() {
    document.querySelectorAll('.notification-toast').forEach(toast => {
        const delay = parseInt(toast.dataset.autoDismiss) || 5000;
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, delay);
    });
}

function initCSRFToken() {
    const token = document.querySelector('input[name="csrf_token"]');
    if (token) {
        window.csrfToken = token.value;
    }
}

function initHamburgerMenu() {
    const hamburger = document.getElementById('hamburgerMenu');
    const navLinks = document.getElementById('navLinks');
    const navActions = document.getElementById('navActions');
    
    if (!hamburger || !navLinks) return;
    
    const newHamburger = hamburger.cloneNode(true);
    hamburger.parentNode.replaceChild(newHamburger, hamburger);
    
    const updatedHamburger = document.getElementById('hamburgerMenu');
    
    updatedHamburger.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleMobileMenu(updatedHamburger, navLinks, navActions);
    });
}

function toggleMobileMenu(hamburger, navLinks, navActions) {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('active');
    if (navActions) {
        navActions.classList.toggle('active');
    }
    document.body.classList.toggle('menu-open');
}

function initMobileMenuClose() {
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburgerMenu');
    const navActions = document.getElementById('navActions');
    
    if (!navLinks || !hamburger) return;
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && navLinks.classList.contains('active')) {
            closeMobileMenu(hamburger, navLinks, navActions);
        }
    });
    
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 992 && navLinks.classList.contains('active')) {
                closeMobileMenu(hamburger, navLinks, navActions);
            }
        }, 250);
    });
}

function initNavLinkClose() {
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburgerMenu');
    const navActions = document.getElementById('navActions');
    
    if (!navLinks || !hamburger) return;
    
    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (window.innerWidth <= 992 && navLinks.classList.contains('active')) {
                if (!this.getAttribute('href')?.includes('logout')) {
                    closeMobileMenu(hamburger, navLinks, navActions);
                }
            }
        });
    });
    
    document.addEventListener('click', function(e) {
        const nav = document.querySelector('.glass-nav');
        if (nav && !nav.contains(e.target) && navLinks.classList.contains('active')) {
            closeMobileMenu(hamburger, navLinks, navActions);
        }
    });
}

function closeMobileMenu(hamburger, navLinks, navActions) {
    if (hamburger) {
        hamburger.classList.remove('active');
    }
    if (navLinks) {
        navLinks.classList.remove('active');
    }
    if (navActions) {
        navActions.classList.remove('active');
    }
    document.body.classList.remove('menu-open');
}

function initMobileMenuState() {
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburgerMenu');
    const navActions = document.getElementById('navActions');
    
    if (!navLinks || !hamburger) return;
    
    if (window.innerWidth > 992) {
        closeMobileMenu(hamburger, navLinks, navActions);
    }
}

function initViewportFix() {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
    
    window.addEventListener('resize', function() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', vh + 'px');
    });
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal, .overlay, .custom-alert-overlay').forEach(el => {
            if (el.style.display !== 'none' && el.classList.contains('active')) {
                el.classList.remove('active');
                el.style.display = 'none';
            }
        });
    }
});

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showToast(message, title, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    
    const icons = {
        success: 'bi-check-circle',
        error: 'bi-x-circle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    };
    
    toast.innerHTML = `
        <i class="bi ${icons[type] || icons.success}"></i>
        <div style="flex:1;">
            ${title ? `<strong>${title}</strong><br>` : ''}
            <span>${message}</span>
        </div>
        <button class="dismiss-btn">&times;</button>
        <div class="progress-bar"></div>
    `;
    
    container.appendChild(toast);
    
    const dismissBtn = toast.querySelector('.dismiss-btn');
    dismissBtn.addEventListener('click', function() {
        dismissToast(toast);
    });
    
    setTimeout(() => {
        if (toast.parentNode) {
            dismissToast(toast);
        }
    }, 5000);
}

function dismissToast(toast) {
    toast.style.animation = 'slideOutRight 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
}