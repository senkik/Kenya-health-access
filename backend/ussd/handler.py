"""
USSD Handler for Kenya Health Access - OPTIMIZED FOR SPEED
Lazy loading prevents timeouts on Render free tier
"""
import json
from datetime import datetime
from django.db.models import Q

# Don't import heavy models at top level - import when needed
# from facilities.models import Facility, County, Service  # REMOVED - will import lazily
# from content.models import HealthTip  # REMOVED - will import lazily
# from utils.sms import SMSService  # REMOVED - will import lazily
# from .tasks import process_location_request  # REMOVED - will import lazily


class USSDHandler:
    """Handles USSD session flows - OPTIMIZED for speed"""
    
    def __init__(self, session):
        self.session = session
        self._sms_service = None
        self._facility_model = None
    
    def _get_sms_service(self):
        """Lazy load SMS service - only when needed"""
        if self._sms_service is None:
            from utils.sms import SMSService
            self._sms_service = SMSService()
        return self._sms_service
    
    def _get_facility_model(self):
        """Lazy load Facility model - only when needed"""
        if self._facility_model is None:
            from facilities.models import Facility
            self._facility_model = Facility
        return self._facility_model
    
    def process_input(self, text_array, last_input):
        """Main USSD flow processor - FAST PATH for main menu"""
        # FAST PATH: Main menu requires no database or external calls
        if len(text_array) == 0:
            return self.main_menu()
        
        # Get current menu level from session or default
        menu_level = self.session.get('menu_level', 'main')
        
        if menu_level == 'main':
            return self.handle_main_menu(text_array, last_input)
        elif menu_level == 'search':
            return self.handle_search_flow(text_array, last_input)
        elif menu_level == 'health_tips':
            return self.handle_health_tips(text_array, last_input)
        
        return self.error_message()
    
    def main_menu(self):
        """Main USSD Menu in Swahili - PURE STRING, NO DATABASE"""
        self.session['menu_level'] = 'main'
        return """CON Karibu HudumaAfya Kenya
1. Tafuta Hospitali/Kliniki
2. Tafuta karibu nami
3. Ushauri wa Afya
4. Nambari za Dharura
5. Kuhusu Sisi

Chagua nambari:"""
    
    def handle_main_menu(self, text_array, last_input):
        """Handle main menu selections"""
        if last_input == "1":
            self.session['menu_level'] = 'search'
            self.session['search_step'] = 1
            return self.search_menu()
        elif last_input == "2":
            # Lazy import for task - only when needed
            from .tasks import process_location_request
            phone_number = self.session.get('phone_number')
            process_location_request.delay(phone_number)
            return "END Tunaangalia eneo lako... tafadhali subiri. Utapokea SMS ndani ya sekunde 30."
        elif last_input == "3":
            self.session['menu_level'] = 'health_tips'
            return self.health_tips_menu()
        elif last_input == "4":
            return self.emergency_numbers()
        elif last_input == "5":
            return self.about_us()
        else:
            return "END Chaguo sio sahihi. Tafadhali jaribu tena."
    
    def search_menu(self):
        """Search facility menu - PURE STRING"""
        return """CON Tafuta kwa:
1. Jina la Kaunti
2. Jina la Hospitali
3. Huduma Unayotaka
4. Jina la Mji/Eneo

Chagua nambari:"""
    
    def handle_search_flow(self, text_array, last_input):
        """Handle search flow with real database queries"""
        search_step = self.session.get('search_step', 1)

        # Level 1: Choose search type
        if search_step == 1:
            if last_input == "1":
                self.session['search_type'] = 'county'
                self.session['search_step'] = 2
                return "CON Andika jina la kaunti yako:"
            elif last_input == "2":
                self.session['search_type'] = 'facility_name'
                self.session['search_step'] = 2
                return "CON Andika jina la hospitali:"
            elif last_input == "3":
                self.session['search_type'] = 'service'
                self.session['search_step'] = 2
                return "CON Andika huduma unayotaka:"
            elif last_input == "4":
                self.session['search_type'] = 'town'
                self.session['search_step'] = 2
                return "CON Andika jina la mji au eneo lako:"
            elif last_input == "0":
                return self.main_menu()
            else:
                return "END Chaguo sio sahihi."
        
        # Level 2: Process search query
        elif search_step == 2:
            if last_input == "0":
                self.session['search_step'] = 1
                return self.search_menu()

            search_type = self.session.get('search_type')
            search_query = last_input
            
            # Store for later use
            self.session['last_search'] = {
                'type': search_type,
                'query': search_query,
                'timestamp': datetime.now().isoformat()
            }
            
            # Perform actual database search (now using lazy-loaded model)
            facilities = self.search_facilities(search_type, search_query)
            self.session['search_results'] = [
                {
                    'id': fac.id,
                    'name': fac.name,
                    'phone': fac.phone or 'N/A',
                    'county': fac.county.name if hasattr(fac, 'county') and fac.county else fac.county_name,
                    'town': fac.town or '',
                    'status': getattr(fac, 'availability_status', 'available'),
                    'services': [s.name for s in fac.services.all()[:2]] if hasattr(fac, 'services') else []
                }
                for fac in facilities[:5]  # Limit to 5 for USSD
            ]
            
            self.session['search_step'] = 3
            return self.format_search_results()
        
        # Level 3: Facility selection
        elif search_step == 3:
            if last_input == "0":
                self.session['search_step'] = 1
                return self.search_menu()
            return self.handle_facility_selection(last_input)
        
        return self.error_message()
    
    def search_facilities(self, search_type, query):
        """Search facilities in database - uses lazy-loaded model"""
        Facility = self._get_facility_model()
        
        facilities = Facility.objects.filter(is_active=True)
        
        query = query.strip()
        
        if search_type == 'county':
            # Handle both ForeignKey and CharField county
            try:
                facilities = facilities.filter(county__name__icontains=query)
            except:
                facilities = facilities.filter(county__icontains=query)
        elif search_type == 'facility_name':
            facilities = facilities.filter(name__icontains=query)
        elif search_type == 'service':
            facilities = facilities.filter(services__name__icontains=query).distinct()
        elif search_type == 'town':
            facilities = facilities.filter(
                Q(town__icontains=query) | Q(address__icontains=query)
            )
        
        return facilities.order_by('name')[:10]
    
    def format_search_results(self):
        """Format search results for USSD - NO DATABASE CALLS"""
        results = self.session.get('search_results', [])
        
        if not results:
            return "END Hakuna hospitali zilizopatikana. Jaribu tena."
        
        response = "CON Matokeo:\n"
        status_icons = {
            'busy': '!',
            'emergency_only': '🚨',
            'closed': 'X',
            'available': '✓'
        }
        
        for i, fac in enumerate(results, 1):
            icon = status_icons.get(fac.get('status', 'available'), '')
            response += f"{i}. {fac['name']} {icon}\n"
        
        response += "\n0. Menu kuu\n"
        response += "Chagua nambari:"
        
        return response
    
    def handle_facility_selection(self, selection):
        """Handle facility selection"""
        try:
            if selection == "0":
                return self.main_menu()
            
            idx = int(selection) - 1
            results = self.session.get('search_results', [])
            
            if 0 <= idx < len(results):
                facility = results[idx]
                
                # Send SMS with details automatically (lazy-loaded)
                self.send_facility_sms(facility)
                
                return self.format_facility_details(facility)
            else:
                return "END Nambari sio sahihi."
        except ValueError:
            return "END Tafadhali ingiza nambari sahihi."
    
    def send_facility_sms(self, facility):
        """Send SMS with facility details to the user - uses lazy-loaded SMS service"""
        phone = self.session.get('phone_number')
        if not phone:
            return
            
        services_str = ", ".join(facility['services']) if facility['services'] else "N/A"
        status_str = facility.get('status', 'available').replace('_', ' ').title()
        
        message = (
            f"HudumaAfya: Maelezo ya {facility['name']}\n"
            f"Kaunti: {facility['county']}\n"
            f"Mji: {facility.get('town', 'N/A')}\n"
            f"Simu: {facility['phone']}\n"
            f"Huduma: {services_str}\n"
            f"Hali ya sasa: {status_str}\n\n"
            "Asante kwa kutumia HudumaAfya Kenya."
        )
        sms = self._get_sms_service()
        sms.send_sms(phone, message)

    def format_facility_details(self, facility):
        """Format facility details for USSD - PURE STRING"""
        services_str = ", ".join(facility['services'][:2]) if facility['services'] else "N/A"
        status_str = facility.get('status', 'available').replace('_', ' ').title()
        
        return f"""END {facility['name']}
Kaunti: {facility['county']}
Mji: {facility.get('town', 'N/A')}
Simu: {facility['phone']}
Huduma: {services_str}
Hali ya sasa: {status_str}

Tumekutumia maelezo haya kwa SMS hivi punde.

Asante!"""
    
    def health_tips_menu(self):
        """Health tips menu - PURE STRING"""
        return """CON Ushauri wa Afya:
1. Afya ya Jumla
2. Afya ya Mama na Mtoto
3. Lishe Bora
4. Uzazi wa Mpango

0. Rudi nyuma
00. Menu kuu

Chagua:"""
    
    def handle_health_tips(self, text_array, last_input):
        """Handle health tips selection"""
        categories = {
            "1": "general",
            "2": "maternal",
            "3": "nutrition",
            "4": "family_planning",
        }
        
        if last_input in categories:
            category = categories[last_input]
            tip = self.get_random_health_tip(category)
            return f"END {tip}\n\nAsante! Kwa ushauri zaidi, piga *384*43149#"
        elif last_input == "0":
            return self.main_menu()
        elif last_input == "00":
            return self.main_menu()
        
        return "END Chaguo sio sahihi."
    
    def get_random_health_tip(self, category):
        """Get a random health tip from database - lazy import"""
        try:
            from content.models import HealthTip
            tip = HealthTip.objects.filter(
                category=category,
                is_active=True,
                language='sw'
            ).order_by('?').first()
            
            if tip:
                return tip.tip
        except:
            pass
        
        # Fallback tips - PURE STRINGS, no database
        fallback_tips = {
            'general': "Kunywa angalau lita 2 za maji kila siku kwa afya njema.",
            'maternal': "Mama mjamzito anahitaji lishe kamili na kupima uzito kila mwezi.",
            'nutrition': "Kula mboga za majani na matunda kwa rangi mbalimbali.",
            'family_planning': "Wasiliana na kliniki ya uzazi karibu nawe kwa ushauri.",
        }
        
        return fallback_tips.get(category, "Tafadhali pitia kliniki karibu nawe kwa ushauri.")
    
    def emergency_numbers(self):
        """Emergency numbers - PURE STRING"""
        return """END 🚨 Nambari za Dharura:
Polisi: 999 / 112 / 911
Zima Moto: 999
Ambulansi: 999 / 0700395395
St. John Ambulance: 0703953953

Usisite kupiga wakati wa dharura!
"""
    
    def about_us(self):
        """About us information - PURE STRING"""
        return """END HudumaAfya Kenya 🇰🇪
Tunasaidia Wakenya kupata huduma za afya karibu nao.

*384*43149# - Bure
Tovuti: Inajengwa

Asante kwa kuwa miongoni mwetu!
"""
    
    def error_message(self):
        """Default error message - PURE STRING"""
        return "END Samahani, hitilafu imetokea. Tafadhali anza tena kwa kupiga *384*43149#"


def create_session(session_id, phone_number):
    """Create a new USSD session - FAST, no external calls"""
    return {
        'session_id': session_id,
        'phone_number': phone_number,
        'menu_level': 'main',
        'data': {},
        'created_at': datetime.now().isoformat(),
        'search_results': [],
    }