import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { facilityAPI } from '../services/api';
import Layout from '../components/Layout';
import { Link } from 'react-router-dom';

export default function Manage() {
    const queryClient = useQueryClient();
    const [search, setSearch] = useState('');

    const { data: facilitiesData, isLoading } = useQuery({
        queryKey: ['facilities', 'manage'],
        queryFn: () => facilityAPI.getAll({ limit: 100 }),
    });

    const updateStatusMutation = useMutation({
        mutationFn: ({ id, status }) => facilityAPI.updateAvailability(id, status),
        onSuccess: () => {
            queryClient.invalidateQueries(['facilities', 'manage']);
            alert('Status updated successfully!');
        },
    });

    const facilities = facilitiesData?.data?.results || [];
    const filteredFacilities = facilities.filter(f =>
        f.name.toLowerCase().includes(search.toLowerCase())
    );

    const getStatusColor = (status) => {
        switch (status) {
            case 'available': return 'bg-green-100 text-green-800 border-green-200';
            case 'busy': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'emergency_only': return 'bg-orange-100 text-orange-800 border-orange-200';
            case 'closed': return 'bg-gray-100 text-gray-800 border-gray-200';
            default: return 'bg-blue-100 text-blue-800 border-blue-200';
        }
    };

    return (
        <Layout>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Manage Facilities</h1>
                    <p className="text-gray-600 mt-2">Quickly update availability and manage facility data.</p>
                </div>

                <div className="mb-6">
                    <input
                        type="text"
                        placeholder="Search your facilities..."
                        className="input max-w-md"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 gap-6">
                        {filteredFacilities.map(facility => (
                            <div key={facility.id} className="card flex flex-col md:flex-row md:items-center justify-between gap-4">
                                <div>
                                    <h2 className="text-xl font-bold text-gray-900">{facility.name}</h2>
                                    <p className="text-sm text-gray-500">{facility.county_name} • {facility.facility_type_name}</p>
                                    <div className="mt-2 flex items-center space-x-2">
                                        <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${getStatusColor(facility.availability_status)}`}>
                                            {facility.availability_status?.toUpperCase()}
                                        </span>
                                        <span className="text-[10px] text-gray-400">
                                            Last updated: {new Date(facility.last_status_update).toLocaleString()}
                                        </span>
                                    </div>
                                </div>

                                <div className="flex flex-wrap items-center gap-3">
                                    <select
                                        className="input text-sm !py-1.5"
                                        value={facility.availability_status}
                                        onChange={(e) => updateStatusMutation.mutate({ id: facility.id, status: e.target.value })}
                                        disabled={updateStatusMutation.isLoading}
                                    >
                                        <option value="available">Set Available</option>
                                        <option value="busy">Set Busy</option>
                                        <option value="emergency_only">Set Emergency Only</option>
                                        <option value="closed">Set Closed</option>
                                    </select>

                                    <Link
                                        to={`/facility/${facility.uuid}`}
                                        className="btn btn-outline !py-1.5 text-sm"
                                    >
                                        View Details
                                    </Link>

                                    <Link
                                        to={`/admin/facilities/facility/${facility.id}/change/`}
                                        target="_blank"
                                        className="btn btn-primary !py-1.5 text-sm"
                                    >
                                        Edit All Info
                                    </Link>
                                </div>
                            </div>
                        ))}

                        {filteredFacilities.length === 0 && (
                            <div className="text-center py-12 bg-white rounded-xl border-2 border-dashed border-gray-200">
                                <p className="text-gray-500">No facilities found matching your search.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </Layout>
    );
}
