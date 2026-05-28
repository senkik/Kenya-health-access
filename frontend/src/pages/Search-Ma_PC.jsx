import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import SearchBar from '../components/SearchBar';
import FacilityCard from '../components/FacilityCard';
import FacilityMap from '../components/FacilityMap';
import { facilityAPI, countyAPI, facilityTypeAPI, serviceAPI } from '../services/api';
import { getUserLocation, formatDistance } from '../utils/location';

// Standard service categories for multi-select
const SERVICE_OPTIONS = [
    { value: 'Emergency', label: 'Emergency', icon: '🚨' },
    { value: 'Maternity', label: 'Maternity', icon: '🤱' },
    { value: 'Pharmacy', label: 'Pharmacy', icon: '💊' },
    { value: 'Laboratory', label: 'Laboratory', icon: '🔬' },
    { value: 'Surgery', label: 'Surgery', icon: '🏥' },
    { value: 'Dental', label: 'Dental', icon: '🦷' },
    { value: 'Eye Care', label: 'Eye Care', icon: '👁️' },
];

const RADIUS_OPTIONS = [
    { value: 1, label: '1 km' },
    { value: 5, label: '5 km' },
    { value: 10, label: '10 km' },
    { value: 25, label: '25 km' },
    { value: 50, label: '50 km' },
];

export default function Search() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [showMap, setShowMap] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [locationStatus, setLocationStatus] = useState(''); // '', 'loading', 'active', 'error'
    const [locationError, setLocationError] = useState('');
    const [filters, setFilters] = useState({
        search: searchParams.get('q') || '',
        county: searchParams.get('county') || '',
        facility_type: searchParams.get('type') || '',
        accepts_sha: searchParams.get('sha') || '',
        emergency_available: searchParams.get('emergency') || '',
        constituency: searchParams.get('constituency') || '',
        town: searchParams.get('town') || '',
        services: searchParams.get('services') || '',
        is_24_hours: searchParams.get('is_24_hours') || '',
        lat: searchParams.get('lat') || '',
        lng: searchParams.get('lng') || '',
        radius: searchParams.get('radius') || '10',
        page: parseInt(searchParams.get('page')) || 1,
    });

    // Track selected service checkboxes as an array
    const [selectedServices, setSelectedServices] = useState(() => {
        const s = searchParams.get('services');
        return s ? s.split(',').filter(Boolean) : [];
    });

    // Fetch counties
    const { data: countiesData } = useQuery({
        queryKey: ['counties'],
        queryFn: () => countyAPI.getAll(),
    });

    // Fetch facility types
    const { data: typesData } = useQuery({
        queryKey: ['facility-types'],
        queryFn: () => facilityTypeAPI.getAll(),
    });

    // Fetch constituencies for dropdown
    const { data: constituenciesData } = useQuery({
        queryKey: ['constituencies'],
        queryFn: () => facilityAPI.getConstituencies(),
    });

    // Fetch facilities with filters
    const { data: facilitiesData, isLoading, error } = useQuery({
        queryKey: ['facilities', filters],
        queryFn: () => facilityAPI.getAll(filters),
    });

    const counties = countiesData?.data?.results || countiesData?.data || [];
    const facilityTypes = typesData?.data?.results || typesData?.data || [];
    const constituencies = constituenciesData?.data || [];
    const facilities = facilitiesData?.data?.results || [];
    const totalCount = facilitiesData?.data?.count || 0;
    const totalPages = Math.ceil(totalCount / 20);

    // Check if any advanced filter is active
    const hasAdvancedFilters = filters.constituency || filters.town || filters.services ||
        filters.is_24_hours || filters.lat;

    // Auto-expand advanced filters if any are active
    useEffect(() => {
        if (hasAdvancedFilters) setShowAdvanced(true);
    }, []);

    // Update URL when filters change
    useEffect(() => {
        const params = {};
        Object.entries(filters).forEach(([key, value]) => {
            if (value) params[key === 'search' ? 'q' : key] = value;
        });
        setSearchParams(params);
    }, [filters, setSearchParams]);

    const handleFilterChange = useCallback((key, value) => {
        setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
    }, []);

    const handleSearch = useCallback((query) => {
        setFilters(prev => ({ ...prev, search: query, page: 1 }));
    }, []);

    // Service checkbox toggle
    const handleServiceToggle = useCallback((serviceName) => {
        setSelectedServices(prev => {
            const next = prev.includes(serviceName)
                ? prev.filter(s => s !== serviceName)
                : [...prev, serviceName];
            // Update filters with comma-separated string
            setFilters(f => ({ ...f, services: next.join(','), page: 1 }));
            return next;
        });
    }, []);

    // Near Me toggle
    const handleNearMe = useCallback(async () => {
        if (locationStatus === 'active') {
            // Turn off
            setLocationStatus('');
            setLocationError('');
            setFilters(prev => ({ ...prev, lat: '', lng: '', page: 1 }));
            return;
        }

        setLocationStatus('loading');
        setLocationError('');
        try {
            const pos = await getUserLocation();
            setLocationStatus('active');
            setFilters(prev => ({
                ...prev,
                lat: pos.lat.toString(),
                lng: pos.lng.toString(),
                page: 1,
            }));
        } catch (err) {
            setLocationStatus('error');
            setLocationError(err.message);
        }
    }, [locationStatus]);

    const resetFilters = useCallback(() => {
        setFilters({
            search: '',
            county: '',
            facility_type: '',
            accepts_sha: '',
            emergency_available: '',
            constituency: '',
            town: '',
            services: '',
            is_24_hours: '',
            lat: '',
            lng: '',
            radius: '10',
            page: 1,
        });
        setSelectedServices([]);
        setLocationStatus('');
        setLocationError('');
    }, []);

    // Count active filters for badge
    const activeFilterCount = [
        filters.county, filters.facility_type, filters.accepts_sha,
        filters.emergency_available, filters.constituency, filters.town,
        filters.services, filters.is_24_hours, filters.lat,
    ].filter(Boolean).length;

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Search Header */}
            <div className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">Search Healthcare Facilities</h1>
                    <SearchBar onSearch={handleSearch} />
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                    {/* Filters Sidebar */}
                    <aside className="lg:col-span-1">
                        <div className="card sticky top-20">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    Filters
                                    {activeFilterCount > 0 && (
                                        <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-teal-600 rounded-full">
                                            {activeFilterCount}
                                        </span>
                                    )}
                                </h2>
                                <button
                                    onClick={resetFilters}
                                    className="text-sm text-primary-600 hover:text-primary-700"
                                >
                                    Reset
                                </button>
                            </div>

                            <div className="space-y-4">
                                {/* County Filter */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        County
                                    </label>
                                    <select
                                        id="filter-county"
                                        value={filters.county}
                                        onChange={(e) => handleFilterChange('county', e.target.value)}
                                        className="input"
                                    >
                                        <option value="">All Counties</option>
                                        {counties.map(county => (
                                            <option key={county.id} value={county.name}>
                                                {county.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Facility Type Filter */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Facility Type
                                    </label>
                                    <select
                                        id="filter-facility-type"
                                        value={filters.facility_type}
                                        onChange={(e) => handleFilterChange('facility_type', e.target.value)}
                                        className="input"
                                    >
                                        <option value="">All Types</option>
                                        {facilityTypes.map(type => (
                                            <option key={type.id} value={type.id}>
                                                {type.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Constituency Filter */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Constituency
                                    </label>
                                    <select
                                        id="filter-constituency"
                                        value={filters.constituency}
                                        onChange={(e) => handleFilterChange('constituency', e.target.value)}
                                        className="input"
                                    >
                                        <option value="">All Constituencies</option>
                                        {constituencies.map(c => (
                                            <option key={c} value={c}>{c}</option>
                                        ))}
                                    </select>
                                </div>

                                {/* Town / Area Filter */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Town / Area
                                    </label>
                                    <input
                                        id="filter-town"
                                        type="text"
                                        value={filters.town}
                                        onChange={(e) => handleFilterChange('town', e.target.value)}
                                        placeholder="e.g. Kisumu, Westlands..."
                                        className="input"
                                    />
                                </div>

                                {/* Advanced toggle */}
                                <button
                                    onClick={() => setShowAdvanced(!showAdvanced)}
                                    className="w-full flex items-center justify-between text-sm font-medium text-teal-700 hover:text-teal-800 py-2 border-t border-gray-200 pt-4"
                                >
                                    <span>Advanced Filters</span>
                                    <svg
                                        className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
                                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>

                                {showAdvanced && (
                                    <div className="space-y-4 pt-2 animate-in">
                                        {/* Near Me */}
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                📍 Near Me
                                            </label>
                                            <button
                                                id="btn-near-me"
                                                onClick={handleNearMe}
                                                disabled={locationStatus === 'loading'}
                                                className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all ${
                                                    locationStatus === 'active'
                                                        ? 'bg-teal-100 text-teal-800 border-2 border-teal-400 shadow-sm'
                                                        : locationStatus === 'loading'
                                                            ? 'bg-gray-100 text-gray-500 border border-gray-300 cursor-wait'
                                                            : 'bg-white text-gray-700 border border-gray-300 hover:border-teal-400 hover:bg-teal-50'
                                                }`}
                                            >
                                                {locationStatus === 'loading' && (
                                                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                                    </svg>
                                                )}
                                                {locationStatus === 'active' ? '✓ Location Active' :
                                                 locationStatus === 'loading' ? 'Getting Location...' :
                                                 '📍 Use My Location'}
                                            </button>
                                            {locationStatus === 'error' && (
                                                <p className="text-xs text-red-600 mt-1">{locationError}</p>
                                            )}
                                            {locationStatus === 'active' && (
                                                <div className="mt-2">
                                                    <label className="block text-xs font-medium text-gray-500 mb-1">Radius</label>
                                                    <div className="flex flex-wrap gap-1">
                                                        {RADIUS_OPTIONS.map(opt => (
                                                            <button
                                                                key={opt.value}
                                                                onClick={() => handleFilterChange('radius', opt.value.toString())}
                                                                className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all ${
                                                                    filters.radius === opt.value.toString()
                                                                        ? 'bg-teal-600 text-white shadow-sm'
                                                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                                }`}
                                                            >
                                                                {opt.label}
                                                            </button>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        {/* Services Multi-Select */}
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                🏥 Services
                                            </label>
                                            <div className="grid grid-cols-2 gap-1.5">
                                                {SERVICE_OPTIONS.map(svc => (
                                                    <label
                                                        key={svc.value}
                                                        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg cursor-pointer text-xs font-medium transition-all border ${
                                                            selectedServices.includes(svc.value)
                                                                ? 'bg-teal-50 text-teal-800 border-teal-300'
                                                                : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                                                        }`}
                                                    >
                                                        <input
                                                            type="checkbox"
                                                            checked={selectedServices.includes(svc.value)}
                                                            onChange={() => handleServiceToggle(svc.value)}
                                                            className="sr-only"
                                                        />
                                                        <span>{svc.icon}</span>
                                                        <span>{svc.label}</span>
                                                    </label>
                                                ))}
                                            </div>
                                        </div>

                                        {/* 24/7 Toggle */}
                                        <div className="pt-2">
                                            <label className="flex items-center justify-between cursor-pointer" htmlFor="toggle-24hr">
                                                <span className="text-sm font-medium text-gray-700">🕐 24/7 Only</span>
                                                <div className="relative">
                                                    <input
                                                        type="checkbox"
                                                        id="toggle-24hr"
                                                        checked={filters.is_24_hours === 'true'}
                                                        onChange={(e) => handleFilterChange('is_24_hours', e.target.checked ? 'true' : '')}
                                                        className="sr-only peer"
                                                    />
                                                    <div className="w-10 h-5 bg-gray-200 rounded-full peer-checked:bg-teal-600 transition-colors"></div>
                                                    <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-5"></div>
                                                </div>
                                            </label>
                                        </div>
                                    </div>
                                )}

                                {/* SHA Filter */}
                                <div className="mt-4 pt-4 border-t border-gray-200">
                                    <label className="flex items-center">
                                        <input
                                            type="checkbox"
                                            className="rounded border-gray-300 text-teal-600 shadow-sm focus:border-teal-300 focus:ring focus:ring-teal-200 focus:ring-opacity-50 h-4 w-4"
                                            checked={filters.accepts_sha === 'true'}
                                            onChange={(e) => handleFilterChange('accepts_sha', e.target.checked ? 'true' : '')}
                                        />
                                        <span className="ml-2 text-sm text-gray-700">Accepts SHA</span>
                                    </label>
                                </div>

                                {/* Emergency Filter */}
                                <div>
                                    <label className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={filters.emergency_available === 'true'}
                                            onChange={(e) => handleFilterChange('emergency_available', e.target.checked ? 'true' : '')}
                                            className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                                        />
                                        <span className="text-sm text-gray-700">Emergency Services</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </aside>

                    {/* Results */}
                    <div className="lg:col-span-3">
                        {/* Results Count & Toggle */}
                        <div className="flex justify-between items-center mb-6">
                            <div>
                                <p className="text-gray-600">
                                    Found <span className="font-bold text-gray-900">{totalCount}</span> facilities
                                </p>
                                {locationStatus === 'active' && (
                                    <p className="text-xs text-teal-600 mt-0.5">
                                        Sorted by distance • within {filters.radius} km
                                    </p>
                                )}
                            </div>
                            <button
                                onClick={() => setShowMap(!showMap)}
                                className="btn btn-outline flex items-center space-x-2"
                            >
                                <span>{showMap ? '📋 List View' : '🗺️ Map View'}</span>
                            </button>
                        </div>

                        {/* Map View */}
                        {showMap && !isLoading && !error && (
                            <div className="mb-8">
                                <FacilityMap facilities={facilities} height="500px" />
                            </div>
                        )}

                        {/* Loading State */}
                        {isLoading && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {[1, 2, 3, 4].map(i => (
                                    <div key={i} className="card animate-pulse">
                                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                                        <div className="h-3 bg-gray-200 rounded w-1/2 mb-6"></div>
                                        <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                                        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Error State */}
                        {error && (
                            <div className="card bg-red-50 border border-red-200">
                                <p className="text-red-800">Error loading facilities. Please try again.</p>
                            </div>
                        )}

                        {/* No Results */}
                        {!isLoading && !error && facilities.length === 0 && (
                            <div className="card text-center py-12">
                                <div className="text-6xl mb-4">🔍</div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">No facilities found</h3>
                                <p className="text-gray-600 mb-6">Try adjusting your search filters</p>
                                <button onClick={resetFilters} className="btn btn-primary">
                                    Reset Filters
                                </button>
                            </div>
                        )}

                        {/* Results Grid */}
                        {!isLoading && !error && facilities.length > 0 && (
                            <>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {facilities.map(facility => (
                                        <FacilityCard key={facility.id} facility={facility} />
                                    ))}
                                </div>

                                {/* Pagination */}
                                {totalPages > 1 && (
                                    <div className="flex justify-center items-center space-x-2 mt-8">
                                        <button
                                            onClick={() => handleFilterChange('page', filters.page - 1)}
                                            disabled={filters.page === 1}
                                            className="btn btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            ← Previous
                                        </button>

                                        <div className="flex space-x-1">
                                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                                const page = i + 1;
                                                return (
                                                    <button
                                                        key={page}
                                                        onClick={() => handleFilterChange('page', page)}
                                                        className={`px-4 py-2 rounded-lg font-medium ${filters.page === page
                                                            ? 'bg-primary-600 text-white'
                                                            : 'bg-white text-gray-700 hover:bg-gray-100'
                                                            }`}
                                                    >
                                                        {page}
                                                    </button>
                                                );
                                            })}
                                        </div>

                                        <button
                                            onClick={() => handleFilterChange('page', filters.page + 1)}
                                            disabled={filters.page === totalPages}
                                            className="btn btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            Next →
                                        </button>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
