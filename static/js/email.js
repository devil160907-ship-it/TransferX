document.addEventListener('DOMContentLoaded', function() {
    initEditorToolbar();
    initEmailForm();
});

function initEditorToolbar() {
    const toolbar = document.querySelector('.editor-toolbar');
    const textarea = document.getElementById('body');
    
    if (!toolbar || !textarea) return;
    
    toolbar.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const command = this.dataset.command;
            if (!command) return;
            
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = textarea.value;
            let newText = text;
            let cursorOffset = 0;
            
            switch(command) {
                case 'bold':
                    newText = text.substring(0, start) + '**' + text.substring(start, end) + '**' + text.substring(end);
                    cursorOffset = 2;
                    break;
                case 'italic':
                    newText = text.substring(0, start) + '*' + text.substring(start, end) + '*' + text.substring(end);
                    cursorOffset = 1;
                    break;
                case 'underline':
                    newText = text.substring(0, start) + '__' + text.substring(start, end) + '__' + text.substring(end);
                    cursorOffset = 2;
                    break;
                case 'strike':
                    newText = text.substring(0, start) + '~~' + text.substring(start, end) + '~~' + text.substring(end);
                    cursorOffset = 2;
                    break;
                case 'justifyLeft':
                case 'justifyCenter':
                case 'justifyRight':
                    break;
                case 'insertUnorderedList':
                    const lines = text.substring(start, end).split('\n');
                    const bulletLines = lines.map(line => '- ' + line).join('\n');
                    newText = text.substring(0, start) + bulletLines + text.substring(end);
                    cursorOffset = 2;
                    break;
                case 'insertOrderedList':
                    const oLines = text.substring(start, end).split('\n');
                    const numLines = oLines.map((line, i) => (i + 1) + '. ' + line).join('\n');
                    newText = text.substring(0, start) + numLines + text.substring(end);
                    cursorOffset = 3;
                    break;
                default:
                    return;
            }
            
            textarea.value = newText;
            const newCursor = start + cursorOffset;
            textarea.setSelectionRange(newCursor, newCursor);
            textarea.focus();
        });
    });
}

function initEmailForm() {
    const form = document.getElementById('composeForm');
    const sendBtn = document.getElementById('sendEmailBtn');
    
    if (!form || !sendBtn) return;
    
    sendBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        handleSendEmail(form);
    });
}

function handleSendEmail(form) {
    const recipient = document.getElementById('recipient').value.trim();
    if (!recipient) {
        showNotification('Please enter at least one recipient.', 'error');
        document.getElementById('recipient').focus();
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const emails = recipient.split(',').map(e => e.trim());
    const invalidEmails = emails.filter(e => !emailRegex.test(e));
    if (invalidEmails.length > 0) {
        showNotification('Invalid email address(es): ' + invalidEmails.join(', '), 'error');
        document.getElementById('recipient').focus();
        return;
    }
    
    const subject = document.getElementById('subject').value.trim();
    if (!subject) {
        showNotification('Please enter a subject.', 'error');
        document.getElementById('subject').focus();
        return;
    }
    
    const body = document.getElementById('body').value.trim();
    if (!body) {
        showNotification('Please enter a message.', 'error');
        document.getElementById('body').focus();
        return;
    }
    
    const formData = new FormData(form);
    formData.set('action', 'send');
    
    if (window.uploadManager) {
        const files = window.uploadManager.getFiles();
        if (files.length > 0) {
            files.forEach((file) => {
                formData.append('attachments', file);
            });
        }
    }
    
    fetch('/dashboard/compose', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        return response.json().catch(() => response.text());
    })
    .then(data => {
        if (typeof data === 'object' && data.error) {
            showNotification(data.error, 'error');
        } else if (typeof data === 'object' && data.success) {
            showNotification(data.message || 'Email sent successfully!', 'success');
            setTimeout(() => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    window.location.href = '/dashboard/sent';
                }
            }, 1500);
        } else if (typeof data === 'string' && data.includes('<!DOCTYPE')) {
            showNotification('Email sent successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard/sent';
            }, 1500);
        } else {
            showNotification('Email sent successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard/sent';
            }, 1500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to send email. Please try again.', 'error');
    });
}

function showNotification(message, type = 'info', title = '') {
    const container = document.getElementById('toast-container');
    if (!container) {
        console.log(message);
        return;
    }
    
    const toast = document.createElement('div');
    toast.className = 'notification-toast ' + type;
    
    const icons = {
        success: 'bi-check-circle',
        error: 'bi-x-circle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    };
    
    toast.innerHTML = `
        <i class="bi ${icons[type] || icons.info}"></i>
        <div style="flex:1;">
            ${title ? '<strong>' + title + '</strong><br>' : ''}
            <span>${message}</span>
        </div>
        <button class="dismiss-btn">&times;</button>
        <div class="progress-bar"></div>
    `;
    
    container.appendChild(toast);
    
    const dismissBtn = toast.querySelector('.dismiss-btn');
    dismissBtn.addEventListener('click', function() {
        toast.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(function() {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    });
    
    setTimeout(function() {
        if (toast.parentNode) {
            toast.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(function() {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }
    }, 5000);
}