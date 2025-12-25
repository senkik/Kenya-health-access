import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect } from 'react';
import { Link } from 'react-router-dom';

// Fix for default marker icons in Leaflet with Webpack/Vite
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: markerIcon,
    iconRetinaUrl: markerIconRetina,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Component to handle map view updates
function MapViewUpdater({ facilities, center }) {
    const map = useMap();

    useEffect(() => {
        if (center) {
            map.setView(center, map.getZoom());
        } else if (facilities && facilities.length > 0) {
            // Fit bounds to show all markers
            const validFacilities = facilities.filter(f => f.latitude && f.longitude);
            if (validFacilities.length > 0) {
                const bounds = L.latLngBounds(validFacilities.map(f => [f.latitude, f.longitude]));
                map.fitBounds(bounds, { padding: [50, 50] });
            }
        }
    }, [facilities, center, map]);

    return null;
}

export default function FacilityMap({ facilities = [], center, zoom = 6, height = "400px" }) {
    const kenyaCenter = [-1.2921, 36.8219]; // Nairobi

    return (
        <div style={{ height, width: '100%' }} className="rounded-lg overflow-hidden shadow-md border border-gray-200 z-0">
            <MapContainer
                center={center || kenyaCenter}
                zoom={zoom}
                scrollWheelZoom={true}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {facilities.filter(f => f.latitude && f.longitude).map((facility) => (
                    <Marker
                        key={facility.uuid || facility.id}
                        position={[facility.latitude, facility.longitude]}
                    >
                        <Popup>
                            <div className="p-1">
                                <h3 className="font-bold text-gray-900">{facility.name}</h3>
                                <p className="text-sm text-gray-600 mb-2">{facility.facility_type?.name}</p>
                                <Link
                                    to={`/facility/${facility.uuid}`}
                                    className="text-xs font-medium text-primary-600 hover:text-primary-700 underline"
                                >
                                    View Details
                                </Link>
                            </div>
                        </Popup>
                    </Marker>
                ))}

                <MapViewUpdater facilities={facilities} center={center} />
            </MapContainer>
        </div>
    );
}
