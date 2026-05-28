"""
Fast bulk import of facilities_for_postgres.csv into Neon PostgreSQL.
Uses bulk_create with ignore_conflicts to stay within connection timeouts.
"""
import os, sys, django, csv, uuid, traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from facilities.models import Facility, FacilityType
from locations.models import County

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'facility_data', 'facilities_for_postgres.csv')

TYPE_MAP = {
    'dispensary': 'Dispensary',
    'health centre': 'Health Centre',
    'medical clinic': 'Medical Clinic',
    'medical centre': 'Medical Centre',
    'sub-district hospital': 'Sub-District Hospital',
    'district hospital': 'District Hospital',
    'other hospital': 'Other Hospital',
    'nursing home': 'Nursing Home',
    'maternity home': 'Maternity Home',
    'dental clinic': 'Dental Clinic',
    'vct centre (stand-alone)': 'VCT Centre',
    'eye centre': 'Eye Centre',
    'radiology unit': 'Radiology',
    'health programme': 'Health Programme',
}

def safe_float(val):
    try:
        f = float(val)
        return f if f != 0.0 else None
    except (TypeError, ValueError):
        return None

def main():
    now = datetime.now(timezone.utc)

    print(f"Reading {CSV_PATH} ...")
    with open(CSV_PATH, encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    print(f"Total rows: {len(rows)}")

    # --- Step 1: Collect all unique county names and type names ---
    county_names = set()
    type_names = set()
    for row in rows:
        c = row.get('county', '').strip().title()
        if c:
            county_names.add(c)
        t = row.get('type', '').strip()
        mapped = TYPE_MAP.get(t.lower(), t.title()[:100])
        if mapped:
            type_names.add(mapped)

    # --- Step 2: Bulk upsert counties ---
    print(f"Upserting {len(county_names)} counties...")
    existing_counties = {c.name: c for c in County.objects.all()}
    new_counties = [
        County(name=n, code='000', capital='Unknown', region='Unknown')
        for n in county_names if n not in existing_counties
    ]
    if new_counties:
        County.objects.bulk_create(new_counties, ignore_conflicts=True)
    counties = {c.name: c for c in County.objects.all()}
    print(f"  Total counties: {len(counties)}")

    # --- Step 3: Bulk upsert facility types ---
    print(f"Upserting {len(type_names)} facility types...")
    existing_types = {ft.name: ft for ft in FacilityType.objects.all()}
    new_types = [
        FacilityType(name=n)
        for n in type_names if n not in existing_types
    ]
    if new_types:
        FacilityType.objects.bulk_create(new_types, ignore_conflicts=True)
    ftypes = {ft.name: ft for ft in FacilityType.objects.all()}
    print(f"  Total facility types: {len(ftypes)}")

    # --- Step 4: Get existing facility names to skip duplicates ---
    print("Loading existing facility names...")
    existing_names = set(Facility.objects.values_list('name', flat=True))
    print(f"  Already in DB: {len(existing_names)}")

    # --- Step 5: Build facility objects in chunks and bulk_create ---
    CHUNK = 500
    total_created = 0
    total_skipped = 0
    total_errors = 0
    batch = []

    for i, row in enumerate(rows):
        name = row.get('name', '').strip()[:200]
        if not name or name in existing_names:
            total_skipped += 1
            continue

        try:
            county_name = row.get('county', '').strip().title()
            county = counties.get(county_name)

            t = row.get('type', '').strip()
            mapped_type = TYPE_MAP.get(t.lower(), t.title()[:100])
            ftype = ftypes.get(mapped_type)

            if not county or not ftype:
                total_errors += 1
                continue

            phone = str(row.get('official_mobile') or row.get('official_landline') or '').strip()[:20]
            email = str(row.get('official_email') or '').strip()[:254]
            if '@' not in email:
                email = ''
            address = str(row.get('official_address') or '').strip()[:100]
            town = str(row.get('town') or row.get('nearest_town') or '').strip()[:100]
            constituency = str(row.get('constituency') or '').strip()[:100]
            is_24h = str(row.get('open_24_hours', 'f')).strip().lower() in ('t', 'true', 'yes', '1')
            op_status = str(row.get('operational_status', '')).strip().lower()
            is_active = op_status == 'operational'

            obj = Facility(
                name=name,
                facility_type=ftype,
                county=county,
                constituency=constituency,
                town=town,
                latitude=safe_float(row.get('latitude')),
                longitude=safe_float(row.get('longitude')),
                address=address,
                phone=phone,
                email=email,
                is_24_hours=is_24h,
                is_active=is_active,
                uuid=uuid.uuid4(),
                created_at=now,
                updated_at=now,
                availability_status='available',
                last_status_update=now,
            )
            batch.append(obj)
            existing_names.add(name)  # prevent dupes within this batch

            if len(batch) >= CHUNK:
                Facility.objects.bulk_create(batch, ignore_conflicts=True)
                total_created += len(batch)
                batch = []
                print(f"  Inserted chunk — total created so far: {total_created}")

        except Exception as e:
            total_errors += 1
            print(f"  ERROR row {i} ({name}): {e}")

    # Final batch
    if batch:
        Facility.objects.bulk_create(batch, ignore_conflicts=True)
        total_created += len(batch)

    print(f"\n✅ Done!")
    print(f"   Created : {total_created}")
    print(f"   Skipped : {total_skipped}")
    print(f"   Errors  : {total_errors}")
    print(f"   Total in DB: {Facility.objects.count()}")

if __name__ == '__main__':
    main()
