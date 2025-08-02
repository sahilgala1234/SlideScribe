// YouTube Slide Extractor - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const videoForm = document.getElementById('videoForm');
    const submitBtn = document.getElementById('submitBtn');
    const youtubeUrlInput = document.getElementById('youtube_url');

    // Form submission handling
    if (videoForm) {
        videoForm.addEventListener('submit', function(e) {
            const url = youtubeUrlInput.value.trim();
            
            // Basic YouTube URL validation
            if (!isValidYouTubeUrl(url)) {
                e.preventDefault();
                showAlert('Please enter a valid YouTube URL', 'error');
                return;
            }

            // Show loading state
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
            
            // Allow form to submit normally
            // The server will handle the processing
        });
    }

    // Real-time URL validation
    if (youtubeUrlInput) {
        youtubeUrlInput.addEventListener('input', function() {
            const url = this.value.trim();
            const isValid = url === '' || isValidYouTubeUrl(url);
            
            if (isValid) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    });
});

/**
 * Validate YouTube URL format
 * @param {string} url - The URL to validate
 * @returns {boolean} - True if valid YouTube URL
 */
function isValidYouTubeUrl(url) {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11})/;
    return youtubeRegex.test(url);
}

/**
 * Show alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, error, info, warning)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the main container
    const container = document.querySelector('.container');
    const firstChild = container.firstElementChild;
    container.insertBefore(alertContainer.firstElementChild, firstChild);
}

/**
 * Get icon class for alert type
 * @param {string} type - Alert type
 * @returns {string} - Font Awesome icon class
 */
function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Format file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy: ', err);
        showAlert('Failed to copy to clipboard', 'error');
    }
}

/**
 * Smooth scroll to element
 * @param {string} elementId - ID of element to scroll to
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Utility functions for processing page
if (typeof processingId !== 'undefined') {
    // This code runs only on the processing page
    
    /**
     * Format duration in seconds to human readable format
     * @param {number} seconds - Duration in seconds
     * @returns {string} - Formatted duration
     */
    function formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        if (minutes > 0) {
            return `${minutes}m ${remainingSeconds}s`;
        }
        return `${remainingSeconds}s`;
    }
    
    /**
     * Update page title with progress
     * @param {number} progress - Progress percentage
     */
    function updatePageTitle(progress) {
        if (progress >= 0 && progress <= 100) {
            document.title = `(${progress}%) Processing Video - YouTube Slide Extractor`;
        }
    }
    
    // Update page title when progress changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                const progressBar = document.getElementById('progressBar');
                if (progressBar) {
                    const width = progressBar.style.width;
                    const progress = parseInt(width.replace('%', '')) || 0;
                    updatePageTitle(progress);
                }
            }
        });
    });
    
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        observer.observe(progressBar, { attributes: true });
    }
    
    // Reset page title when leaving page
    window.addEventListener('beforeunload', function() {
        document.title = 'YouTube Slide Extractor';
    });
}

// Prevent form resubmission on page refresh
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}
