// Custom cursor
const cursor = document.querySelector('.cursor');
const cursorFollower = document.querySelector('.cursor-follower');

document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
    
    setTimeout(() => {
        cursorFollower.style.left = e.clientX + 'px';
        cursorFollower.style.top = e.clientY + 'px';
    }, 100);
});

// File upload handling
const fileInputs = document.querySelectorAll('.file-input');
const uploadAreas = document.querySelectorAll('.upload-area');
const previewContainers = document.querySelectorAll('.preview-container');
const removeButtons = document.querySelectorAll('.remove-file');

fileInputs.forEach((input, index) => {
    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = previewContainers[index].querySelector('.image-preview');
                preview.src = e.target.result;
                previewContainers[index].style.display = 'block';
                uploadAreas[index].style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });
});

removeButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
        const preview = previewContainers[index].querySelector('.image-preview');
        preview.src = '';
        previewContainers[index].style.display = 'none';
        uploadAreas[index].style.display = 'block';
        fileInputs[index].value = '';
    });
});

// Form submission handling
const forms = document.querySelectorAll('form');
forms.forEach(form => {
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
    resultPreview.src = result.preview_url;
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

// Maintain aspect ratio checkbox handling
const maintainAspectRatio = document.querySelector('#maintain-aspect-ratio');
const widthInput = document.querySelector('#width');
const heightInput = document.querySelector('#height');

let originalWidth = 0;
let originalHeight = 0;

widthInput.addEventListener('change', () => {
    if (maintainAspectRatio.checked && originalWidth && originalHeight) {
        const ratio = originalHeight / originalWidth;
        heightInput.value = Math.round(widthInput.value * ratio);
    }
});

heightInput.addEventListener('change', () => {
    if (maintainAspectRatio.checked && originalWidth && originalHeight) {
        const ratio = originalWidth / originalHeight;
        widthInput.value = Math.round(heightInput.value * ratio);
    }
});

// Update original dimensions when image is loaded
fileInputs[0].addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const img = new Image();
        img.onload = () => {
            originalWidth = img.width;
            originalHeight = img.height;
            widthInput.value = originalWidth;
            heightInput.value = originalHeight;
        };
        img.src = URL.createObjectURL(file);
    }
});

// Quality slider value display
const qualitySlider = document.querySelector('#quality');
const qualityValue = document.querySelector('.quality-value');

qualitySlider.addEventListener('input', () => {
    qualityValue.textContent = qualitySlider.value + '%';
}); 