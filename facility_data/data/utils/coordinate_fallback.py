# utils/coordinate_fallback.py
def smart_coordinate_fallback(df):
    """Intelligent fallback strategy for missing coordinates"""
    
    # Priority 1: Google Maps (most accurate)
    # Priority 2: Nominatim (free but rate limited)
    # Priority 3: County centers (approximate)
    # Priority 4: Town centers (if town known)
    # Priority 5: Manual review list
    
    results = []
    
    # Town centers (approximate)
    TOWN_CENTERS = {
        'Nairobi': (-1.286389, 36.817223),
        'Mombasa': (-4.043477, 39.668205),
        'Kisumu': (-0.102210, 34.761711),
        'Eldoret': (0.514277, 35.269779),
        'Nakuru': (-0.303099, 36.080026),
        'Thika': (-1.033333, 37.066667),
        'Malindi': (-3.216667, 40.116667),
        'Kitale': (1.016667, 34.983333),
        'Garissa': (-0.456944, 39.658333),
        'Kakamega': (0.284767, 34.752308),
        'Machakos': (-1.516667, 37.266667),
        'Meru': (0.050000, 37.650000),
        'Nyeri': (-0.416667, 36.950000),
        'Embu': (-0.533333, 37.450000),
        'Kitui': (-1.366667, 38.016667),
    }
    
    for idx, row in df.iterrows():
        # Check if coordinates already exist
        if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
            if row['latitude'] != 0 and row['longitude'] != 0:
                results.append({
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'coordinate_source': 'existing'
                })
                continue
        
        # Try town center if available
        town = str(row.get('town', '')).strip().title()
        if town in TOWN_CENTERS:
            lat, lon = TOWN_CENTERS[town]
            results.append({
                'latitude': lat,
                'longitude': lon,
                'coordinate_source': f'town_center_{town}'
            })
            continue
        
        # Fallback to county center
        county = str(row.get('county', '')).strip()
        matched = False
        for county_name, (lat, lon) in COUNTY_CENTERS.items():
            if county_name.lower() in county.lower():
                results.append({
                    'latitude': lat,
                    'longitude': lon,
                    'coordinate_source': f'county_center_{county_name}'
                })
                matched = True
                break
        
        if not matched:
            # No coordinates at all
            results.append({
                'latitude': None,
                'longitude': None,
                'coordinate_source': 'missing'
            })
    
    return pd.DataFrame(results)