document.addEventListener('DOMContentLoaded', function() {
    initAttachmentPreview();
    initMediaPlayers();
    initSyntaxHighlighting();
});

function initAttachmentPreview() {
    document.querySelectorAll('.attachment-item .btn-icon[target="_blank"]').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href) {
                e.preventDefault();
                openPreview(href);
            }
        });
    });
}

function openPreview(url) {
    fetch(url)
        .then(response => {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.startsWith('image/')) {
                return response.blob().then(blob => ({ blob, type: 'image' }));
            } else if (contentType && contentType.startsWith('video/')) {
                return response.blob().then(blob => ({ blob, type: 'video' }));
            } else if (contentType && contentType.startsWith('audio/')) {
                return response.blob().then(blob => ({ blob, type: 'audio' }));
            } else if (contentType && contentType === 'application/pdf') {
                return response.blob().then(blob => ({ blob, type: 'pdf' }));
            } else {
                return response.text().then(text => ({ text, type: 'text' }));
            }
        })
        .then(data => {
            if (data.type === 'image') {
                createImagePreview(data.blob);
            } else if (data.type === 'video') {
                createVideoPreview(data.blob);
            } else if (data.type === 'audio') {
                createAudioPreview(data.blob);
            } else if (data.type === 'pdf') {
                createPDFPreview(data.blob);
            } else if (data.type === 'text') {
                createTextPreview(data.text);
            }
        })
        .catch(() => {
            window.open(url, '_blank');
        });
}

function createImagePreview(blob) {
    const url = URL.createObjectURL(blob);
    const modal = createModal(`
        <div class="image-preview-container">
            <img src="${url}" alt="Preview" class="preview-image">
            <div class="preview-controls">
                <button onclick="zoomImage('in')"><i class="bi bi-zoom-in"></i></button>
                <button onclick="zoomImage('out')"><i class="bi bi-zoom-out"></i></button>
                <button onclick="resetZoom()"><i class="bi bi-arrows-expand"></i></button>
                <button onclick="downloadPreview()"><i class="bi bi-download"></i></button>
            </div>
        </div>
    `);
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

function createVideoPreview(blob) {
    const url = URL.createObjectURL(blob);
    const modal = createModal(`
        <div class="video-preview-container">
            <video controls class="preview-video">
                <source src="${url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="video-controls">
                <button onclick="togglePlay()"><i class="bi bi-play"></i></button>
                <input type="range" min="0" max="100" value="0" id="progressControl">
                <button onclick="toggleMute()"><i class="bi bi-volume-up"></i></button>
                <button onclick="toggleFullscreen()"><i class="bi bi-fullscreen"></i></button>
                <button onclick="togglePIP()"><i class="bi bi-pip"></i></button>
            </div>
        </div>
    `);
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    
    const video = modal.querySelector('video');
    const progress = modal.querySelector('#progressControl');
    
    video.addEventListener('timeupdate', () => {
        progress.value = (video.currentTime / video.duration) * 100;
    });
    
    progress.addEventListener('input', () => {
        video.currentTime = (progress.value / 100) * video.duration;
    });
}

function createAudioPreview(blob) {
    const url = URL.createObjectURL(blob);
    const modal = createModal(`
        <div class="audio-preview-container">
            <div class="audio-waveform">
                <canvas id="waveform"></canvas>
            </div>
            <audio controls class="preview-audio">
                <source src="${url}" type="audio/mpeg">
                Your browser does not support the audio tag.
            </audio>
            <div class="audio-controls">
                <button onclick="toggleAudioPlay()"><i class="bi bi-play"></i></button>
                <input type="range" min="0" max="100" value="0" id="audioProgress">
                <span id="audioTime">0:00</span>
                <button onclick="toggleAudioVolume()"><i class="bi bi-volume-up"></i></button>
                <input type="range" min="0" max="100" value="100" id="audioVolume">
            </div>
        </div>
    `);
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    
    const audio = modal.querySelector('audio');
    const progress = modal.querySelector('#audioProgress');
    const time = modal.querySelector('#audioTime');
    const volume = modal.querySelector('#audioVolume');
    
    audio.addEventListener('timeupdate', () => {
        progress.value = (audio.currentTime / audio.duration) * 100;
        time.textContent = formatTime(audio.currentTime);
    });
    
    progress.addEventListener('input', () => {
        audio.currentTime = (progress.value / 100) * audio.duration;
    });
    
    volume.addEventListener('input', () => {
        audio.volume = volume.value / 100;
    });
    
    drawWaveform(modal.querySelector('#waveform'));
}

function createPDFPreview(blob) {
    const url = URL.createObjectURL(blob);
    const modal = createModal(`
        <div class="pdf-preview-container">
            <iframe src="${url}" class="preview-pdf"></iframe>
            <div class="pdf-controls">
                <button onclick="downloadPreview()"><i class="bi bi-download"></i></button>
                <button onclick="printPreview()"><i class="bi bi-printer"></i></button>
            </div>
        </div>
    `);
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

function createTextPreview(text) {
    const modal = createModal(`
        <div class="text-preview-container">
            <div class="text-controls">
                <button onclick="copyText()"><i class="bi bi-copy"></i></button>
                <button onclick="downloadPreview()"><i class="bi bi-download"></i></button>
            </div>
            <pre class="preview-text"><code>${escapeHtml(text)}</code></pre>
        </div>
    `);
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    initSyntaxHighlighting(modal);
}

function createModal(content) {
    const modal = document.createElement('div');
    modal.className = 'preview-modal';
    modal.innerHTML = `
        <div class="preview-content">
            <button class="preview-close" onclick="closePreview()">
                <i class="bi bi-x-lg"></i>
            </button>
            ${content}
        </div>
    `;
    
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            closePreview();
        }
    });
    
    return modal;
}

function closePreview() {
    const modal = document.querySelector('.preview-modal');
    if (modal) {
        modal.remove();
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function drawWaveform(canvas) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 80;
    
    const bars = 60;
    const barWidth = (canvas.width - 20) / bars;
    
    ctx.fillStyle = 'rgba(79, 140, 255, 0.3)';
    for (let i = 0; i < bars; i++) {
        const height = Math.random() * 60 + 10;
        const x = 10 + i * barWidth;
        const y = (canvas.height - height) / 2;
        ctx.fillRect(x, y, barWidth - 2, height);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function initSyntaxHighlighting(container) {
    const codeBlocks = (container || document).querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const text = block.textContent;
        const lines = text.split('\n');
        let html = '';
        lines.forEach(line => {
            let highlighted = line;
            highlighted = highlighted.replace(/\/\/.*/g, '<span class="comment">$&</span>');
            highlighted = highlighted.replace(/".*?"/g, '<span class="string">$&</span>');
            highlighted = highlighted.replace(/\b(function|return|var|let|const|if|else|for|while|class|import|export|default|new|this|typeof|instanceof)\b/g, 
                '<span class="keyword">$&</span>');
            html += highlighted + '\n';
        });
        block.innerHTML = html;
    });
}

const previewStyle = document.createElement('style');
previewStyle.textContent = `
    .preview-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        z-index: 10000;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .preview-content {
        background: white;
        border-radius: 20px;
        max-width: 90vw;
        max-height: 90vh;
        overflow: auto;
        position: relative;
        padding: 2rem;
    }
    
    .preview-close {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: var(--glass-bg);
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 1.5rem;
        cursor: pointer;
        transition: var(--transition);
        z-index: 1;
    }
    
    .preview-close:hover {
        background: var(--error);
        color: white;
        transform: rotate(90deg);
    }
    
    .preview-image {
        max-width: 100%;
        max-height: 80vh;
        object-fit: contain;
    }
    
    .preview-video {
        max-width: 100%;
        max-height: 70vh;
    }
    
    .preview-pdf {
        width: 100%;
        height: 80vh;
        border: none;
    }
    
    .preview-text {
        max-width: 100%;
        max-height: 80vh;
        overflow: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .preview-text .comment { color: #6a9955; }
    .preview-text .string { color: #ce9178; }
    .preview-text .keyword { color: #569cd6; font-weight: bold; }
    
    .preview-controls,
    .video-controls,
    .audio-controls,
    .text-controls,
    .pdf-controls {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
        align-items: center;
    }
    
    .preview-controls button,
    .video-controls button,
    .audio-controls button {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 8px;
        padding: 0.5rem;
        cursor: pointer;
        transition: var(--transition);
    }
    
    .preview-controls button:hover,
    .video-controls button:hover,
    .audio-controls button:hover {
        background: var(--primary);
        color: white;
    }
    
    .video-controls input[type="range"],
    .audio-controls input[type="range"] {
        flex: 1;
        min-width: 100px;
        accent-color: var(--primary);
    }
`;
document.head.appendChild(previewStyle);