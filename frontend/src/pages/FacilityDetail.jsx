import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { facilityAPI, reviewAPI } from '../services/api';
import { formatPhone } from '../utils/helpers';
import FacilityMap from '../components/FacilityMap';

export default function FacilityDetail() {
    const { uuid } = useParams();
    const queryClient = useQueryClient();
    const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '', user_name: '' });

    // Fetch facility
    const { data: facilityData, isLoading: isLoadingFacility, error: facilityError } = useQuery({
        queryKey: ['facility', uuid],
        queryFn: () => facilityAPI.getByUUID(uuid),
    });

    const facility = facilityData?.data;

    // Fetch reviews
    const { data: reviewsData, isLoading: isLoadingReviews } = useQuery({
        queryKey: ['reviews', facility?.id],
        queryFn: () => reviewAPI.getByFacility(facility.id),
        enabled: !!facility?.id,
    });

    const reviews = reviewsData?.data?.results || [];

    // Submit review mutation
    const reviewMutation = useMutation({
        mutationFn: (newReview) => reviewAPI.create(newReview),
        onSuccess: () => {
            queryClient.invalidateQueries(['reviews', facility?.id]);
            queryClient.invalidateQueries(['facility', uuid]);
            setReviewForm({ rating: 5, comment: '', user_name: '' });
            alert('Review submitted successfully!');
        },
    });

    const handleReviewSubmit = (e) => {
        e.preventDefault();
        reviewMutation.mutate({
            facility: facility.id,
            ...reviewForm
        });
    };

    if (isLoadingFacility) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading facility details...</p>
                </div>
            </div>
        );
    }

    if (facilityError || !facility) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="card max-w-md text-center">
                    <div className="text-6xl mb-4">❌</div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Facility Not Found</h2>
                    <p className="text-gray-600 mb-6">The facility you're looking for doesn't exist or has been removed.</p>
                    <Link to="/search" className="btn btn-primary">
                        Back to Search
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <Link to="/search" className="text-primary-600 hover:text-primary-700 font-medium mb-4 inline-block">
                        ← Back to Search
                    </Link>
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">{facility.name}</h1>
                            <p className="text-lg text-gray-600 mt-2">
                                {facility.facility_type_name || facility.facility_type?.name || 'Healthcare Facility'}
                            </p>
                        </div>
                        {facility.average_rating > 0 && (
                            <div className="flex items-center bg-yellow-50 px-4 py-2 rounded-lg border border-yellow-200">
                                <span className="text-yellow-500 mr-2 text-xl">⭐</span>
                                <span className="font-bold text-gray-900 text-lg">{facility.average_rating}</span>
                                <span className="text-gray-400 ml-2">({facility.total_reviews} reviews)</span>
                            </div>
                        )}
                    </div>

                    {/* Availability Status */}
                    <div className="mt-4 flex flex-wrap items-center gap-4">
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${facility.availability_status === 'available' ? 'bg-green-100 text-green-800 border-green-200' :
                            facility.availability_status === 'busy' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                                facility.availability_status === 'emergency_only' ? 'bg-orange-100 text-orange-800 border-orange-200' :
                                    'bg-gray-100 text-gray-800 border-gray-200'
                            }`}>
                            <span className={`h-2.5 w-2.5 rounded-full mr-2 ${facility.availability_status === 'available' ? 'bg-green-500 animate-pulse' :
                                facility.availability_status === 'busy' ? 'bg-yellow-500' :
                                    facility.availability_status === 'emergency_only' ? 'bg-orange-500' :
                                        'bg-gray-500'
                                }`}></span>
                            Status: {facility.availability_status?.replace('_', ' ').toUpperCase() || 'AVAILABLE'}
                        </div>
                        <span className="text-sm text-gray-500 italic">
                            Last updated: {new Date(facility.last_status_update).toLocaleString()}
                        </span>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Map */}
                        {facility.latitude && facility.longitude && (
                            <div className="card !p-0 overflow-hidden h-96">
                                <FacilityMap
                                    facilities={[facility]}
                                    center={[parseFloat(facility.latitude), parseFloat(facility.longitude)]}
                                    zoom={15}
                                    height="100%"
                                />
                            </div>
                        )}

                        {/* Badges */}
                        <div className="card">
                            <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Info</h2>
                            <div className="flex flex-wrap gap-3">
                                {facility.accepts_nhif && (
                                    <span className="px-4 py-2 bg-green-100 text-green-800 font-medium rounded-lg">
                                        ✓ NHIF Accepted
                                    </span>
                                )}
                                {facility.emergency_available && (
                                    <span className="px-4 py-2 bg-red-100 text-red-800 font-medium rounded-lg">
                                        🚨 Emergency Services
                                    </span>
                                )}
                                {facility.ambulance_available && (
                                    <span className="px-4 py-2 bg-orange-100 text-orange-800 font-medium rounded-lg">
                                        🚑 Ambulance Available
                                    </span>
                                )}
                                {facility.is_24_hours && (
                                    <span className="px-4 py-2 bg-blue-100 text-blue-800 font-medium rounded-lg">
                                        🕐 24 Hours
                                    </span>
                                )}
                                {facility.is_verified && (
                                    <span className="px-4 py-2 bg-primary-100 text-primary-800 font-medium rounded-lg">
                                        ✓ Verified
                                    </span>
                                )}
                            </div>
                        </div>

                        {/* Services */}
                        {facility.services && facility.services.length > 0 && (
                            <div className="card">
                                <h2 className="text-xl font-bold text-gray-900 mb-4">Services Offered</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {facility.services.map((service, index) => (
                                        <div key={index} className="flex items-center space-x-2">
                                            <span className="text-primary-600">✓</span>
                                            <span className="text-gray-700">{service.name}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Opening Hours */}
                        {facility.opening_hours && (
                            <div className="card">
                                <h2 className="text-xl font-bold text-gray-900 mb-4">Opening Hours</h2>
                                <p className="text-gray-700 whitespace-pre-line">{facility.opening_hours}</p>
                            </div>
                        )}

                        {/* Reviews Section */}
                        <div className="card">
                            <h2 className="text-xl font-bold text-gray-900 mb-6">Patient Reviews</h2>

                            {/* Review Form */}
                            <form onSubmit={handleReviewSubmit} className="mb-8 bg-gray-50 p-4 rounded-lg border border-gray-100">
                                <h3 className="font-bold text-gray-900 mb-4">Leave a Review</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
                                        <input
                                            type="text"
                                            required
                                            value={reviewForm.user_name}
                                            onChange={(e) => setReviewForm({ ...reviewForm, user_name: e.target.value })}
                                            className="input"
                                            placeholder="Enter your name"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Rating</label>
                                        <select
                                            value={reviewForm.rating}
                                            onChange={(e) => setReviewForm({ ...reviewForm, rating: parseInt(e.target.value) })}
                                            className="input"
                                        >
                                            <option value="5">5 Stars - Excellent</option>
                                            <option value="4">4 Stars - Good</option>
                                            <option value="3">3 Stars - Average</option>
                                            <option value="2">2 Stars - Poor</option>
                                            <option value="1">1 Star - Terrible</option>
                                        </select>
                                    </div>
                                </div>
                                <div className="mb-4">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Comment</label>
                                    <textarea
                                        required
                                        value={reviewForm.comment}
                                        onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                                        className="input h-24"
                                        placeholder="Share your experience..."
                                    ></textarea>
                                </div>
                                <button
                                    type="submit"
                                    disabled={reviewMutation.isLoading}
                                    className="btn btn-primary w-full md:w-auto"
                                >
                                    {reviewMutation.isLoading ? 'Submitting...' : 'Submit Review'}
                                </button>
                            </form>

                            {/* Reviews List */}
                            <div className="space-y-6">
                                {isLoadingReviews ? (
                                    <p className="text-gray-500 italic">Loading reviews...</p>
                                ) : reviews.length > 0 ? (
                                    reviews.map((review) => (
                                        <div key={review.id} className="border-b border-gray-100 pb-6 last:border-0 last:pb-0">
                                            <div className="flex justify-between items-start mb-2">
                                                <div>
                                                    <span className="font-bold text-gray-900">{review.user_name}</span>
                                                    <div className="flex text-yellow-500 text-sm mt-1">
                                                        {[...Array(review.rating)].map((_, i) => <span key={i}>⭐</span>)}
                                                    </div>
                                                </div>
                                                <span className="text-sm text-gray-400">
                                                    {new Date(review.created_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                            <p className="text-gray-700">{review.comment}</p>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-gray-500 italic text-center py-4">No reviews yet. Be the first to leave one!</p>
                                )}
                            </div>
                        </div>

                        {/* Additional Info */}
                        <div className="card">
                            <h2 className="text-xl font-bold text-gray-900 mb-4">Additional Information</h2>
                            <dl className="space-y-3">
                                {facility.nhif_code && (
                                    <div>
                                        <dt className="text-sm font-medium text-gray-500">NHIF Code</dt>
                                        <dd className="text-gray-900">{facility.nhif_code}</dd>
                                    </div>
                                )}
                                {facility.verified_date && (
                                    <div>
                                        <dt className="text-sm font-medium text-gray-500">Last Verified</dt>
                                        <dd className="text-gray-900">
                                            {new Date(facility.verified_date).toLocaleDateString()}
                                        </dd>
                                    </div>
                                )}
                            </dl>
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="lg:col-span-1">
                        <div className="card sticky top-20 space-y-6">
                            {/* Location */}
                            <div>
                                <h3 className="text-lg font-bold text-gray-900 mb-3">Location</h3>
                                <div className="space-y-2">
                                    <div className="flex items-start space-x-2">
                                        <span className="text-xl">📍</span>
                                        <div>
                                            <p className="font-medium text-gray-900">{facility.county_name || facility.county}</p>
                                            {facility.town && <p className="text-sm text-gray-600">{facility.town}</p>}
                                            {facility.constituency && (
                                                <p className="text-sm text-gray-600">{facility.constituency}</p>
                                            )}
                                            {facility.address && (
                                                <p className="text-sm text-gray-500 mt-1">{facility.address}</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Contact */}
                            <div>
                                <h3 className="text-lg font-bold text-gray-900 mb-3">Contact</h3>
                                <div className="space-y-3">
                                    {facility.phone && (
                                        <div className="flex items-center space-x-2">
                                            <span className="text-xl">📞</span>
                                            <a
                                                href={`tel:${facility.phone}`}
                                                className="text-primary-600 hover:text-primary-700 font-medium"
                                            >
                                                {formatPhone(facility.phone)}
                                            </a>
                                        </div>
                                    )}
                                    {facility.email && (
                                        <div className="flex items-center space-x-2">
                                            <span className="text-xl">✉️</span>
                                            <a
                                                href={`mailto:${facility.email}`}
                                                className="text-primary-600 hover:text-primary-700 break-all"
                                            >
                                                {facility.email}
                                            </a>
                                        </div>
                                    )}
                                    {facility.website && (
                                        <div className="flex items-center space-x-2">
                                            <span className="text-xl">🌐</span>
                                            <a
                                                href={facility.website}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-primary-600 hover:text-primary-700 break-all"
                                            >
                                                Visit Website
                                            </a>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="space-y-2 pt-4 border-t border-gray-200">
                                {facility.phone && (
                                    <a
                                        href={`tel:${facility.phone}`}
                                        className="btn btn-primary w-full text-center"
                                    >
                                        📞 Call Facility
                                    </a>
                                )}
                                {facility.latitude && facility.longitude && (
                                    <a
                                        href={`https://www.google.com/maps?q=${facility.latitude},${facility.longitude}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn btn-outline w-full text-center"
                                    >
                                        🗺️ Get Directions
                                    </a>
                                )}
                            </div>

                            {/* Demo Status Update (Admin Only in real world) */}
                            <div className="pt-4 border-t border-gray-200">
                                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Update Status (Demo)</h3>
                                <div className="space-y-2">
                                    <select
                                        className="input text-sm"
                                        defaultValue={facility.availability_status}
                                        onChange={(e) => {
                                            if (window.confirm(`Change status to ${e.target.value.toUpperCase()}?`)) {
                                                facilityAPI.updateAvailability(facility.id, e.target.value)
                                                    .then(() => {
                                                        queryClient.invalidateQueries(['facility', uuid]);
                                                        alert('Status updated!');
                                                    })
                                                    .catch(() => alert('Failed to update status'));
                                            }
                                        }}
                                    >
                                        <option value="available">Available</option>
                                        <option value="busy">Busy</option>
                                        <option value="emergency_only">Emergency Only</option>
                                        <option value="closed">Closed</option>
                                    </select>
                                    <p className="text-[10px] text-gray-400">
                                        Note: This simulate an admin dashboard action.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
