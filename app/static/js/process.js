// File upload handling
const fileInput = document.getElementById('file-input');
const uploadArea = document.querySelector('.upload-area');
const previewContainer = document.querySelector('.preview-container');
const imagePreview = document.querySelector('.image-preview');
const removeButton = document.querySelector('.remove-file');

// Initialize state
let originalWidth = 0;
let originalHeight = 0;

// Handle file selection
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            alert('Please select a valid image file (JPG, PNG, GIF, or WebP)');
            fileInput.value = '';
            return;
        }

        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size exceeds 10MB limit');
            fileInput.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                // Set the preview image
                imagePreview.src = e.target.result;
                
                // Calculate dimensions to fit container while maintaining aspect ratio
                const containerWidth = previewContainer.clientWidth - 32; // Account for padding
                const containerHeight = 280; // Max height
                
                const ratio = Math.min(
                    containerWidth / img.width,
                    containerHeight / img.height
                );
                
                imagePreview.style.width = `${img.width * ratio}px`;
                imagePreview.style.height = `${img.height * ratio}px`;
                
                // Show preview container and hide upload area
                previewContainer.style.display = 'block';
                uploadArea.style.display = 'none';
                
                // Set initial dimensions
                widthInput.value = img.width;
                heightInput.value = img.height;
                originalWidth = img.width;
                originalHeight = img.height;
            };
            img.onerror = function() {
                alert('Error loading image');
                fileInput.value = '';
            };
            img.src = e.target.result;
        };
        reader.onerror = function() {
            alert('Error reading file');
            fileInput.value = '';
        };
        reader.readAsDataURL(file);
    }
});

// Handle drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
    fileInput.dispatchEvent(new Event('change'));
});

// Handle remove file
removeButton.addEventListener('click', () => {
    fileInput.value = '';
    imagePreview.src = '';
    previewContainer.style.display = 'none';
    uploadArea.style.display = 'flex';
    widthInput.value = '';
    heightInput.value = '';
    originalWidth = 0;
    originalHeight = 0;
});

// Maintain aspect ratio checkbox handling
const maintainAspectRatio = document.querySelector('#maintain-aspect-ratio');
const widthInput = document.querySelector('#width');
const heightInput = document.querySelector('#height');

function updateDimensions(input, otherInput, ratio) {
    if (maintainAspectRatio.checked && originalWidth && originalHeight) {
        const value = parseInt(input.value);
        if (!isNaN(value) && value > 0) {
            otherInput.value = Math.round(value * ratio);
        }
    }
}

widthInput.addEventListener('input', () => {
    updateDimensions(widthInput, heightInput, originalHeight / originalWidth);
});

heightInput.addEventListener('input', () => {
    updateDimensions(heightInput, widthInput, originalWidth / originalHeight);
});

// Quality slider value display
const qualitySlider = document.querySelector('#quality');
const qualityValue = document.querySelector('.quality-value');

qualitySlider.addEventListener('input', () => {
    qualityValue.textContent = qualitySlider.value + '%';
});

// Form submission handling
const form = document.querySelector('form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitButton = form.querySelector('.submit-button');
    submitButton.classList.add('loading');
    
    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Server error');
        }
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Show result modal
        const modal = document.querySelector('.result-modal');
        const resultPreview = modal.querySelector('.result-preview img');
        const originalSize = modal.querySelector('.original-size');
        const newSize = modal.querySelector('.new-size');
        const reduction = modal.querySelector('.reduction');
        const downloadButton = modal.querySelector('.download-button');
        
        resultPreview.src = result.preview_url;
        originalSize.textContent = formatFileSize(result.original_size);
        newSize.textContent = formatFileSize(result.new_size);
        reduction.textContent = `${result.reduction}%`;
        downloadButton.href = result.download_url;
        
        // Set proper filename for download
        const filename = result.filename || 'processed_image.jpg';
        downloadButton.setAttribute('download', filename);
        
        modal.style.display = 'flex';

        // Add event listeners for modal closing
        const closeBtn = modal.querySelector('.close-modal');
        closeBtn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            modal.style.display = 'none';
            resetForm();
        };

        // Close when clicking outside
        modal.onclick = function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
                resetForm();
            }
        };

    } catch (error) {
        alert(error.message || 'An error occurred while processing your image');
    } finally {
        submitButton.classList.remove('loading');
    }
});

// Helper function to reset form
function resetForm() {
    form.reset();
    imagePreview.src = '';
    previewContainer.style.display = 'none';
    uploadArea.style.display = 'flex';
    originalWidth = 0;
    originalHeight = 0;
}

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    const modal = document.querySelector('.result-modal');
    if (e.key === 'Escape' && modal.style.display === 'flex') {
        modal.style.display = 'none';
        resetForm();
    }
});

// Helper function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
} 