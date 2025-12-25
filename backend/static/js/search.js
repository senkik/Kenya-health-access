// Current search state
let currentPage = 1;
const itemsPerPage = 12;
let totalResults = 0;
let currentFilters = {};

// DOM elements
const elements = {
    searchInput: document.getElementById('searchInput'),
    countySelect: document.getElementById('countySelect'),
    facilityTypeSelect: document.getElementById('facilityTypeSelect'),
    nhifFilter: document.getElementById('nhifFilter'),
    sortSelect: document.getElementById('sortSelect'),
    facilitiesContainer: document.getElementById('facilitiesContainer'),
    pagination: document.getElementById('pagination'),
    resultsCount: document.getElementById('resultsCount')
};

// Initialize page
async function initializePage() {
    await loadCounties();
    await loadFacilityTypes();
    await searchFacilities();

    // Load filters from URL if present
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');
    const county = urlParams.get('county');

    if (searchQuery) {
        elements.searchInput.value = searchQuery;
    }

    if (county) {
        elements.countySelect.value = county;
    }

    // Make Enter key trigger search
    elements.searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchFacilities();
    });
}

// Load counties dropdown
async function loadCounties() {
    const data = await fetchAPI('/counties/');
    if (data && (data.results || data.length > 0)) {
        const counties = data.results || data;
        counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county.name;
            option.textContent = county.name;
            elements.countySelect.appendChild(option);
        });
    }
}

// Load facility types dropdown
async function loadFacilityTypes() {
    const data = await fetchAPI('/facility-types/');
    if (data && (data.results || data.length > 0)) {
        const types = data.results || data;
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = type.name;
            elements.facilityTypeSelect.appendChild(option);
        });
    }
}

// Main search function
async function searchFacilities(page = 1) {
    currentPage = page;
    showLoading('facilitiesContainer');

    // Build query parameters
    const params = new URLSearchParams();

    if (elements.searchInput.value) {
        params.append('search', elements.searchInput.value);
    }

    if (elements.countySelect.value) {
        params.append('county', elements.countySelect.value);
    }

    if (elements.facilityTypeSelect.value) {
        params.append('facility_type', elements.facilityTypeSelect.value);
    }

    if (elements.nhifFilter.value) {
        params.append('accepts_nhif', elements.nhifFilter.value);
    }

    // Sorting
    params.append('ordering', elements.sortSelect.value);

    // Pagination
    params.append('page', page);
    params.append('page_size', itemsPerPage);

    // Store current filters
    currentFilters = Object.fromEntries(params);

    // Update URL without reloading
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);

    // Fetch data
    const endpoint = `/facilities/?${params.toString()}`;
    const data = await fetchAPI(endpoint);

    if (data) {
        displayFacilities(data);
    }
}

// Display facilities
function displayFacilities(data) {
    const facilities = data.results || data;
    totalResults = data.count || facilities.length;

    // Update results count
    elements.resultsCount.textContent = `Found ${totalResults} facility${totalResults !== 1 ? 'ies' : ''}`;

    if (facilities.length === 0) {
        elements.facilitiesContainer.innerHTML = `
            <div class="no-results">
                <h3>No facilities found</h3>
                <p>Try adjusting your search filters</p>
                <button onclick="resetFilters()" class="btn">Show All Facilities</button>
            </div>
        `;
        elements.pagination.innerHTML = '';
        return;
    }

    // Render facilities grid
    let html = '<div class="facility-grid">';

    facilities.forEach(facility => {
        html += `
            <div class="facility-card">
                <div class="card-header">
                    <h3 style="margin: 0; font-size: 1.2rem;">${facility.name}</h3>
                    <div style="font-size: 0.9rem; opacity: 0.9;">
                        ${facility.facility_type?.name || 'Healthcare Facility'}
                    </div>
                </div>
                
                <div class="card-body">
                    <div class="facility-info">
                        <i>📍</i>
                        <div>
                            <strong>${facility.county}</strong>
                            ${facility.town ? `, ${facility.town}` : ''}
                            ${facility.address ? `<div style="font-size: 0.9rem; color: #666;">${facility.address}</div>` : ''}
                        </div>
                    </div>
                    
                    <div class="facility-info">
                        <i>📞</i>
                        <div>${formatPhone(facility.phone) || 'Phone not available'}</div>
                    </div>
                    
                    ${facility.email ? `
                    <div class="facility-info">
                        <i>✉️</i>
                        <div>${facility.email}</div>
                    </div>
                    ` : ''}
                    
                    <div style="margin: 1rem 0;">
                        ${facility.accepts_nhif ? '<span class="badge badge-success">Accepts NHIF</span>' : ''}
                        ${facility.emergency_available ? '<span class="badge badge-warning">Emergency Services</span>' : ''}
                        ${facility.is_verified ? '<span class="badge badge-primary">✓ Verified</span>' : ''}
                    </div>
                    
                    ${facility.services && facility.services.length > 0 ? `
                    <div style="margin-top: 1rem;">
                        <strong>Services:</strong>
                        <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">
                            ${facility.services.slice(0, 3).map(s => s.name).join(', ')}
                            ${facility.services.length > 3 ? '...' : ''}
                        </div>
                    </div>
                    ` : ''}
                    
                    <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem;">
                        ${facility.phone ? `<a href="tel:${facility.phone}" class="btn" style="flex: 1; text-align: center;">Call</a>` : ''}
                        <button onclick="showFacilityDetails('${facility.uuid}')" class="btn" style="flex: 1; background: #0055aa;">
                            Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    elements.facilitiesContainer.innerHTML = html;

    // Render pagination
    renderPagination(data);
}

// Render pagination controls
function renderPagination(data) {
    const totalPages = Math.ceil(totalResults / itemsPerPage);

    if (totalPages <= 1) {
        elements.pagination.innerHTML = '';
        return;
    }

    let html = '';

    // Previous button
    html += `
        <button onclick="searchFacilities(${currentPage - 1})" 
                class="page-btn" 
                ${currentPage === 1 ? 'disabled' : ''}>
            ← Previous
        </button>
    `;

    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        html += `
            <button onclick="searchFacilities(${i})" 
                    class="page-btn ${i === currentPage ? 'active' : ''}">
                ${i}
            </button>
        `;
    }

    // Next button
    html += `
        <button onclick="searchFacilities(${currentPage + 1})" 
                class="page-btn" 
                ${currentPage === totalPages ? 'disabled' : ''}>
            Next →
        </button>
    `;

    elements.pagination.innerHTML = html;
}

// Reset all filters
function resetFilters() {
    elements.searchInput.value = '';
    elements.countySelect.value = '';
    elements.facilityTypeSelect.value = '';
    elements.nhifFilter.value = '';
    elements.sortSelect.value = 'name';

    searchFacilities(1);
}

// Use current location
function useMyLocation() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            // For now, just show an alert with coordinates
            // In future, implement actual nearby search
            alert(`Your location: ${lat.toFixed(4)}, ${lng.toFixed(4)}\n\nNearby search coming soon!`);

            // Example API call for nearby facilities:
            // fetchAPI(`/facilities/?lat=${lat}&lng=${lng}&radius=10`);
        },
        (error) => {
            alert('Unable to retrieve your location. Please enable location services.');
        }
    );
}

// Show facility details (modal or new page)
function showFacilityDetails(uuid) {
    // For now, redirect to API endpoint
    window.open(`/api/facilities/${uuid}/`, '_blank');

    // Future: Show modal with more details
    // showFacilityModal(uuid);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializePage);

// Handle browser back/forward buttons
window.addEventListener('popstate', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get('page')) || 1;
    searchFacilities(page);
});
