// ============================================
// FILE CRYPTO - JAVASCRIPT
// Lógica de Upload, Criptografia e Gerenciamento
// ============================================

// ============================================
// CONFIGURAÇÕES E CONSTANTES
// ============================================

const EXTENSION_MAP = {
    'ad3': 'mp3',
    'vd4': 'mp4',
    'ph': 'png',
    'sz': 'jpg',
    'ssz': 'jpeg',
    'jsn': 'json',
    'sc': 'js',
    'sty': 'css',
    'hyp': 'html'
};

const REVERSE_EXTENSION_MAP = Object.fromEntries(
    Object.entries(EXTENSION_MAP).map(([k, v]) => [v, k])
);

// ============================================
// ELEMENTOS DO DOM
// ============================================

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const filesGrid = document.getElementById('filesGrid');
const fileCount = document.getElementById('fileCount');
const tabBtns = document.querySelectorAll('.tab-btn');
const previewModal = document.getElementById('previewModal');
const closePreviewBtn = document.getElementById('closePreviewBtn');
const closePreviewBtnFooter = document.getElementById('closePreviewBtnFooter');
const downloadPreviewBtn = document.getElementById('downloadPreviewBtn');
const toastContainer = document.getElementById('toastContainer');

// ============================================
// VARIÁVEIS GLOBAIS
// ============================================

let currentCategory = 'all';
let currentPreviewFile = null;

// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadFiles();
    console.log('✅ File Crypto inicializado com sucesso!');
    console.log('🔐 Criptografia AES-256-GCM ativada');
});

function initializeEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Tab buttons
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => handleTabChange(btn));
    });

    // Modal close
    closePreviewBtn.addEventListener('click', closePreview);
    closePreviewBtnFooter.addEventListener('click', closePreview);
    downloadPreviewBtn.addEventListener('click', downloadPreviewFile);

    // Modal background click
    previewModal.addEventListener('click', (e) => {
        if (e.target === previewModal) closePreview();
    });
}

// ============================================
// DRAG AND DROP HANDLERS
// ============================================

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect({ target: { files } });
    }
}

// ============================================
// FILE SELECTION HANDLER
// ============================================

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length === 0) return;

    const file = files[0];
    displayFileInfo(file);
    uploadFile(file);
}

function displayFileInfo(file) {
    const size = (file.size / 1024).toFixed(2);
    const type = file.type || 'Tipo desconhecido';
    fileInfo.textContent = `📄 ${file.name} (${size} KB) - ${type}`;
}

// ============================================
// FILE UPLOAD
// ============================================

async function uploadFile(file) {
    try {
        showUploadProgress();

        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();

        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                updateProgressBar(percentComplete);
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    showToast('Arquivo criptografado e salvo com sucesso!', 'success');
                    hideUploadProgress();
                    fileInfo.textContent = '';
                    fileInput.value = '';
                    loadFiles();
                } else {
                    showToast(response.error || 'Erro ao fazer upload', 'error');
                    hideUploadProgress();
                }
            } else {
                const response = JSON.parse(xhr.responseText);
                showToast(response.error || 'Erro ao fazer upload', 'error');
                hideUploadProgress();
            }
        });

        xhr.addEventListener('error', () => {
            showToast('Erro na conexão ao fazer upload', 'error');
            hideUploadProgress();
        });

        xhr.open('POST', '/api/upload');
        xhr.send(formData);

    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        showToast('Erro ao fazer upload do arquivo', 'error');
        hideUploadProgress();
    }
}

function showUploadProgress() {
    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Enviando arquivo...';
}

function hideUploadProgress() {
    setTimeout(() => {
        uploadProgress.style.display = 'none';
    }, 500);
}

function updateProgressBar(percent) {
    progressFill.style.width = percent + '%';
    progressText.textContent = `Enviando arquivo... ${Math.round(percent)}%`;
}

// ============================================
// FILE LOADING AND DISPLAY
// ============================================

async function loadFiles() {
    try {
        const response = await fetch(`/api/files?category=${currentCategory}`);
        const data = await response.json();

        if (data.success) {
            displayFiles(data.files);
            updateFileCount(data.files.length);
        }
    } catch (error) {
        console.error('Erro ao carregar arquivos:', error);
        showToast('Erro ao carregar arquivos', 'error');
    }
}

function displayFiles(files) {
    filesGrid.innerHTML = '';

    if (files.length === 0) {
        filesGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📁</div>
                <p>Nenhum arquivo encontrado</p>
                <small>Comece enviando um arquivo para criptografar</small>
            </div>
        `;
        return;
    }

    files.forEach(file => {
        const fileCard = createFileCard(file);
        filesGrid.appendChild(fileCard);
    });
}

function createFileCard(file) {
    const card = document.createElement('div');
    card.className = 'file-card';

    const icon = getFileIcon(file.category, file.realExtension);
    const uploadDate = new Date(file.uploadedAt).toLocaleDateString('pt-BR');

    card.innerHTML = `
        <div class="file-icon">${icon}</div>
        <div class="file-name" title="${file.originalName}">${file.originalName}</div>
        <div class="file-meta">
            <span class="file-ext">${file.extension}</span>
            <span>${file.sizeFormatted}</span>
        </div>
        <div class="file-meta">
            <span>${uploadDate}</span>
        </div>
        <div class="file-actions">
            <button class="file-btn file-btn-preview" data-file="${file.id}" onclick="previewFile('${file.id}')">
                <span class="btn-icon">👁️</span>
                <span>Preview</span>
            </button>
            <button class="file-btn file-btn-download" data-file="${file.id}" onclick="downloadFile('${file.id}', '${file.originalName}', '${file.realExtension}')">
                <span class="btn-icon">⬇️</span>
                <span>Download</span>
            </button>
            <button class="file-btn file-btn-delete" data-file="${file.id}" onclick="deleteFile('${file.id}')">
                <span class="btn-icon">🗑️</span>
                <span>Deletar</span>
            </button>
        </div>
    `;

    return card;
}

function getFileIcon(category, extension) {
    const iconMap = {
        'audio': '🎵',
        'image': '🖼️',
        'json': '{ }',
        'encrypted': '🔒',
        'other': '📄'
    };
    return iconMap[category] || '📄';
}

function updateFileCount(count) {
    fileCount.textContent = `${count} arquivo${count !== 1 ? 's' : ''}`;
}

// ============================================
// TAB NAVIGATION
// ============================================

function handleTabChange(btn) {
    // Remove active class from all tabs
    tabBtns.forEach(b => b.classList.remove('active'));
    
    // Add active class to clicked tab
    btn.classList.add('active');
    
    // Update current category
    currentCategory = btn.dataset.category;
    
    // Reload files
    loadFiles();
}

// ============================================
// FILE PREVIEW
// ============================================

async function previewFile(filename) {
    try {
        currentPreviewFile = filename;
        
        const response = await fetch(`/api/preview/${filename}`);
        const data = await response.json();

        if (!data.success) {
            showToast('Erro ao carregar preview', 'error');
            return;
        }

        clearAllPreviews();
        previewModal.style.display = 'flex';

        if (data.type === 'image') {
            showImagePreview(data.data);
        } else if (data.type === 'audio') {
            showAudioPreview(data.data);
        } else if (data.type === 'json') {
            showJsonPreview(data.data);
        } else if (data.type === 'text') {
            showTextPreview(data.data);
        }

    } catch (error) {
        console.error('Erro ao fazer preview:', error);
        showToast('Erro ao fazer preview do arquivo', 'error');
    }
}

function showImagePreview(dataUrl) {
    const preview = document.getElementById('imagePreview');
    const img = document.getElementById('previewImage');
    img.src = dataUrl;
    preview.style.display = 'flex';
    document.getElementById('previewTitle').textContent = 'Preview - Imagem';
}

function showAudioPreview(dataUrl) {
    const preview = document.getElementById('audioPreview');
    const audio = document.getElementById('previewAudio');
    audio.src = dataUrl;
    preview.style.display = 'flex';
    document.getElementById('previewTitle').textContent = 'Preview - Áudio';
}

function showJsonPreview(data) {
    const preview = document.getElementById('jsonPreview');
    const pre = document.getElementById('previewJson');
    
    if (typeof data === 'string') {
        pre.textContent = data;
    } else {
        pre.textContent = JSON.stringify(data, null, 2);
    }
    
    preview.style.display = 'flex';
    document.getElementById('previewTitle').textContent = 'Preview - JSON';
}

function showTextPreview(text) {
    const preview = document.getElementById('textPreview');
    const pre = document.getElementById('previewText');
    pre.textContent = text;
    preview.style.display = 'flex';
    document.getElementById('previewTitle').textContent = 'Preview - Texto';
}

function clearAllPreviews() {
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('audioPreview').style.display = 'none';
    document.getElementById('jsonPreview').style.display = 'none';
    document.getElementById('textPreview').style.display = 'none';
}

function closePreview() {
    previewModal.style.display = 'none';
    clearAllPreviews();
    currentPreviewFile = null;
}

// ============================================
// FILE DOWNLOAD
// ============================================

function downloadFile(filename, originalName, realExtension) {
    const link = document.createElement('a');
    link.href = `/api/decrypt/${filename}`;
    link.download = `${originalName}.${realExtension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Download iniciado!', 'success');
}

function downloadPreviewFile() {
    if (currentPreviewFile) {
        const filename = currentPreviewFile;
        const ext = filename.split('.').pop();
        const realExt = EXTENSION_MAP[ext] || ext;
        const originalName = filename.split('.')[0];
        downloadFile(filename, originalName, realExt);
    }
}

// ============================================
// FILE DELETION
// ============================================

async function deleteFile(filename) {
    if (!confirm('Tem certeza que deseja deletar este arquivo?')) {
        return;
    }

    try {
        const response = await fetch(`/api/delete/${filename}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Arquivo deletado com sucesso!', 'success');
            loadFiles();
        } else {
            showToast(data.error || 'Erro ao deletar arquivo', 'error');
        }
    } catch (error) {
        console.error('Erro ao deletar arquivo:', error);
        showToast('Erro ao deletar arquivo', 'error');
    }
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
