from django.test import TestCase
from .models import Facility, FacilityType, Service
from locations.models import County

class FacilityModelTest(TestCase):
    def setUp(self):
        # Create test data
        self.county = County.objects.create(
            name="Test County",
            code="999",
            capital="Test Capital"
        )
        
        self.facility_type = FacilityType.objects.create(
            name="Test Hospital",
            icon="🏥"
        )
        
        self.service = Service.objects.create(
            name="Test Service",
            category="general"
        )
    
    def test_facility_creation(self):
        """Test facility creation with county foreign key"""
        facility = Facility.objects.create(
            name="Test Hospital",
            facility_type=self.facility_type,
            county=self.county,
            town="Test Town",
            phone="123-456-7890",
            is_verified=True
        )
        
        facility.services.add(self.service)
        
        self.assertEqual(facility.name, "Test Hospital")
        self.assertEqual(facility.county.name, "Test County")
        self.assertEqual(facility.services.count(), 1)
        self.assertTrue(facility.is_verified)
    
    def test_county_relationship(self):
        """Test facility-county foreign key relationship"""
        facility = Facility.objects.create(
            name="Another Hospital",
            facility_type=self.facility_type,
            county=self.county,
            is_verified=True
        )
        
        # Test reverse relationship
        county_facilities = self.county.facility_set.all()
        self.assertIn(facility, county_facilities)
    
    def test_search_by_county(self):
        """Test searching facilities by county"""
        facility = Facility.objects.create(
            name="County Hospital",
            facility_type=self.facility_type,
            county=self.county,
            is_verified=True
        )
        
        # Search by county name
        facilities = Facility.objects.filter(county__name__icontains="Test")
        self.assertEqual(facilities.count(), 1)
        self.assertEqual(facilities.first().name, "County Hospital")

    def test_facility_average_rating(self):
        """Test the calculation of average rating from reviews"""
        facility = Facility.objects.create(
            name="Rating Hospital",
            facility_type=self.facility_type,
            county=self.county,
            is_verified=True
        )
        
        from .models import Review
        Review.objects.create(facility=facility, rating=5, comment="Great", user_name="User1", is_approved=True)
        Review.objects.create(facility=facility, rating=3, comment="Okay", user_name="User2", is_approved=True)
        Review.objects.create(facility=facility, rating=2, comment="Bad", user_name="User3", is_approved=False) # Not approved
        
        # (5 + 3) / 2 = 4.0
        self.assertEqual(facility.average_rating, 4.0)
        self.assertEqual(facility.total_reviews, 2)

    def test_availability_status_update(self):
        """Test updating facility availability status"""
        facility = Facility.objects.create(
            name="Status Hospital",
            facility_type=self.facility_type,
            county=self.county,
            is_verified=True
        )
        
        self.assertEqual(facility.availability_status, 'available')
        
        facility.availability_status = 'busy'
        facility.save()
        
        updated_facility = Facility.objects.get(id=facility.id)
        self.assertEqual(updated_facility.availability_status, 'busy')