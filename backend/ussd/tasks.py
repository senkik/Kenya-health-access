from celery import shared_task
from django.core.cache import cache
import logging
import os
from location.service import NetworkLocationService
from location.demo import DemoLocationService
from facilities.models import Facility
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.conf import settings
from utils.sms import SMSService

logger = logging.getLogger(__name__)

# Initialize SMS Service
sms_service = SMSService()

@shared_task
def process_location_request(phone_number):
    """
    Process USSD location request asynchronously
    """
    
    if os.getenv('USE_DEMO_LOCATION') == 'True' or getattr(settings, 'USE_DEMO_LOCATION', False):
        location_service = DemoLocationService()
    else:
        location_service = NetworkLocationService()
        
    location = location_service.get_location(phone_number)
    
    if not location:
        location = location_service.get_location_fallback(phone_number)
    
    if not location:
        sms_service.send_sms(phone_number, "Samahani, hatukuweza kupata eneo lako. Tafadhali jaribu tena baadaye.")
        return
    
    cache.set(f"user_location_{phone_number}", location, 1800)
    
    facilities = find_nearby_facilities(
        lat=location['lat'],
        lon=location['lon'],
        radius_km=10,
        limit=3
    )
    
    sms_service.send_facility_list(phone_number, facilities)

def find_nearby_facilities(lat, lon, radius_km=10, limit=3):
    """
    Find facilities within radius using PostGIS
    """
    if lat is None or lon is None:
        return []
        
    user_location = Point(float(lon), float(lat), srid=4326)
    
    facilities = Facility.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).annotate(
        distance=Distance('location', user_location)
    ).filter(
        distance__lte=radius_km * 1000
    ).order_by('distance')[:limit]
    
    results = []
    for facility in facilities:
        distance_km = facility.distance.m / 1000 if hasattr(facility, 'distance') and facility.distance else 0
        results.append({
            'name': facility.name,
            'distance': round(distance_km, 1),
            'phone': facility.phone or 'N/A',
            'county': facility.county.name,
            'town': facility.town or '',
            'emergency': facility.emergency_available
        })
    
    return results
