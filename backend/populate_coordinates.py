import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from facilities.models import Facility

def populate_coordinates():
    # Kenyatta National Hospital
    knh = Facility.objects.filter(name__icontains="Kenyatta National Hospital").first()
    if knh:
        knh.latitude = -1.3013
        knh.longitude = 36.8016
        knh.save()
        print(f"Updated {knh.name} with coordinates.")
    
    # Test Hospital (generic location in Nairobi)
    test_hosp = Facility.objects.filter(name__icontains="Test Hospital").first()
    if test_hosp:
        test_hosp.latitude = -1.2921
        test_hosp.longitude = 36.8219
        test_hosp.save()
        print(f"Updated {test_hosp.name} with coordinates.")

    # Any other facilities without coordinates
    others = Facility.objects.filter(latitude__isnull=True)
    for i, fac in enumerate(others):
        # Slightly offset from Nairobi center for variety
        fac.latitude = -1.2921 + (i * 0.01)
        fac.longitude = 36.8219 + (i * 0.01)
        fac.save()
        print(f"Updated {fac.name} with default coordinates.")

if __name__ == "__main__":
    populate_coordinates()
