import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from facilities.models import Facility, FacilityType
from locations.models import County

county, _ = County.objects.get_or_create(name='Nairobi', code='047')
fac_type, _ = FacilityType.objects.get_or_create(name='Public Hospital')

Facility.objects.get_or_create(
    name='Kenyatta National Hospital',
    facility_type=fac_type,
    county=county,
    is_verified=True,
    is_active=True
)
print("TestData Created")
