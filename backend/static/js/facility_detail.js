function getFacilityUuid() {
    const path = window.location.pathname;
    const match = path.match(/facility\/([^/]+)/);
    return match ? match[1] : null;
}

// Load facility details
async function loadFacilityDetails() {
    const uuid = getFacilityUuid();
    if (!uuid) {
        document.getElementById('facilityContent').innerHTML = `
            <div class="alert alert-warning">
                <h3>Facility not found</h3>
                <p>The facility you're looking for doesn't exist or the URL is incorrect.</p>
                <a href="/search/" class="btn">Browse Facilities</a>
            </div>
        `;
        return;
    }

    const data = await fetchAPI(`/facilities/${uuid}/`);

    if (!data) {
        document.getElementById('facilityContent').innerHTML = `
            <div class="alert alert-warning">
                <h3>Failed to load facility</h3>
                <p>Could not load facility details. Please try again later.</p>
            </div>
        `;
        return;
    }

    displayFacilityDetails(data);
}

// Display facility details
function displayFacilityDetails(facility) {
    const container = document.getElementById('facilityContent');

    // Format services list
    const servicesHtml = facility.services && facility.services.length > 0
        ? facility.services.map(service =>
            `<span class="service-tag">${service.name}</span>`
        ).join('')
        : '<p>No services listed</p>';

    // Format opening hours
    let openingHoursHtml = '<p>Opening hours not specified</p>';
    if (facility.opening_hours && typeof facility.opening_hours === 'object') {
        openingHoursHtml = Object.entries(facility.opening_hours)
            .map(([day, hours]) => `<p><strong>${day}:</strong> ${hours}</p>`)
            .join('');
    } else if (facility.opening_hours) {
        openingHoursHtml = `<p>${facility.opening_hours}</p>`;
    }

    // Map coordinates (if available)
    let mapHtml = '<p>Map location not available</p>';
    if (facility.latitude && facility.longitude) {
        mapHtml = `
            <div class="map-container">
                <p>📍 Location: ${facility.latitude}, ${facility.longitude}</p>
                <!-- In future: Add actual map integration -->
            </div>
        `;
    }

    container.innerHTML = `
        <div class="facility-header">
            <div class="facility-title">
                <h1>${facility.name}</h1>
                <p style="color: #666; font-size: 1.1rem;">
                    ${facility.facility_type?.name || 'Healthcare Facility'}
                </p>
            </div>
            
            <div style="text-align: right;">
                ${facility.is_verified ? '<div class="meta-item">✓ Verified Facility</div>' : ''}
                ${facility.accepts_sha ? '<div class="meta-item">✅ Accepts SHA</div>' : ''}
                ${facility.emergency_available ? '<div class="meta-item">🚨 Emergency Services</div>' : ''}
            </div>
        </div>
        
        <div class="facility-meta">
            <div class="meta-item">
                <span>📍</span>
                <div>
                    <strong>${facility.county}</strong>
                    ${facility.town ? `, ${facility.town}` : ''}
                    ${facility.address ? `<div style="font-size: 0.9rem;">${facility.address}</div>` : ''}
                </div>
            </div>
            
            ${facility.phone ? `
            <div class="meta-item">
                <span>📞</span>
                <div>
                    <strong>Phone:</strong>
                    <div>${formatPhone(facility.phone)}</div>
                </div>
            </div>
            ` : ''}
            
            ${facility.email ? `
            <div class="meta-item">
                <span>✉️</span>
                <div>
                    <strong>Email:</strong>
                    <div>${facility.email}</div>
                </div>
            </div>
            ` : ''}
        </div>
        
        ${mapHtml}
        
        <div class="info-grid">
            <div class="info-section">
                <h3>Contact Information</h3>
                
                ${facility.phone ? `
                <div class="contact-item">
                    <div class="contact-icon">📞</div>
                    <div>
                        <strong>Phone</strong>
                        <div>${formatPhone(facility.phone)}</div>
                        <a href="tel:${facility.phone}" class="btn" style="margin-top: 0.5rem; padding: 0.25rem 0.75rem; font-size: 0.9rem;">
                            Call Now
                        </a>
                    </div>
                </div>
                ` : ''}
                
                ${facility.email ? `
                <div class="contact-item">
                    <div class="contact-icon">✉️</div>
                    <div>
                        <strong>Email</strong>
                        <div>${facility.email}</div>
                        <a href="mailto:${facility.email}" class="btn" style="margin-top: 0.5rem; padding: 0.25rem 0.75rem; font-size: 0.9rem;">
                            Send Email
                        </a>
                    </div>
                </div>
                ` : ''}
                
                ${facility.website ? `
                <div class="contact-item">
                    <div class="contact-icon">🌐</div>
                    <div>
                        <strong>Website</strong>
                        <div>${facility.website}</div>
                        <a href="${facility.website}" target="_blank" class="btn" style="margin-top: 0.5rem; padding: 0.25rem 0.75rem; font-size: 0.9rem;">
                            Visit Website
                        </a>
                    </div>
                </div>
                ` : ''}
            </div>
            
            <div class="info-section">
                <h3>Services Offered</h3>
                <div>${servicesHtml}</div>
                
                ${facility.ambulance_available ? `
                <div style="margin-top: 1rem; padding: 1rem; background: #fff3cd; border-radius: 5px;">
                    <strong>🚑 Ambulance Service Available</strong>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        This facility has ambulance services for emergency transport.
                    </p>
                </div>
                ` : ''}
            </div>
            
            <div class="info-section">
                <h3>Operating Hours</h3>
                ${openingHoursHtml}
                
                ${facility.is_24_hours ? `
                <div style="margin-top: 1rem; padding: 1rem; background: #e8f5e8; border-radius: 5px;">
                    <strong>24/7 Facility</strong>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        This facility operates 24 hours a day, 7 days a week.
                    </p>
                </div>
                ` : ''}
            </div>
            
            <div class="info-section">
                <h3>Insurance & Verification</h3>
                
                <div style="margin: 1rem 0;">
                    <p><strong>SHA Accepted:</strong> 
                        ${facility.accepts_sha ? '✅ Yes' : '❌ No'}
                        ${facility.sha_code ? ` (Code: ${facility.sha_code})` : ''}
                    </p>
                    
                    <p><strong>Facility Verified:</strong> 
                        ${facility.is_verified ? '✅ Yes' : '❌ Not verified'}
                    </p>
                    
                    ${facility.verified_date ? `
                    <p><strong>Last Verified:</strong> ${new Date(facility.verified_date).toLocaleDateString()}</p>
                    ` : ''}
                </div>
            </div>
        </div>
        
        <div style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 10px;">
            <h3>Additional Information</h3>
            <p><strong>Facility ID:</strong> ${facility.uuid}</p>
            <p><strong>Added to System:</strong> ${new Date(facility.created_at).toLocaleDateString()}</p>
            <p><strong>Last Updated:</strong> ${new Date(facility.updated_at).toLocaleDateString()}</p>
        </div>
    `;

    // Update page title
    document.title = `${facility.name} - Kenya Health Access`;
}

// Load facility details on page load
document.addEventListener('DOMContentLoaded', loadFacilityDetails);
