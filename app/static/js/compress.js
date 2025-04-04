// File upload handling
const fileInput = document.querySelector('.file-input');
const uploadArea = document.querySelector('.upload-area');
const previewContainer = document.querySelector('.preview-container');
const removeButton = document.querySelector('.remove-file');
const imagePreview = document.querySelector('.image-preview');

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            // Create a new image to ensure proper loading
            const img = new Image();
            img.onload = () => {
                // Set the preview image
                imagePreview.src = e.target.result;
                imagePreview.style.width = 'auto';
                imagePreview.style.height = 'auto';
                imagePreview.style.maxWidth = '100%';
                imagePreview.style.maxHeight = '280px';
                
                // Show preview container
                previewContainer.style.display = 'flex';
                uploadArea.style.display = 'none';
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

removeButton.addEventListener('click', () => {
    imagePreview.src = '';
    previewContainer.style.display = 'none';
    uploadArea.style.display = 'block';
    fileInput.value = '';
});

// Form submission handling
const form = document.querySelector('form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitButton = form.querySelector('.submit-button');
    const buttonText = submitButton.querySelector('span');
    const loader = submitButton.querySelector('.button-loader');
    
    // Show loading state
    submitButton.classList.add('loading');
    
    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResultModal(result);
        } else {
            alert(result.error || 'An error occurred');
        }
    } catch (error) {
        alert('An error occurred while processing your request');
    } finally {
        // Reset loading state
        submitButton.classList.remove('loading');
    }
});

// Result modal handling
const resultModal = document.querySelector('.result-modal');
const closeModal = document.querySelector('.close-modal');
const resultPreview = document.querySelector('.result-preview img');
const originalSize = document.querySelector('.original-size');
const newSize = document.querySelector('.new-size');
const reduction = document.querySelector('.reduction');
const downloadButton = document.querySelector('.download-button');

function showResultModal(result) {
    // Add a timestamp to prevent browser caching
    const timestamp = new Date().getTime();
    resultPreview.src = `${result.preview_url}?t=${timestamp}`;
    
    // Log the image URL for debugging
    console.log('Preview URL:', resultPreview.src);
    
    originalSize.textContent = formatFileSize(result.original_size);
    newSize.textContent = formatFileSize(result.new_size);
    reduction.textContent = result.reduction + '%';
    downloadButton.href = result.download_url;
    
    resultModal.style.display = 'flex';
    
    // Animate modal entrance
    gsap.from('.modal-content', {
        duration: 0.5,
        y: 50,
        opacity: 0,
        ease: 'power3.out'
    });
    
    // Add error handling for the image
    resultPreview.onerror = function() {
        console.error('Error loading image:', resultPreview.src);
        alert('Error loading the preview image. Please try again.');
    };
}

closeModal.addEventListener('click', () => {
    gsap.to('.modal-content', {
        duration: 0.3,
        y: 50,
        opacity: 0,
        ease: 'power3.in',
        onComplete: () => {
            resultModal.style.display = 'none';
        }
    });
});

// Helper function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Quality slider value display
const qualitySlider = document.querySelector('#quality');
const qualityValue = document.querySelector('.quality-value');

qualitySlider.addEventListener('input', () => {
    qualityValue.textContent = qualitySlider.value + '%';
}); 