import axios from 'axios';

// Base API URL - adjust based on environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

// API endpoints
export const facilityAPI = {
    // Get all facilities with optional filters
    getAll: (params = {}) => api.get('/facilities/', { params }),

    // Get single facility by UUID
    getByUUID: (uuid) => api.get(`/facilities/${uuid}/`),

    // Search facilities
    search: (query, county = '') =>
        api.get('/facilities/search/', { params: { q: query, county } }),

    // Get facilities by county
    getByCounty: (county) =>
        api.get('/facilities/by-county/', { params: { county } }),

    // Get nearby facilities (requires lat/lng)
    getNearby: (lat, lng, radius = 10) =>
        api.get('/facilities/', { params: { lat, lng, radius } }),

    // Update availability status (uses uuid as lookup)
    updateAvailability: (uuid, status) =>
        api.post(`/facilities/${uuid}/update_availability/`, { status }),
};

export const countyAPI = {
    // Get all counties
    getAll: () => api.get('/counties/'),

    // Search counties
    search: (query) => api.get('/counties/', { params: { search: query } }),
};

export const facilityTypeAPI = {
    // Get all facility types
    getAll: () => api.get('/facility-types/'),
};

export const serviceAPI = {
    // Get all services
    getAll: () => api.get('/services/'),

    // Get services by category
    getByCategory: (category) =>
        api.get('/services/', { params: { category } }),
};

export const healthContentAPI = {
    // Get health articles
    getArticles: (params = {}) => api.get('/articles/', { params }),

    // Get health tips
    getTips: (params = {}) => api.get('/health-tips/', { params }),

    // Get random health tip
    getRandomTip: () => api.get('/health-tips/random/'),
};

export const reviewAPI = {
    // Get reviews for a facility
    getByFacility: (facilityId) => api.get('/reviews/', { params: { facility: facilityId } }),

    // Post a new review
    create: (data) => api.post('/reviews/', data),
};

export default api;
