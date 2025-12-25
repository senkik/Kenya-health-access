"""
USSD Handler for Kenya Health Access
Contains all USSD flow logic separated from views
"""
import json
from datetime import datetime
from django.db.models import Q
from facilities.models import Facility, County, Service
from content.models import HealthTip
from utils.sms_service import send_sms


class USSDHandler:
    """Handles USSD session flows"""
    
    def __init__(self, session):
        self.session = session
    
    def process_input(self, text_array, last_input):
        """Main USSD flow processor"""
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
        """Main USSD Menu in Swahili"""
        self.session['menu_level'] = 'main'
        return """CON Karibu HudumaAfya Kenya
1. Tafuta Hospitali/Kliniki
2. Ushauri wa Afya
3. Nambari za Dharura
4. Kuhusu Sisi

Chagua nambari:"""
    
    def handle_main_menu(self, text_array, last_input):
        """Handle main menu selections"""
        if last_input == "1":
            self.session['menu_level'] = 'search'
            return self.search_menu()
        elif last_input == "2":
            self.session['menu_level'] = 'health_tips'
            return self.health_tips_menu()
        elif last_input == "3":
            return self.emergency_numbers()
        elif last_input == "4":
            return self.about_us()
        else:
            return "END Chaguo sio sahihi. Tafadhali jaribu tena."
    
    def search_menu(self):
        """Search facility menu"""
        return """CON Tafuta kwa:
1. Jina la Kaunti
2. Jina la Hospitali
3. Huduma Unayotaka
4. Jina la Mji/Eneo

Chagua nambari:"""
    
    def handle_search_flow(self, text_array, last_input):
        """Handle search flow with real database queries"""
        
        # Level 1: Choose search type
        if len(text_array) == 2:
            if last_input == "1":
                self.session['search_type'] = 'county'
                return "CON Andika jina la kaunti yako:"
            elif last_input == "2":
                self.session['search_type'] = 'facility_name'
                return "CON Andika jina la hospitali:"
            elif last_input == "3":
                self.session['search_type'] = 'service'
                return "CON Andika huduma unayotaka:"
            elif last_input == "4":
                self.session['search_type'] = 'town'
                return "CON Andika jina la mji au eneo lako:"
            else:
                return "END Chaguo sio sahihi."
        
        # Level 2: Process search query
        elif len(text_array) == 3:
            search_type = self.session.get('search_type')
            search_query = last_input
            
            # Store for later use
            self.session['last_search'] = {
                'type': search_type,
                'query': search_query,
                'timestamp': datetime.now().isoformat()
            }
            
            # Perform actual database search
            facilities = self.search_facilities(search_type, search_query)
            self.session['search_results'] = [
                {
                    'id': fac.id,
                    'name': fac.name,
                    'phone': fac.phone or 'N/A',
                    'county': fac.county.name,
                    'town': fac.town or '',
                    'status': fac.availability_status,
                    'services': [s.name for s in fac.services.all()[:2]]
                }
                for fac in facilities[:5]  # Limit to 5 for USSD
            ]
            
            return self.format_search_results()
        
        # Level 3: Facility selection
        elif len(text_array) == 4:
            return self.handle_facility_selection(last_input)
        
        return self.error_message()
    
    def search_facilities(self, search_type, query):
        """Search facilities in database"""
        facilities = Facility.objects.filter(
            is_verified=True,
            is_active=True
        )
        
        query = query.strip()
        
        if search_type == 'county':
            facilities = facilities.filter(county__name__icontains=query)
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
        """Format search results for USSD"""
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
            icon = status_icons.get(fac['status'], '')
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
                
                # Send SMS with details automatically
                self.send_facility_sms(facility)
                
                return self.format_facility_details(facility)
            else:
                return "END Nambari sio sahihi."
        except ValueError:
            return "END Tafadhali ingiza nambari sahihi."
    
    def send_facility_sms(self, facility):
        """Send SMS with facility details to the user"""
        phone = self.session.get('phone_number')
        if not phone:
            return
            
        services_str = ", ".join(facility['services']) if facility['services'] else "N/A"
        status_str = facility['status'].replace('_', ' ').title()
        
        message = (
            f"HudumaAfya: Maelezo ya {facility['name']}\n"
            f"📍 Kaunti: {facility['county']}\n"
            f"🏥 Mji: {facility.get('town', 'N/A')}\n"
            f"📞 Simu: {facility['phone']}\n"
            f"🩺 Huduma: {services_str}\n"
            f"⚡ Hali ya sasa: {status_str}\n\n"
            "Asante kwa kutumia HudumaAfya Kenya."
        )
        send_sms(phone, message)

    def format_facility_details(self, facility):
        """Format facility details for USSD"""
        services_str = ", ".join(facility['services'][:2]) if facility['services'] else "N/A"
        status_str = facility['status'].replace('_', ' ').title()
        
        return f"""END {facility['name']}
📍 {facility['county']}
📞 {facility['phone']}
🩺 {services_str}
⚡ Hali: {status_str}

Tumekutumia maelezo haya kwa SMS hivi punde.

Asante!"""
    
    def health_tips_menu(self):
        """Health tips menu"""
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
        if len(text_array) == 1:
            categories = {
                "1": "general",
                "2": "maternal",
                "3": "nutrition",
                "4": "family_planning",
            }
            
            if last_input in categories:
                category = categories[last_input]
                tip = self.get_random_health_tip(category)
                return f"END {tip}\n\nAsante! Kwa ushauri zaidi, piga *384#"
            elif last_input == "0":
                self.session['menu_level'] = 'main'
                return self.main_menu()
            elif last_input == "00":
                self.session['menu_level'] = 'main'
                return self.main_menu()
        
        return "END Chaguo sio sahihi."
    
    def get_random_health_tip(self, category):
        """Get a random health tip from database"""
        try:
            tip = HealthTip.objects.filter(
                category=category,
                is_active=True,
                language='sw'  # Swahili tips for USSD
            ).order_by('?').first()
            
            if tip:
                return tip.tip
        except:
            pass
        
        # Fallback tips
        fallback_tips = {
            'general': "Kunywa angalau lita 2 za maji kila siku kwa afya njema.",
            'maternal': "Mama mjamzito anahitaji lishe kamili na kupima uzito kila mwezi.",
            'nutrition': "Kula mboga za majani na matunda kwa rangi mbalimbali.",
        }
        
        return fallback_tips.get(category, "Tafadhali pitia kliniki karibu nawe kwa ushauri.")
    
    def emergency_numbers(self):
        """Emergency numbers"""
        return """END 🚨 Nambari za Dharura:
Polisi: 999 / 112 / 911
Zima Moto: 999
Ambulansi: 999 / 0700395395
St. John Ambulance: 0703953953

Usisite kupiga wakati wa dharura!
"""
    
    def about_us(self):
        """About us information"""
        return """END HudumaAfya Kenya 🇰🇪
Tunasaidia Wakenya kupata huduma za afya karibu nao.

*384# - Bure
Tovuti: Inajengwa

Asante kwa kuwa miongoni mwetu!
"""
    
    def error_message(self):
        """Default error message"""
        return "END Samahani, hitilafu imetokea. Tafadhali anza tena kwa kupiga *384#"


def create_session(session_id, phone_number):
    """Create a new USSD session"""
    return {
        'session_id': session_id,
        'phone_number': phone_number,
        'menu_level': 'main',
        'data': {},
        'created_at': datetime.now().isoformat(),
        'search_results': [],
    }