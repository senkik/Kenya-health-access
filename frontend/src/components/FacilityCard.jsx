
import { Link } from 'react-router-dom';
import { formatPhone } from '../utils/helpers';

export default function FacilityCard({ facility }) {
    return (
        <div className="card hover:shadow-lg transition-shadow duration-200">
            {/* Header */}
            <div className="border-b border-gray-200 pb-4 mb-4">
                <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 mb-1">
                            {facility.name}
                        </h3>
                        <p className="text-sm text-gray-600">
                            {facility.facility_type_name || facility.facility_type?.name || 'Healthcare Facility'}
                        </p>
                    </div>
                    {facility.average_rating > 0 && (
                        <div className="flex items-center bg-yellow-50 px-2 py-1 rounded border border-yellow-200">
                            <span className="text-yellow-500 mr-1 text-sm">⭐</span>
                            <span className="font-bold text-gray-900 text-sm">{facility.average_rating}</span>
                            <span className="text-gray-400 text-xs ml-1">({facility.total_reviews})</span>
                        </div>
                    )}
                </div>
                {/* Availability Badge */}
                <div className="mt-2">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${facility.availability_status === 'available' ? 'bg-green-50 text-green-700 border-green-200' :
                        facility.availability_status === 'busy' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                            facility.availability_status === 'emergency_only' ? 'bg-orange-50 text-orange-700 border-orange-200' :
                                'bg-gray-50 text-gray-700 border-gray-200'
                        }`}>
                        <span className={`h-1.5 w-1.5 rounded-full mr-1.5 ${facility.availability_status === 'available' ? 'bg-green-400' :
                            facility.availability_status === 'busy' ? 'bg-yellow-400' :
                                facility.availability_status === 'emergency_only' ? 'bg-orange-400' :
                                    'bg-gray-400'
                            }`}></span>
                        {facility.availability_status?.replace('_', ' ').toUpperCase() || 'AVAILABLE'}
                    </span>
                </div>
            </div>

            {/* Location */}
            <div className="space-y-3">
                <div className="flex items-start space-x-2">
                    <span className="text-lg">📍</span>
                    <div className="flex-1">
                        <p className="font-medium text-gray-900">{facility.county}</p>
                        {facility.town && (
                            <p className="text-sm text-gray-600">{facility.town}</p>
                        )}
                        {facility.address && (
                            <p className="text-sm text-gray-500 mt-1">{facility.address}</p>
                        )}
                    </div>
                </div>

                {/* Phone */}
                {facility.phone && (
                    <div className="flex items-center space-x-2">
                        <span className="text-lg">📞</span>
                        <a
                            href={`tel:${facility.phone}`}
                            className="text-primary-600 hover:text-primary-700 font-medium"
                        >
                            {formatPhone(facility.phone)}
                        </a>
                    </div>
                )}

                {/* Email */}
                {facility.email && (
                    <div className="flex items-center space-x-2">
                        <span className="text-lg">✉️</span>
                        <a
                            href={`mailto:${facility.email}`}
                            className="text-primary-600 hover:text-primary-700 text-sm"
                        >
                            {facility.email}
                        </a>
                    </div>
                )}
            </div>

            {/* Badges */}
            <div className="flex flex-wrap gap-2 mt-4">
                {facility.accepts_sha && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        ✓ SHA Accepted
                    </span>
                )}
                {facility.emergency_available && (
                    <span className="px-3 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                        🚨 Emergency Services
                    </span>
                )}
                {facility.is_24_hours && (
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                        🕐 24 Hours
                    </span>
                )}
                {facility.is_verified && (
                    <span className="px-3 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded-full">
                        ✓ Verified
                    </span>
                )}
            </div>

            {/* Services */}
            {facility.services && facility.services.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Services:</p>
                    <p className="text-sm text-gray-600">
                        {facility.services.slice(0, 3).map(s => s.name).join(', ')}
                        {facility.services.length > 3 && '...'}
                    </p>
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 mt-6">
                {facility.phone && (
                    <a
                        href={`tel:${facility.phone}`}
                        className="btn btn-outline flex-1 text-center"
                    >
                        Call
                    </a>
                )}
                <Link
                    to={`/facility/${facility.uuid}`}
                    className="btn btn-primary flex-1 text-center"
                >
                    View Details
                </Link>
            </div>
        </div>
    );
}
