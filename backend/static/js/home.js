async function loadRecentFacilities() {
    const container = document.getElementById('recentFacilities');
    showLoading('recentFacilities');

    const data = await fetchAPI('/facilities/?ordering=-created_at&limit=5');

    if (data && (data.results || data.length > 0)) {
        const facilities = data.results || data;
        container.innerHTML = '';

        facilities.slice(0, 5).forEach(facility => {
            const div = document.createElement('div');
            div.style.cssText = 'padding: 0.75rem; border-bottom: 1px solid #eee;';
            div.innerHTML = `
                <strong>${facility.name}</strong>
                <div style="font-size: 0.9rem; color: #666;">
                    ${facility.county} • ${facility.phone || 'No phone'}
                </div>
            `;
            container.appendChild(div);
        });

        if (facilities.length === 0) {
            container.innerHTML = '<p>No facilities found. Add some via admin panel.</p>';
        }
    } else {
        container.innerHTML = '<p>Failed to load facilities.</p>';
    }
}

// Load health tips
async function loadHealthTips() {
    const container = document.getElementById('healthTips');
    showLoading('healthTips');

    const data = await fetchAPI('/articles/?limit=3');

    if (data && (data.results || data.length > 0)) {
        const articles = data.results || data;
        container.innerHTML = '';

        articles.slice(0, 3).forEach(article => {
            const div = document.createElement('div');
            div.style.cssText = 'padding: 0.75rem; border-bottom: 1px solid #eee;';
            div.innerHTML = `
                <strong>${article.title}</strong>
                <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">
                    ${article.excerpt || article.content.substring(0, 100)}...
                </div>
            `;
            container.appendChild(div);
        });
    } else {
        container.innerHTML = '<p>No health tips available.</p>';
    }
}

// Quick search function
function quickSearch() {
    const query = document.getElementById('quickSearch').value.trim();
    if (query) {
        window.location.href = `/search/?q=${encodeURIComponent(query)}`;
    }
}

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadRecentFacilities();
    loadHealthTips();

    // Make Enter key trigger search
    document.getElementById('quickSearch').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') quickSearch();
    });
});
