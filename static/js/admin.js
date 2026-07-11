document.addEventListener('DOMContentLoaded', function() {
    initAdminStats();
    initUserManagement();
    initActivityMonitoring();
});

function initAdminStats() {
    const stats = document.querySelectorAll('.stat-card .stat-value');
    stats.forEach(stat => {
        const target = parseInt(stat.textContent);
        if (!isNaN(target) && target > 0) {
            animateNumber(stat, target);
        }
    });
}

function animateNumber(element, target) {
    const duration = 1000;
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeOutCubic(progress);
        const current = Math.floor(eased * target);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target;
        }
    }
    
    requestAnimationFrame(update);
}

function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

function initUserManagement() {
    document.querySelectorAll('.user-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const status = this.dataset.status;
            
            fetch(`/admin/users/${userId}/toggle`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.active) {
                    this.classList.remove('btn-danger');
                    this.classList.add('btn-success');
                    this.innerHTML = '<i class="bi bi-check-circle"></i> Active';
                    this.dataset.status = 'active';
                } else {
                    this.classList.remove('btn-success');
                    this.classList.add('btn-danger');
                    this.innerHTML = '<i class="bi bi-x-circle"></i> Inactive';
                    this.dataset.status = 'inactive';
                }
                notifications.success(`User status updated successfully`);
            })
            .catch(() => {
                notifications.error('Failed to update user status');
            });
        });
    });
    
    document.querySelectorAll('.user-delete').forEach(button => {
        button.addEventListener('click', function() {
            if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
                return;
            }
            
            const userId = this.dataset.userId;
            const row = this.closest('.user-item');
            
            fetch(`/admin/users/${userId}/delete`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    row.remove();
                    notifications.success('User deleted successfully');
                    updateStats();
                }
            })
            .catch(() => {
                notifications.error('Failed to delete user');
            });
        });
    });
}

function initActivityMonitoring() {
    const refreshBtn = document.getElementById('refreshActivity');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const days = document.getElementById('activityDays')?.value || 7;
            
            fetch(`/admin/activity-logs?days=${days}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('emailCount').textContent = data.emails;
                document.getElementById('userCount').textContent = data.new_users;
                notifications.success('Activity data refreshed');
            })
            .catch(() => {
                notifications.error('Failed to refresh activity data');
            });
        });
    }
}

function updateStats() {
    fetch('/admin/dashboard')
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newStats = doc.querySelectorAll('.stat-card .stat-value');
            document.querySelectorAll('.stat-card .stat-value').forEach((stat, index) => {
                if (newStats[index]) {
                    stat.textContent = newStats[index].textContent;
                }
            });
        });
}