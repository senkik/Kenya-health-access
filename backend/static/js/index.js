// Load counties on page load
fetch('/api/counties/')
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById('countySelect');
        data.forEach(county => {
            const option = document.createElement('option');
            option.value = county.name;
            option.textContent = county.name;
            select.appendChild(option);
        });
    });

// Load all facilities on page load
function loadAllFacilities() {
    fetch('/api/facilities/')
        .then(response => response.json())
        .then(data => displayFacilities(data.results || data));
}

// Search facilities
function searchFacilities() {
    const searchTerm = document.getElementById('searchInput').value;
    const county = document.getElementById('countySelect').value;

    let url = '/api/facilities/';
    if (searchTerm || county) {
        url = `/api/facilities/search/?q=${searchTerm}&county=${county}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => displayFacilities(data.results || data));
}

// Display facilities
function displayFacilities(facilities) {
    const container = document.getElementById('facilitiesList');
    container.innerHTML = '';

    if (!facilities || facilities.length === 0) {
        container.innerHTML = '<p>No facilities found. Try a different search.</p>';
        return;
    }

    facilities.forEach(facility => {
        const card = document.createElement('div');
        card.className = 'facility-card';
        card.innerHTML = `
            <h3>${facility.name}</h3>
            <p>📍 ${facility.county} ${facility.town ? ', ' + facility.town : ''}</p>
            <p>📞 ${facility.phone || 'Phone not available'}</p>
            <p>${facility.emergency_available ? '🚨 Emergency Services Available' : ''}</p>
            <p>${facility.accepts_sha ? '✅ Accepts SHA' : ''}</p>
            <small>Type: ${facility.facility_type?.name || 'Healthcare'}</small>
        `;
        container.appendChild(card);
    });
}

// Load facilities on page load
loadAllFacilities();
