from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from facilities.models import Facility, FacilityType, Review
from locations.models import County

class FacilityAPITest(APITestCase):
    def setUp(self):
        self.county = County.objects.create(name="Nairobi", code="047", capital="Nairobi")
        self.facility_type = FacilityType.objects.create(name="Public Hospital")
        self.facility = Facility.objects.create(
            name="Nairobi General",
            facility_type=self.facility_type,
            county=self.county,
            is_verified=True,
            availability_status='available'
        )
        self.detail_url = reverse('facility-detail', kwargs={'pk': self.facility.id})
        self.update_availability_url = f"{self.detail_url}update_availability/"
        self.reviews_url = reverse('review-list')

    def test_get_facility_detail(self):
        """Test retrieving a single facility detail"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Nairobi General")
        self.assertEqual(response.data['availability_status'], "available")

    def test_update_availability(self):
        """Test the custom action to update availability"""
        data = {'status': 'busy'}
        response = self.client.post(self.update_availability_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'busy')
        
        # Verify in DB
        self.facility.refresh_from_db()
        self.assertEqual(self.facility.availability_status, 'busy')

    def test_update_availability_invalid(self):
        """Test update with invalid status"""
        data = {'status': 'not_a_status'}
        response = self.client.post(self.update_availability_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review(self):
        """Test submitting a review for a facility"""
        data = {
            'facility': self.facility.id,
            'rating': 5,
            'user_name': 'John Doe',
            'comment': 'Excellent service!'
        }
        response = self.client.post(self.reviews_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        
    def test_filter_reviews_by_facility(self):
        """Test listing reviews filtered by facility ID"""
        Review.objects.create(facility=self.facility, rating=4, user_name="Jane", comment="Good", is_approved=True)
        
        response = self.client.get(self.reviews_url, {'facility': self.facility.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Account for pagination: check results list
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['user_name'], "Jane")
