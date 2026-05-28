import pandas as pd
import argparse
from datetime import datetime
import sys
import os

# Add the project root to the path so we can import from data.utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from data.utils.geocode_addresses import geocode_with_nominatim
except ImportError:
    print("Warning: Could not import geocode_addresses. Nominatim geocoding will be skipped.")
    geocode_with_nominatim = None

# We need COUNTY_CENTERS which seem to be missing from the files
COUNTY_CENTERS = {
    'Baringo': (0.466667, 35.966667),
    'Bomet': (-0.783333, 35.350000),
    'Bungoma': (0.566667, 34.566667),
    'Busia': (0.460000, 34.110000),
    'Elgeyo-Marakwet': (0.800000, 35.500000),
    'Embu': (-0.533333, 37.450000),
    'Garissa': (-0.456944, 39.658333),
    'Homa Bay': (-0.516667, 34.450000),
    'Isiolo': (0.350000, 37.583333),
    'Kajiado': (-1.850000, 36.783333),
    'Kakamega': (0.284767, 34.752308),
    'Kericho': (-0.366667, 35.283333),
    'Kiambu': (-1.166667, 36.833333),
    'Kilifi': (-3.633333, 39.850000),
    'Kirinyaga': (-0.500000, 37.283333),
    'Kisii': (-0.683333, 34.766667),
    'Kisumu': (-0.102210, 34.761711),
    'Kitui': (-1.366667, 38.016667),
    'Kwale': (-4.183333, 39.450000),
    'Laikipia': (0.366667, 37.033333),
    'Lamu': (-2.266667, 40.900000),
    'Machakos': (-1.516667, 37.266667),
    'Makueni': (-1.800000, 37.616667),
    'Mandera': (3.933333, 41.866667),
    'Marsabit': (2.333333, 37.983333),
    'Meru': (0.050000, 37.650000),
    'Migori': (-1.066667, 34.466667),
    'Mombasa': (-4.043477, 39.668205),
    'Murang\'a': (-0.716667, 37.150000),
    'Nairobi': (-1.286389, 36.817223),
    'Nakuru': (-0.303099, 36.080026),
    'Nandi': (0.166667, 35.133333),
    'Narok': (-1.083333, 35.866667),
    'Nyamira': (-0.633333, 34.933333),
    'Nyandarua': (-0.183333, 36.366667),
    'Nyeri': (-0.416667, 36.950000),
    'Samburu': (1.316667, 36.983333),
    'Siaya': (0.066667, 34.283333),
    'Taita-Taveta': (-3.400000, 38.350000),
    'Tana River': (-1.500000, 40.033333),
    'Tharaka-Nithi': (-0.300000, 38.000000),
    'Trans Nzoia': (1.016667, 34.983333),
    'Turkana': (3.116667, 35.600000),
    'Uasin Gishu': (0.516667, 35.283333),
    'Vihiga': (0.083333, 34.716667),
    'Wajir': (1.750000, 40.066667),
    'West Pokot': (1.233333, 35.116667)
}


class CoordinateEnricher:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.df = pd.read_csv(input_file)
        self.stats = {
            'total': len(self.df),
            'already_had_coords': 0,
            'geocoded_nominatim': 0,
            'county_center': 0,
            'town_center': 0,
            'still_missing': 0
        }
    
    def count_existing_coords(self):
        """Count facilities that already have coordinates"""
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            self.stats['already_had_coords'] = 0
            self.df['latitude'] = None
            self.df['longitude'] = None
            self.df['coordinate_source'] = None
            print("✅ 0 facilities already have coordinates (columns missing)")
            return
            
        has_coords = (
            pd.notna(self.df['latitude']) & 
            pd.notna(self.df['longitude']) &
            (self.df['latitude'] != 0) &
            (self.df['longitude'] != 0)
        )
        self.stats['already_had_coords'] = has_coords.sum()
        print(f"✅ {self.stats['already_had_coords']} facilities already have coordinates")
        
    def apply_nominatim(self):
        """Geocode missing coordinates using Nominatim"""
        if not geocode_with_nominatim:
            print("Skipping Nominatim geocoding since module is not available.")
            return

        print('Starting Nominatim geocoding (this will be slow due to rate limiting)...')
        attempts = 0
        for idx, row in self.df.iterrows():
            # Skip if already has coordinates
            if pd.notna(row.get('latitude')) and row.get('latitude') != 0:
                continue

            # Only process up to 5 missing items to avoid long script execution during testing
            if attempts >= 5:
                break
                
            lat, lon, source = geocode_with_nominatim(
                row.get('name', ''),
                row.get('town', ''),
                row.get('county', '')
            )
            attempts += 1
            
            if lat and lon:
                self.df.at[idx, 'latitude'] = lat
                self.df.at[idx, 'longitude'] = lon
                self.df.at[idx, 'coordinate_source'] = source
                self.stats['geocoded_nominatim'] += 1
                
        print(f"🌍 Geocoded {self.stats['geocoded_nominatim']} facilities using Nominatim (out of {attempts} attempts)")

    def apply_town_centers(self):
        """Apply town center coordinates"""
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
        
        for idx, row in self.df.iterrows():
            # Skip if already has coordinates
            if pd.notna(row.get('latitude')) and row.get('latitude') != 0:
                continue
            
            town = str(row.get('town', '')).strip().title()
            if town in TOWN_CENTERS:
                lat, lon = TOWN_CENTERS[town]
                self.df.at[idx, 'latitude'] = lat
                self.df.at[idx, 'longitude'] = lon
                self.df.at[idx, 'coordinate_source'] = f'town_center'
                self.stats['town_center'] += 1
    
    def apply_county_centers(self):
        """Apply county center coordinates as fallback"""
        for idx, row in self.df.iterrows():
            # Skip if already has coordinates
            if pd.notna(row.get('latitude')) and row.get('latitude') != 0:
                continue
            
            county = str(row.get('county', '')).strip()
            
            for county_name, (lat, lon) in COUNTY_CENTERS.items():
                if county_name.lower() in county.lower():
                    self.df.at[idx, 'latitude'] = lat
                    self.df.at[idx, 'longitude'] = lon
                    self.df.at[idx, 'coordinate_source'] = f'county_center'
                    self.stats['county_center'] += 1
                    break
    
    def mark_still_missing(self):
        """Mark facilities still without coordinates"""
        missing = (
            pd.isna(self.df.get('latitude')) | 
            (self.df.get('latitude') == 0)
        )
        self.stats['still_missing'] = missing.sum()
        
        # Create review list
        if self.stats['still_missing'] > 0:
            missing_df = self.df[missing][['name', 'county', 'town', 'official_address']] if 'official_address' in self.df.columns else self.df[missing]
            missing_df.to_csv('facilities_needing_review.csv', index=False)
            print(f"📝 Created review list for {self.stats['still_missing']} facilities")
    
    def run(self):
        """Execute all strategies"""
        print(f"🚀 Starting coordinate enrichment for {self.stats['total']} facilities")
        print("=" * 50)
        
        self.count_existing_coords()
        self.apply_nominatim()
        self.apply_town_centers()
        self.apply_county_centers()
        self.mark_still_missing()
        
        print("\n📊 Final Statistics:")
        for key, value in self.stats.items():
            percentage = (value / self.stats['total']) * 100
            print(f"  {key}: {value} ({percentage:.1f}%)")
        
        # Save results
        self.df.to_csv(self.output_file, index=False)
        print(f"\n✅ Saved enriched data to {self.output_file}")
        
        return self.df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', default='facilities_with_coords.csv', help='Output CSV file')
    
    args = parser.parse_args()
    
    enricher = CoordinateEnricher(args.input, args.output)
    enricher.run()