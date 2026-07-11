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
        
        this.init();
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
        this.fileInput.value = '';
    }
    
    addFiles(files) {
        let validFiles = [];
        let totalSize = 0;
        
        for (const file of files) {
            if (this.validateFile(file)) {
                validFiles.push(file);
                totalSize += file.size;
            }
        }
        
        if (totalSize > this.maxSize) {
            notifications.error('Total file size exceeds the maximum allowed size.');
            return;
        }
        
        this.files = [...this.files, ...validFiles];
        this.renderFileList();
    }
    
    validateFile(file) {
        if (file.size > this.maxSize) {
            notifications.error(`${file.name} exceeds the maximum file size.`);
            return false;
        }
        
        if (this.allowedTypes.length > 0) {
            const ext = file.name.split('.').pop().toLowerCase();
            if (!this.allowedTypes.includes(ext)) {
                notifications.error(`${file.name} is not an allowed file type.`);
                return false;
            }
        }
        
        return true;
    }
    
    renderFileList() {
        if (!this.fileList) return;
        
        if (this.files.length === 0) {
            this.fileList.innerHTML = '';
            return;
        }
        
        this.fileList.innerHTML = this.files.map((file, index) => `
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
        this.files.splice(index, 1);
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
        return this.files;
    }
    
    clearFiles() {
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