import os
import django
import sys
import pandas as pd
import numpy as np

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from facilities.models import Facility, FacilityType, Service
from locations.models import County

def import_facilities():
    file_path = '../facility_data/final_facilities.csv'
    
    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path)
    df = df.replace({np.nan: None})
    
    print(f"Total rows to import: {len(df)}")
    
    # Track metrics
    created_count = 0
    updated_count = 0
    
    # Precache lookups
    counties = {c.name.lower(): c for c in County.objects.all()}
    facility_types = {t.name.lower(): t for t in FacilityType.objects.all()}
    
    for i, row in df.iterrows():
        try:
            # 1. County Lookup
            county_name = str(row.get('county', '')).strip().lower()
            county = counties.get(county_name)
            if not county and county_name:
                # Generate a dummy code for imported unseen counties e.g. "048", "049"...
                next_code = str(48 + len(counties)).zfill(3)
                county, _ = County.objects.get_or_create(
                    name=county_name.title(),
                    defaults={'code': next_code, 'region': 'Unknown', 'capital': 'Unknown'}
                )
                counties[county_name] = county
            
            # 2. Facility Type Lookup
            type_name = str(row.get('type', '')).strip()
            if not type_name or type_name == 'None':
                type_name = 'Other'
                
            f_type = facility_types.get(type_name.lower())
            if not f_type:
                f_type, _ = FacilityType.objects.get_or_create(
                    name=type_name.title()[:100]
                )
                facility_types[type_name.lower()] = f_type
                
            # 3. Handle specific booleans 
            # Note: Final data from script-cleaning.py mapping might vary
            is_24_hours = str(row.get('open_24_hours', '')).lower() in ['yes', 'true', '1', 'y']
            
            # Numeric fields
            lat = row.get('latitude')
            lon = row.get('longitude')
            try: lat = float(lat) if lat else None
            except: lat = None
            try: lon = float(lon) if lon else None
            except: lon = None
            
            # Determine facility name from column format
            name = str(row.get('name', 'Unknown Facility')).strip()[:200]
            
            # Extract common columns
            address = str(row.get('official_address', '')).strip()[:100]
            town = str(row.get('town', row.get('nearest_town', ''))).strip()[:100]
            constituency = str(row.get('constituency', '')).strip()[:100]
            
            phone = str(row.get('official_mobile', row.get('official_landline', ''))).strip()[:20]
            email = str(row.get('official_email', '')).strip()[:254]
            if '@' not in email: email = ''
            
            # Prepare kwargs
            defaults = {
                'facility_type': f_type,
                'county': county,
                'constituency': constituency,
                'town': town,
                'latitude': lat,
                'longitude': lon,
                'address': address,
                'phone': phone,
                'email': email,
                'is_24_hours': is_24_hours,
                'is_active': True
            }
            
            # Update or Create Facility
            facility, created = Facility.objects.update_or_create(
                name=name,
                defaults=defaults
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
            if i > 0 and i % 500 == 0:
                print(f"Processed {i} rows... ({created_count} created, {updated_count} updated)")
                
        except Exception as e:
            print(f"Error importing row {i} ({row.get('name')}): {e}")

    print(f"\\n✅ Import Summary \\n=================")
    print(f"Total Created: {created_count}")
    print(f"Total Updated: {updated_count}")

if __name__ == '__main__':
    import_facilities()
