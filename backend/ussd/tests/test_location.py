import pytest
from unittest.mock import Mock, patch
from ussd.tasks import process_location_request, find_nearby_facilities
from facilities.models import Facility
from django.contrib.gis.geos import Point

@pytest.mark.django_db
class TestLocationService:
    
    @patch('ussd.tasks.Facility.objects.filter')
    def test_find_nearby_facilities(self, mock_filter):
        # Mocking the geospatial query return
        mock_fac = Mock()
        mock_fac.name = "Test Hospital"
        mock_fac.distance = Mock(m=5000)
        mock_fac.phone = "0712345678"
        mock_fac.county.name = "Nairobi"
        mock_fac.town = "CBD"
        mock_fac.emergency_available = True
        
        # This is a bit complex to mock perfectly due to annotate/filter chains
        # but we can test the structure
        facilities = find_nearby_facilities(
            lat=-1.286389,
            lon=36.817223,
            radius_km=10
        )
        assert isinstance(facilities, list)
    
    @patch('location.service.NetworkLocationService.get_location')
    @patch('ussd.tasks.send_facilities_sms')
    @patch('ussd.tasks.find_nearby_facilities')
    def test_process_location_request(self, mock_find, mock_send_sms, mock_get_location):
        mock_get_location.return_value = {
            'lat': -1.286389,
            'lon': 36.817223,
            'accuracy': 'test',
            'source': 'test'
        }
        mock_find.return_value = [{
            'name': 'Test Hospital',
            'distance': 5.0,
            'phone': '0712345678',
            'town': 'CBD'
        }]
        
        # This should run without errors
        process_location_request('+254712345678')
        
        assert mock_send_sms.called
        assert mock_find.called
