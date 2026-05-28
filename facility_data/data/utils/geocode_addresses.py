# utils/geocode_addresses.py
import requests
import time
from urllib.parse import quote

def geocode_with_nominatim(facility_name, town, county):
    """Geocode using OpenStreetMap's Nominatim (free, rate limited)"""
    
    # Build search query
    query_parts = []
    if facility_name and str(facility_name).strip() != 'nan':
        query_parts.append(str(facility_name).strip())
    if town and str(town).strip() != 'nan':
        query_parts.append(str(town).strip())
    if county and str(county).strip() != 'nan':
        query_parts.append(f"{str(county).strip()} County")
    query_parts.append("Kenya")
    
    query = ", ".join(query_parts)
    encoded_query = quote(query)
    
    # Nominatim API (free, but respect rate limits)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=1"
    
    # Add user agent (required)
    headers = {
        'User-Agent': 'KenyaHealthAccess/1.0 (your-email@example.com)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        time.sleep(1)  # Respect rate limit (1 request per second)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon, 'nominatim'
    except Exception as e:
        print(f"Geocoding error for {query}: {e}")
    
    return None, None, None

def batch_geocode(df, batch_size=50):
    """Batch geocode facilities"""
    geocoded = []
    
    for idx, row in df.iterrows():
        if idx % 10 == 0:
            print(f"Geocoding {idx}/{len(df)}...")
        
        lat, lon, source = geocode_with_nominatim(
            row.get('name', ''),
            row.get('town', ''),
            row.get('county', '')
        )
        
        geocoded.append({
            'latitude': lat,
            'longitude': lon,
            'coordinate_source': source
        })
    
    return pd.DataFrame(geocoded)