from django.test import TestCase
from facilities.models import Facility, FacilityType
from locations.models import County
from .handler import USSDHandler, create_session

class USSDHandlerTest(TestCase):
    def setUp(self):
        self.county = County.objects.create(name="Nairobi", code="047", capital="Nairobi")
        self.facility_type = FacilityType.objects.create(name="Public Hospital")
        self.facility = Facility.objects.create(
            name="Nairobi General",
            facility_type=self.facility_type,
            county=self.county,
            is_verified=True,
            is_active=True,
            availability_status='available'
        )
        # Initialize session properly
        self.session = create_session("test_id", "+254700000000")
        self.handler = USSDHandler(self.session)

    def test_main_menu(self):
        """Test the USSD main menu response"""
        response = self.handler.process_input([], "")
        self.assertIn("Karibu HudumaAfya Kenya", response)
        self.assertIn("1. Tafuta Hospitali", response)

    def test_search_menu(self):
        """Test navigating to the search menu"""
        # Step 1: Main menu
        self.handler.process_input([], "")
        
        # Action: Choose "1"
        response = self.handler.process_input(["1"], "1")
        self.assertIn("Tafuta kwa:", response)
        self.assertIn("1. Jina la Kaunti", response)
        self.assertEqual(self.session['menu_level'], 'search')

    def test_county_search_results(self):
        """Test searching facilities by county in USSD"""
        # Step 1: Call main menu
        self.handler.process_input([], "")
        # Step 2: Choose "1" (Search)
        self.handler.process_input(["1"], "1") 
        # Step 3: Choose "1" (County Search)
        self.handler.process_input(["1", "1"], "1")
        
        # Step 4: Type query "Nairobi"
        text_array = ["1", "1", "Nairobi"]
        response = self.handler.process_input(text_array, "Nairobi")
        self.assertIn("Matokeo:", response)
        self.assertIn("Nairobi General", response)
        
    def test_facility_selection_and_sms(self):
        """Test selecting a facility and triggering SMS"""
        # Manually prep session for speed
        self.session['menu_level'] = 'search'
        self.session['search_results'] = [{
            'id': self.facility.id,
            'name': self.facility.name,
            'phone': '123456',
            'county': 'Nairobi',
            'status': 'available',
            'services': []
        }]
        
        # User is at level 4: selecting facility index "1"
        text_array = ["1", "1", "Nairobi", "1"]
        response = self.handler.process_input(text_array, "1")
        self.assertIn("Nairobi General", response)
        self.assertIn("Tumekutumia maelezo haya kwa SMS", response)
