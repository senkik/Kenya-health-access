/**
 * GPS Location utility for "Near Me" facility search.
 * Uses the browser Geolocation API.
 */

/**
 * Get the user's current GPS coordinates.
 * @returns {Promise<{lat: number, lng: number, accuracy: number}>}
 */
export const getUserLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by your browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy,
        });
      },
      (error) => {
        let message;
        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = 'Location permission denied. Please allow location access.';
            break;
          case error.POSITION_UNAVAILABLE:
            message = 'Location information is unavailable.';
            break;
          case error.TIMEOUT:
            message = 'Location request timed out.';
            break;
          default:
            message = 'An unknown error occurred while getting location.';
        }
        reject(new Error(message));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000, // Cache for 1 minute
      }
    );
  });
};

/**
 * Format distance for display.
 * @param {number} km - Distance in kilometres
 * @returns {string}
 */
export const formatDistance = (km) => {
  if (km == null) return '';
  if (km < 1) return `${Math.round(km * 1000)}m`;
  return `${km.toFixed(1)} km`;
};
