// File upload handling
const pdfFileInput = document.getElementById('pdf-file-input');
const pdfUploadArea = document.querySelector('#pdf-upload-area');
const pdfPreviewContainer = document.querySelector('#pdf-preview-container');
const imageList = document.querySelector('#image-list');
const pdfForm = document.querySelector('#pdf-form');
const resultModal = document.getElementById('pdf-result-modal');
const closeModalBtn = resultModal.querySelector('.close-modal');
const downloadBtn = resultModal.querySelector('.download-button');

let files = [];

// Initialize Sortable for drag-and-drop reordering
const sortable = new Sortable(imageList, {
    animation: 150,
    ghostClass: 'sortable-ghost',
    onEnd: updateImageOrder
});

// File Input Change Handler
pdfFileInput.addEventListener('change', handleFileSelect);

// Drag and Drop Handlers
pdfUploadArea.addEventListener('dragover', handleDragOver);
pdfUploadArea.addEventListener('dragleave', handleDragLeave);
pdfUploadArea.addEventListener('drop', handleDrop);
pdfUploadArea.addEventListener('click', () => pdfFileInput.click());

// Form Submit Handler
pdfForm.addEventListener('submit', handleSubmit);

// Close Modal Handler
closeModalBtn.addEventListener('click', () => {
    resultModal.style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === resultModal) {
        resultModal.style.display = 'none';
    }
});

// Handle image removal
imageList.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-image')) {
        const imageItem = e.target.closest('.image-item');
        const index = parseInt(imageItem.dataset.index);
        files.splice(index, 1);
        updatePreview();
        
        if (files.length === 0) {
            pdfPreviewContainer.style.display = 'none';
            pdfUploadArea.style.display = 'block';
        }
    }
});

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    pdfUploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    pdfUploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    pdfUploadArea.classList.remove('dragover');
    
    const newFiles = Array.from(e.dataTransfer.files).filter(file => {
        if (!file.type.startsWith('image/')) {
            alert(`File "${file.name}" is not an image. Please select only image files.`);
            return false;
        }
        if (file.size > 10 * 1024 * 1024) {
            alert(`File "${file.name}" exceeds 10MB limit.`);
            return false;
        }
        return true;
    });
    
    if (newFiles.length > 0) {
        addFiles(newFiles);
    }
}

function handleFileSelect(e) {
    const newFiles = Array.from(e.target.files).filter(file => {
        if (!file.type.startsWith('image/')) {
            alert(`File "${file.name}" is not an image. Please select only image files.`);
            return false;
        }
        if (file.size > 10 * 1024 * 1024) {
            alert(`File "${file.name}" exceeds 10MB limit.`);
            return false;
        }
        return true;
    });
    
    if (newFiles.length > 0) {
        addFiles(newFiles);
    }
}

function addFiles(newFiles) {
    files = [...files, ...newFiles];
    updatePreview();
}

function updatePreview() {
    imageList.innerHTML = '';
    
    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageItem = document.createElement('div');
            imageItem.className = 'image-item';
            imageItem.dataset.index = index;
            
            imageItem.innerHTML = `
                <div class="image-preview">
                    <img src="${e.target.result}" alt="Preview">
                    <span class="image-number">${index + 1}</span>
                </div>
                <div class="image-controls">
                    <button type="button" class="remove-image">×</button>
                </div>
            `;
            
            imageList.appendChild(imageItem);
        };
        reader.readAsDataURL(file);
    });
    
    pdfPreviewContainer.style.display = 'block';
    pdfUploadArea.style.display = 'none';
}

function updateImageOrder() {
    const newFiles = [];
    const items = imageList.querySelectorAll('.image-item');
    
    items.forEach(item => {
        const index = parseInt(item.dataset.index);
        newFiles.push(files[index]);
    });
    
    files = newFiles;
}

async function handleSubmit(e) {
    e.preventDefault();
    
    if (files.length === 0) {
        alert('Please select at least one image');
        return;
    }
    
    const convertBtn = pdfForm.querySelector('.convert-btn');
    convertBtn.disabled = true;
    convertBtn.classList.add('loading');
    
    const formData = new FormData();
    
    // Add PDF name if provided
    const pdfName = document.getElementById('pdf-name').value;
    if (pdfName) {
        formData.append('pdf_name', pdfName);
    }
    
    // Add files
    files.forEach(file => {
        formData.append('files', file);
    });
    
    try {
        const response = await fetch('/convert-to-pdf', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResultModal(result);
            // Reset form
            files = [];
            updatePreview();
            pdfForm.reset();
        } else {
            throw new Error(result.error || 'Failed to convert images to PDF');
        }
    } catch (error) {
        alert(error.message);
    } finally {
        convertBtn.disabled = false;
        convertBtn.classList.remove('loading');
    }
}

function showResultModal(result) {
    const modal = document.getElementById('pdf-result-modal');
    const pdfName = modal.querySelector('.pdf-name');
    const pageCount = modal.querySelector('.page-count');
    const fileSize = modal.querySelector('.file-size');
    const downloadBtn = modal.querySelector('.download-button');
    
    // Update modal content
    pdfName.textContent = result.filename;
    pageCount.textContent = result.page_count;
    fileSize.textContent = formatFileSize(result.file_size);
    downloadBtn.href = result.download_url;
    
    // Show modal
    modal.style.display = 'flex';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
} 