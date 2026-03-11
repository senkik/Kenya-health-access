import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import SearchBar from '../components/SearchBar';
import FacilityCard from '../components/FacilityCard';
import FacilityMap from '../components/FacilityMap';
import { facilityAPI, countyAPI, facilityTypeAPI } from '../services/api';

export default function Search() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [showMap, setShowMap] = useState(false);
    const [filters, setFilters] = useState({
        search: searchParams.get('q') || '',
        county: searchParams.get('county') || '',
        facility_type: searchParams.get('type') || '',
        accepts_sha: searchParams.get('sha') || '',
        emergency_available: searchParams.get('emergency') || '',
        page: parseInt(searchParams.get('page')) || 1,
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

    // Fetch facilities with filters
    const { data: facilitiesData, isLoading, error } = useQuery({
        queryKey: ['facilities', filters],
        queryFn: () => facilityAPI.getAll(filters),
    });

    const counties = countiesData?.data?.results || countiesData?.data || [];
    const facilityTypes = typesData?.data?.results || typesData?.data || [];
    const facilities = facilitiesData?.data?.results || [];
    const totalCount = facilitiesData?.data?.count || 0;
    const totalPages = Math.ceil(totalCount / 20);

    // Update URL when filters change
    useEffect(() => {
        const params = {};
        Object.entries(filters).forEach(([key, value]) => {
            if (value) params[key === 'search' ? 'q' : key] = value;
        });
        setSearchParams(params);
    }, [filters, setSearchParams]);

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
    };

    const handleSearch = (query) => {
        setFilters(prev => ({ ...prev, search: query, page: 1 }));
    };

    const resetFilters = () => {
        setFilters({
            search: '',
            county: '',
            facility_type: '',
            accepts_sha: '',
            emergency_available: '',
            page: 1,
        });
    };

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
                                <h2 className="text-lg font-bold text-gray-900">Filters</h2>
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

                                {/* SHA Filter */}
                                <div className="mt-4">
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
                            <p className="text-gray-600">
                                Found <span className="font-bold text-gray-900">{totalCount}</span> facilities
                            </p>
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
