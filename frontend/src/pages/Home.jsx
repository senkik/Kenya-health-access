import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import SearchBar from '../components/SearchBar';
import FacilityCard from '../components/FacilityCard';
import { facilityAPI, healthContentAPI } from '../services/api';

export default function Home() {
    const [randomTip, setRandomTip] = useState(null);

    // Fetch recent facilities
    const { data: facilitiesData, isLoading: facilitiesLoading } = useQuery({
        queryKey: ['facilities', 'recent'],
        queryFn: () => facilityAPI.getAll({ page_size: 6, ordering: '-created_at' }),
    });

    // Fetch random health tip
    useEffect(() => {
        healthContentAPI.getRandomTip()
            .then(response => setRandomTip(response.data))
            .catch(error => console.error('Error fetching health tip:', error));
    }, []);

    const facilities = facilitiesData?.data?.results || [];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="text-center max-w-3xl mx-auto">
                        <h1 className="text-4xl md:text-5xl font-bold mb-4">
                            Find Quality Healthcare Near You
                        </h1>
                        <p className="text-xl text-primary-100 mb-8">
                            Search thousands of hospitals, clinics, and pharmacies across Kenya
                        </p>

                        {/* Search Bar */}
                        <div className="max-w-2xl mx-auto">
                            <SearchBar />
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-3 gap-4 mt-12 max-w-2xl mx-auto">
                            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                                <p className="text-3xl font-bold">1000+</p>
                                <p className="text-sm text-primary-100">Facilities</p>
                            </div>
                            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                                <p className="text-3xl font-bold">47</p>
                                <p className="text-sm text-primary-100">Counties</p>
                            </div>
                            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                                <p className="text-3xl font-bold">24/7</p>
                                <p className="text-sm text-primary-100">Access</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* USSD Banner */}
            <div className="bg-secondary-600 text-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex flex-col md:flex-row items-center justify-between">
                        <div className="flex items-center space-x-4 mb-4 md:mb-0">
                            <span className="text-4xl">📞</span>
                            <div>
                                <h3 className="text-xl font-bold">No Internet? No Problem!</h3>
                                <p className="text-secondary-100">Access via USSD on any phone</p>
                            </div>
                        </div>
                        <div className="bg-white text-secondary-700 px-8 py-4 rounded-lg">
                            <p className="text-sm font-medium">Dial</p>
                            <p className="text-3xl font-bold">*384*43149#</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {/* Browse by County */}
                <section className="mb-12">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Browse by County</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika'].map(county => (
                            <Link
                                key={county}
                                to={`/search?county=${county}`}
                                className="card text-center hover:shadow-lg transition-shadow"
                            >
                                <p className="font-medium text-gray-900">{county}</p>
                            </Link>
                        ))}
                    </div>
                    <div className="text-center mt-6">
                        <Link to="/search" className="btn btn-outline">
                            View All Counties →
                        </Link>
                    </div>
                </section>

                {/* Recent Facilities */}
                <section className="mb-12">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-bold text-gray-900">Recently Added Facilities</h2>
                        <Link to="/search" className="text-primary-600 hover:text-primary-700 font-medium">
                            View All →
                        </Link>
                    </div>

                    {facilitiesLoading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="card animate-pulse">
                                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                                    <div className="h-3 bg-gray-200 rounded w-1/2 mb-6"></div>
                                    <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                                    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                                </div>
                            ))}
                        </div>
                    ) : facilities.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {facilities.map(facility => (
                                <FacilityCard key={facility.id} facility={facility} />
                            ))}
                        </div>
                    ) : (
                        <div className="card text-center py-12">
                            <p className="text-gray-500">No facilities found</p>
                        </div>
                    )}
                </section>

                {/* Health Tip */}
                {randomTip && (
                    <section className="mb-12">
                        <div className="bg-gradient-to-r from-secondary-50 to-primary-50 rounded-lg p-8">
                            <div className="flex items-start space-x-4">
                                <span className="text-4xl">💡</span>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-2">Health Tip of the Day</h3>
                                    <p className="text-gray-700">{randomTip.tip}</p>
                                </div>
                            </div>
                        </div>
                    </section>
                )}

                {/* Features */}
                <section>
                    <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Why Use Kenya Health Access?</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="text-center">
                            <div className="text-5xl mb-4">🔍</div>
                            <h3 className="text-lg font-bold mb-2">Easy Search</h3>
                            <p className="text-gray-600">
                                Find healthcare facilities by name, location, or services offered
                            </p>
                        </div>
                        <div className="text-center">
                            <div className="text-5xl mb-4">📱</div>
                            <h3 className="text-lg font-bold mb-2">USSD Access</h3>
                            <p className="text-gray-600">
                                Works on all phones, even without internet connection
                            </p>
                        </div>
                        <div className="text-center">
                            <div className="text-5xl mb-4">✓</div>
                            <h3 className="text-lg font-bold mb-2">Verified Info</h3>
                            <p className="text-gray-600">
                                Accurate and up-to-date information about facilities
                            </p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}
