// Global API base URL
const API_BASE_URL = '/api';

// Utility function for API calls
async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showError(`Failed to load data: ${error.message}`);
        return null;
    }
}

// Show/hide loading spinner
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '<div class="spinner"></div>';
    }
}

function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-warning';
    alertDiv.textContent = message;
    document.querySelector('main').prepend(alertDiv);

    // Remove after 5 seconds
    setTimeout(() => alertDiv.remove(), 5000);
}

// Format phone number
function formatPhone(phone) {
    if (!phone) return 'Not available';
    return phone.replace(/(\d{3})(\d{3})(\d{3,4})/, '$1 $2 $3');
}
