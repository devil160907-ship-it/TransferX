document.addEventListener('DOMContentLoaded', function() {
    initRippleButtons();
    initFloatingCards();
    initSkeletonLoading();
});

function initRippleButtons() {
    document.querySelectorAll('.btn-primary, .btn-secondary, .btn-danger, .btn-icon').forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const ripple = document.createElement('span');
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                width: ${size}px;
                height: ${size}px;
                left: ${e.clientX - rect.left - size/2}px;
                top: ${e.clientY - rect.top - size/2}px;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            if (getComputedStyle(this).position === 'static') {
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
            }
            
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

function initFloatingCards() {
    document.querySelectorAll('.glass-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });
}

function initSkeletonLoading() {
    document.querySelectorAll('.skeleton').forEach(el => {
        el.classList.add('skeleton-loading');
    });
}

const styleAnimations = document.createElement('style');
styleAnimations.textContent = `
    @keyframes ripple {
        from {
            transform: scale(0);
            opacity: 1;
        }
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
    }
    
    .skeleton-loading {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 4px;
    }
`;
document.head.appendChild(styleAnimations);