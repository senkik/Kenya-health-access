"""
Update facility coordinates using OpenStreetMap Nominatim geocoding.
Only updates facilities whose coordinates came from county_center or town_center
(i.e. approximate, not actual facility GPS).

Usage: python update_coordinates.py [--limit N] [--dry-run]
"""
import os
import sys
import time
import django
import argparse
import requests
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from facilities.models import Facility

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "kenya-health-access-geocoder/1.0 (contact: admin@kenyahealthaccess.ke)"}
DELAY = 1.1  # seconds between requests (Nominatim rate limit: max 1/sec)

CSV_PATH = '../facility_data/final_facilities.csv'


def geocode(query):
    """Call Nominatim and return (lat, lon) or None."""
    try:
        r = requests.get(NOMINATIM_URL, params={
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'ke',
        }, headers=HEADERS, timeout=10)
        results = r.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except Exception as e:
        print(f"  ! Geocode error for '{query}': {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description='Update facility GPS coordinates via Nominatim')
    parser.add_argument('--limit', type=int, default=200, help='Max facilities to update (default: 200)')
    parser.add_argument('--dry-run', action='store_true', help='Print results without saving to DB')
    args = parser.parse_args()

    # Load the CSV to get coordinate_source info
    print(f"Loading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)

    # Keep only facilities with low-quality coordinates
    low_quality = df[df['coordinate_source'].isin(['county_center', 'town_center'])]
    # Also keep facilities with no coordinates at all or clearly wrong ones
    no_coords = df[df['latitude'].isna() | (df['latitude'] == 0)]
    targets = pd.concat([low_quality, no_coords]).drop_duplicates(subset=['facility_code'])
    
    print(f"Found {len(low_quality)} county/town_center coords, {len(no_coords)} missing coords")
    print(f"Total facilities to try geocoding: {len(targets)}")
    print(f"Processing up to {args.limit} facilities...")
    print()

    updated = 0
    failed = 0
    skipped = 0

    for i, (_, row) in enumerate(targets.iterrows()):
        if i >= args.limit:
            break

        name = str(row.get('name', '')).strip()
        town = str(row.get('town', row.get('nearest_town', ''))).strip()
        county = str(row.get('county', '')).strip()

        # Skip if no meaningful location info
        if not name or name == 'nan':
            skipped += 1
            continue

        # Build progressive search queries (try specific → general)
        queries = []
        if town and town not in ('nan', ''):
            queries.append(f"{name}, {town}, {county}, Kenya")
            queries.append(f"{name}, {county}, Kenya")
            queries.append(f"{town}, {county}, Kenya")
        else:
            queries.append(f"{name}, {county}, Kenya")
            queries.append(f"{county}, Kenya")

        # Find this facility in DB
        try:
            facility = Facility.objects.get(name__iexact=name)
        except Facility.DoesNotExist:
            skipped += 1
            continue
        except Facility.MultipleObjectsReturned:
            # Try with county
            try:
                from locations.models import County
                county_obj = County.objects.filter(name__iexact=county).first()
                facility = Facility.objects.filter(name__iexact=name, county=county_obj).first()
                if not facility:
                    skipped += 1
                    continue
            except Exception:
                skipped += 1
                continue

        coords = None
        for query in queries:
            coords = geocode(query)
            time.sleep(DELAY)
            if coords:
                break

        if coords:
            lat, lon = coords
            # Sanity check: Kenya is roughly lat -5 to 5, lon 33 to 42
            if -5 <= lat <= 5 and 33 <= lon <= 42:
                print(f"OK [{i+1}] {name[:40]:40} -> ({lat:.5f}, {lon:.5f})")
                if not args.dry_run:
                    facility.latitude = lat
                    facility.longitude = lon
                    facility.save(update_fields=['latitude', 'longitude'])
                updated += 1
            else:
                print(f"ERR [{i+1}] {name[:40]:40} -> coordinates out of Kenya bounds: ({lat}, {lon})")
                failed += 1
        else:
            print(f"SEARCH [{i+1}] {name[:40]:40} -> not found")
            failed += 1

    print()
    print("=" * 60)
    print(f"OK Updated : {updated}")
    print(f"ERR Failed  : {failed}")
    print(f"SKIP  Skipped : {skipped}")
    if args.dry_run:
        print("   (Dry run — no DB changes made)")


if __name__ == '__main__':
    main()
