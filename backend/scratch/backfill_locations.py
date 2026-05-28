"""Backfill location PointField for facilities with lat/lng."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from facilities.models import Facility
from django.contrib.gis.geos import Point

qs = Facility.objects.filter(
    latitude__isnull=False,
    longitude__isnull=False,
    location__isnull=True,
)
total = qs.count()
print(f"Found {total} facilities to backfill...")

updated = 0
for f in qs.iterator():
    f.location = Point(float(f.longitude), float(f.latitude))
    f.save(update_fields=['location'])
    updated += 1
    if updated % 100 == 0:
        print(f"  Updated {updated}/{total}...")

print(f"Done! Backfilled {updated} facility locations.")
