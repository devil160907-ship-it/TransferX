class FileUploadManager {
    constructor(options = {}) {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.progressBar = document.getElementById('uploadProgress');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.files = [];
        this.maxSize = options.maxSize || 104857600;
        this.allowedTypes = options.allowedTypes || [];
        this.form = document.getElementById('composeForm');
        
        this.init();
        this.setupFormHandler();
    }
    
    init() {
        if (this.uploadArea) {
            this.uploadArea.addEventListener('click', () => this.fileInput.click());
            this.uploadArea.addEventListener('dragover', this.onDragOver.bind(this));
            this.uploadArea.addEventListener('dragleave', this.onDragLeave.bind(this));
            this.uploadArea.addEventListener('drop', this.onDrop.bind(this));
        }
        
        if (this.fileInput) {
            this.fileInput.addEventListener('change', this.onFileSelect.bind(this));
        }
    }
    
    setupFormHandler() {
        if (this.form) {
            // Override the default form submission to include files
            this.form.addEventListener('submit', (e) => {
                // If files were added via drag-and-drop, we need to add them to the file input
                if (this.files.length > 0) {
                    // Create a new FileList-like object
                    const dataTransfer = new DataTransfer();
                    this.files.forEach(file => dataTransfer.items.add(file));
                    this.fileInput.files = dataTransfer.files;
                }
            });
        }
    }
    
    onDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    onDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    onDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        this.addFiles(files);
    }
    
    onFileSelect(e) {
        const files = Array.from(e.target.files);
        this.addFiles(files);
        // Don't reset the input here - we want to keep the files
        // this.fileInput.value = ''; // REMOVE THIS LINE
    }
    
    addFiles(files) {
        let validFiles = [];
        let totalSize = 0;
        
        // Get existing files from the file input
        const existingFiles = Array.from(this.fileInput.files || []);
        
        for (const file of files) {
            if (this.validateFile(file)) {
                validFiles.push(file);
                totalSize += file.size;
            }
        }
        
        if (totalSize > this.maxSize) {
            showToast('Total file size exceeds the maximum allowed size.', 'error');
            return;
        }
        
        // Update the file input with all files
        const dataTransfer = new DataTransfer();
        [...existingFiles, ...validFiles].forEach(file => dataTransfer.items.add(file));
        this.fileInput.files = dataTransfer.files;
        
        // Update the local files array
        this.files = Array.from(this.fileInput.files);
        this.renderFileList();
    }
    
    validateFile(file) {
        if (file.size > this.maxSize) {
            showToast(`${file.name} exceeds the maximum file size.`, 'error');
            return false;
        }
        
        if (this.allowedTypes.length > 0) {
            const ext = file.name.split('.').pop().toLowerCase();
            if (!this.allowedTypes.includes(ext)) {
                showToast(`${file.name} is not an allowed file type.`, 'error');
                return false;
            }
        }
        
        return true;
    }
    
    renderFileList() {
        if (!this.fileList) return;
        
        const files = Array.from(this.fileInput.files || []);
        this.files = files;
        
        if (files.length === 0) {
            this.fileList.innerHTML = '';
            return;
        }
        
        this.fileList.innerHTML = files.map((file, index) => `
            <div class="file-item" data-index="${index}">
                <i class="bi ${this.getFileIcon(file)}"></i>
                <div class="file-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatSize(file.size)}</span>
                </div>
                <button class="file-remove" data-index="${index}">
                    <i class="bi bi-x-circle"></i>
                </button>
            </div>
        `).join('');
        
        this.fileList.querySelectorAll('.file-remove').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.index);
                this.removeFile(index);
            });
        });
    }
    
    removeFile(index) {
        const files = Array.from(this.fileInput.files || []);
        files.splice(index, 1);
        
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        this.fileInput.files = dataTransfer.files;
        this.files = Array.from(this.fileInput.files);
        this.renderFileList();
    }
    
    getFileIcon(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        const icons = {
            'jpg': 'bi-file-image', 'jpeg': 'bi-file-image', 'png': 'bi-file-image',
            'gif': 'bi-file-image', 'webp': 'bi-file-image', 'svg': 'bi-file-image',
            'mp4': 'bi-film', 'avi': 'bi-film', 'mov': 'bi-film', 'webm': 'bi-film',
            'mp3': 'bi-music-note', 'wav': 'bi-music-note', 'aac': 'bi-music-note',
            'pdf': 'bi-file-pdf', 'doc': 'bi-file-word', 'docx': 'bi-file-word',
            'xls': 'bi-file-excel', 'xlsx': 'bi-file-excel',
            'ppt': 'bi-file-ppt', 'pptx': 'bi-file-ppt',
            'zip': 'bi-file-zip', 'rar': 'bi-file-zip', '7z': 'bi-file-zip',
            'js': 'bi-file-code', 'py': 'bi-file-code', 'html': 'bi-file-code',
            'css': 'bi-file-code', 'json': 'bi-file-code', 'xml': 'bi-file-code'
        };
        return icons[ext] || 'bi-file-earmark';
    }
    
    formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
        return (bytes / 1073741824).toFixed(1) + ' GB';
    }
    
    getFiles() {
        return Array.from(this.fileInput.files || []);
    }
    
    clearFiles() {
        this.fileInput.value = '';
        this.files = [];
        this.renderFileList();
        if (this.progressBar) {
            this.progressBar.style.display = 'none';
        }
    }
    
    showProgress(percentage, text) {
        if (this.progressBar) {
            this.progressBar.style.display = 'block';
        }
        if (this.progressFill) {
            this.progressFill.style.width = percentage + '%';
        }
        if (this.progressText) {
            this.progressText.textContent = text || `${Math.round(percentage)}%`;
        }
    }
}

let uploadManager = null;

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('uploadArea')) {
        uploadManager = new FileUploadManager({
            maxSize: 104857600,
            allowedTypes: []
        });
    }
});

// Toast notification helper
function showToast(message, type = 'success') {
    const existingToast = document.querySelector('.notification-toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        box-shadow: var(--glass-shadow);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 9999;
        animation: slideUp 0.3s ease;
        font-size: 0.95rem;
        max-width: 90%;
    `;

    const icons = {
        success: 'bi-check-circle',
        error: 'bi-x-circle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    };

    toast.innerHTML = `
        <i class="bi ${icons[type] || icons.success}" style="color: var(--${type}, var(--primary));"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;font-size:1.2rem;cursor:pointer;color:var(--text-light);">&times;</button>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(20px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }
    }, 3000);
}
