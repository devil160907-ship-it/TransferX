class NotificationManager {
    constructor() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.style.cssText = `
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                max-width: 400px;
                width: 100%;
            `;
            document.body.appendChild(this.container);
        }
    }
    
    show(message, type = 'info', title = '', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `notification-toast ${type}`;
        toast.style.animation = 'slideInRight 0.3s ease';
        
        const icons = {
            success: 'bi-check-circle',
            error: 'bi-x-circle',
            warning: 'bi-exclamation-triangle',
            info: 'bi-info-circle'
        };
        
        toast.innerHTML = `
            <i class="bi ${icons[type] || icons.info}"></i>
            <div class="toast-content">
                ${title ? `<strong>${title}</strong><br>` : ''}
                <span>${message}</span>
            </div>
            <button class="dismiss-btn">&times;</button>
            <div class="progress-bar" style="animation-duration: ${duration}ms"></div>
        `;
        
        this.container.appendChild(toast);
        
        const dismiss = toast.querySelector('.dismiss-btn');
        dismiss.addEventListener('click', () => this.dismiss(toast));
        
        setTimeout(() => {
            if (toast.parentNode) {
                this.dismiss(toast);
            }
        }, duration);
    }
    
    dismiss(toast) {
        toast.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }
    
    success(message, title = '') {
        this.show(message, 'success', title);
    }
    
    error(message, title = '') {
        this.show(message, 'error', title);
    }
    
    warning(message, title = '') {
        this.show(message, 'warning', title);
    }
    
    info(message, title = '') {
        this.show(message, 'info', title);
    }
}

const notifications = new NotificationManager();

document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .toast-content {
            flex: 1;
            font-size: 0.95rem;
        }
    `;
    document.head.appendChild(style);
});