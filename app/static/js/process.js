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
if (fileInput) {
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
                    if (imagePreview) {
                        imagePreview.src = e.target.result;
                        
                        // Calculate dimensions to fit container while maintaining aspect ratio
                        if (previewContainer) {
                            const containerWidth = previewContainer.clientWidth - 32; // Account for padding
                            const containerHeight = 280; // Max height
                            
                            const ratio = Math.min(
                                containerWidth / img.width,
                                containerHeight / img.height
                            );
                            
                            imagePreview.style.width = `${img.width * ratio}px`;
                            imagePreview.style.height = `${img.height * ratio}px`;
                        }
                    }
                    
                    // Show preview container and hide upload area
                    if (previewContainer) previewContainer.style.display = 'flex';
                    if (uploadArea) uploadArea.style.display = 'none';
                    
                    // Store original dimensions
                    originalWidth = img.width;
                    originalHeight = img.height;
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
}

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
    const form = document.querySelector('form');
    if (form) form.reset();
    
    if (imagePreview) imagePreview.src = '';
    if (previewContainer) previewContainer.style.display = 'none';
    if (uploadArea) uploadArea.style.display = 'flex';
    
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

document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const form = document.getElementById('process-form');
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.querySelector('.file-name');
    const removeFileBtn = document.querySelector('.remove-file');
    const uploadArea = document.querySelector('.upload-area');
    const fileInfo = document.querySelector('.file-info');

    // Step navigation
    const steps = {
        1: document.getElementById('step-1'),
        2: document.getElementById('step-2'),
        3: document.getElementById('step-3')
    };

    // Process type selection
    const processOptions = document.querySelectorAll('.process-option');
    const resizeOptions = document.getElementById('resize-options');
    const compressOptions = document.getElementById('compress-options');

    // Navigation buttons
    const nextToStep2Btn = document.getElementById('next-to-step-2');
    const nextToStep3Btn = document.getElementById('next-to-step-3');
    const backToStep1Btn = document.getElementById('back-to-step-1');
    const backToStep2Btn = document.getElementById('back-to-step-2');

    // Result modal
    const resultModal = document.querySelector('.result-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const restartBtn = document.querySelector('.restart-button');
    const downloadBtn = document.querySelector('.download-button');

    // Quality slider
    const qualitySlider = document.getElementById('quality');
    const qualityValue = document.querySelector('.quality-value');

    let selectedProcessType = null;

    // File upload handling
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Display file name instead of preview
            fileNameDisplay.textContent = file.name;
            fileInfo.style.display = 'flex';
            uploadArea.style.display = 'none';
            removeFileBtn.style.display = 'block';
        }
    });

    // Remove file
    removeFileBtn.addEventListener('click', function() {
        fileInput.value = '';
        fileNameDisplay.textContent = '';
        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
        removeFileBtn.style.display = 'none';
    });

    // Drag and drop handling
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            fileInput.files = e.dataTransfer.files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });

    // Step navigation
    nextToStep2Btn.addEventListener('click', function() {
        if (fileInput.files.length > 0) {
            steps[1].style.display = 'none';
            steps[2].style.display = 'block';
        } else {
            alert('Please select an image first');
        }
    });

    nextToStep3Btn.addEventListener('click', function() {
        if (selectedProcessType) {
            steps[2].style.display = 'none';
            steps[3].style.display = 'block';
            
            // Show appropriate options based on selected process type
            if (selectedProcessType === 'resize') {
                resizeOptions.style.display = 'block';
                compressOptions.style.display = 'none';
                form.action = '/resize';
            } else {
                resizeOptions.style.display = 'none';
                compressOptions.style.display = 'block';
                form.action = '/compress';
            }
        } else {
            alert('Please select a process type');
        }
    });

    backToStep1Btn.addEventListener('click', function() {
        steps[2].style.display = 'none';
        steps[1].style.display = 'block';
    });

    backToStep2Btn.addEventListener('click', function() {
        steps[3].style.display = 'none';
        steps[2].style.display = 'block';
    });

    // Process type selection
    processOptions.forEach(option => {
        option.addEventListener('click', function() {
            processOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            selectedProcessType = this.dataset.type;
        });
    });

    // Quality slider update
    qualitySlider.addEventListener('input', function() {
        qualityValue.textContent = this.value + '%';
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitButton = form.querySelector('.submit-button');
        const buttonLoader = submitButton.querySelector('.button-loader');
        
        submitButton.disabled = true;
        buttonLoader.style.display = 'block';

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Update result modal
            document.querySelector('.result-preview img').src = data.preview_url;
            document.querySelector('.original-size').textContent = formatFileSize(data.original_size);
            document.querySelector('.new-size').textContent = formatFileSize(data.new_size);
            document.querySelector('.reduction').textContent = data.reduction + '%';
            downloadBtn.href = data.download_url;
            
            // Show result modal
            resultModal.style.display = 'flex';
        })
        .catch(error => {
            alert(error.message || 'An error occurred while processing the image');
        })
        .finally(() => {
            submitButton.disabled = false;
            buttonLoader.style.display = 'none';
        });
    });

    // Modal handling
    closeModalBtn.addEventListener('click', function() {
        resultModal.style.display = 'none';
    });

    restartBtn.addEventListener('click', function() {
        resultModal.style.display = 'none';
        form.reset();
        fileNameDisplay.textContent = '';
        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
        removeFileBtn.style.display = 'none';
        processOptions.forEach(opt => opt.classList.remove('selected'));
        selectedProcessType = null;
        steps[3].style.display = 'none';
        steps[2].style.display = 'none';
        steps[1].style.display = 'block';
    });

    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}); 