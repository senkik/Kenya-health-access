import africastalking
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import redis
from datetime import datetime, timedelta

# Initialize Africa's Talking
try:
    africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
    ussd_service = africastalking.USSD
    sms_service = africastalking.SMS
    initialized = True
except Exception as e:
    print(f"Africa's Talking initialization failed: {e}")
    initialized = False
    ussd_service = None
    sms_service = None

# Initialize Redis for session storage (optional but recommended)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_available = True
except:
    redis_available = False
    print("Redis not available, using in-memory session storage")

# In-memory session storage fallback
session_store = {}

@csrf_exempt
def ussd_callback(request):
    """Handle USSD requests from Africa's Talking"""
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)
    
    session_id = request.POST.get("sessionId", "")
    service_code = request.POST.get("serviceCode", "*384#")
    phone_number = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "")
    
    print(f"USSD Request: session={session_id}, phone={phone_number}, text={text}")
    
    # Parse USSD text
    text_array = text.split("*") if text else []
    last_input = text_array[-1] if text_array else ""
    
    # Get or create session
    session = get_session(session_id, phone_number)
    
    # Handle USSD flow
    response = handle_ussd_flow(session, text_array, last_input)
    
    # Update session
    update_session(session_id, session)
    
    return HttpResponse(response, content_type='text/plain')

def get_session(session_id, phone_number):
    """Get or create USSD session"""
    if redis_available:
        try:
            session_data = redis_client.get(f"ussd:{session_id}")
            if session_data:
                return json.loads(session_data)
        except:
            pass
    
    # Check in-memory store
    if session_id in session_store:
        return session_store[session_id]
    
    # Create new session
    session = {
        'session_id': session_id,
        'phone_number': phone_number,
        'menu_level': 'main',
        'data': {},
        'created_at': datetime.now().isoformat(),
        'search_results': [],
        'selected_county': '',
    }
    
    return session

def update_session(session_id, session):
    """Update session storage"""
    session['updated_at'] = datetime.now().isoformat()
    
    # Store in Redis with 5-minute expiry
    if redis_available:
        try:
            redis_client.setex(
                f"ussd:{session_id}",
                timedelta(minutes=5),
                json.dumps(session)
            )
        except:
            session_store[session_id] = session
    else:
        session_store[session_id] = session

def handle_ussd_flow(session, text_array, last_input):
    """Main USSD flow handler"""
    
    # LEVEL 0: Main Menu
    if last_input == "":
        session['menu_level'] = 'main'
        return main_menu()
    
    # LEVEL 1: Main Menu Selection
    if len(text_array) == 1:
        if last_input == "1":
            session['menu_level'] = 'search'
            return search_menu()
        elif last_input == "2":
            session['menu_level'] = 'health_tips'
            return health_tips_menu()
        elif last_input == "3":
            session['menu_level'] = 'emergency'
            return emergency_numbers()
        elif last_input == "4":
            session['menu_level'] = 'about'
            return about_us()
        else:
            return "END Chaguo sio sahihi. Tafadhali jaribu tena."
    
    # LEVEL 2+: Handle based on current menu level
    menu_level = session.get('menu_level', 'main')
    
    if menu_level == 'search':
        return handle_search_flow(session, text_array, last_input)
    elif menu_level == 'health_tips':
        return handle_health_tips_flow(text_array, last_input)
    
    return "END Samahani, hitilafu imetokea. Tafadhali anza tena."

def main_menu():
    """Main USSD Menu in Swahili"""
    return """CON Karibu HudumaAfya Kenya 🇰🇪
1. Tafuta Hospitali/Kliniki
2. Ushauri wa Afya
3. Nambari za Dharura
4. Kuhusu Sisi

Chagua nambari:"""

def search_menu():
    """Search facility menu"""
    return """CON Tafuta kwa:
1. Jina la Kaunti
2. Jina la Hospitali
3. Hudua Unayotaka
4. Karibu na Mimi

Chagua nambari:"""

def handle_search_flow(session, text_array, last_input):
    """Handle search flow"""
    
    # Level 2 of search: Choose search type
    if len(text_array) == 2:
        if last_input == "1":
            session['search_type'] = 'county'
            return "CON Andika jina la kaunti yako:"
        elif last_input == "2":
            session['search_type'] = 'facility_name'
            return "CON Andika jina la hospitali:"
        elif last_input == "3":
            session['search_type'] = 'service'
            return "CON Andika hudua unayotaka (mfano: ugonjwa wa moyo):"
        elif last_input == "4":
            session['search_type'] = 'nearby'
            return "END Samahani, utafutaji wa GPS utapatikana hivi karibuni. Tumia chaguo nyingine."
        else:
            return "END Chaguo sio sahihi."
    
    # Level 3: Process search query
    elif len(text_array) == 3:
        search_type = session.get('search_type', 'county')
        search_query = last_input
        
        # Store search query
        session['last_search'] = {
            'type': search_type,
            'query': search_query,
            'timestamp': datetime.now().isoformat()
        }
        
        # Mock search results (you'll replace with real DB query)
        if search_type == 'county':
            session['search_results'] = [
                {"id": 1, "name": "Kenyatta Hospital", "phone": "020-2726300", "distance": "2km"},
                {"id": 2, "name": "Mbagathi Hospital", "phone": "020-2726300", "distance": "5km"},
                {"id": 3, "name": "Aga Khan Hospital", "phone": "020-3662000", "distance": "3km"},
            ]
        else:
            session['search_results'] = [
                {"id": 1, "name": f"Hospitali ya {search_query}", "phone": "020-XXXXXXX", "distance": "N/A"},
            ]
        
        return format_search_results(session['search_results'])
    
    # Level 4: Facility selection
    elif len(text_array) == 4:
        try:
            selection = int(last_input)
            results = session.get('search_results', [])
            
            if 1 <= selection <= len(results):
                facility = results[selection - 1]
                return format_facility_details(facility)
            elif last_input == "0":
                return search_menu()
            elif last_input == "00":
                return main_menu()
            else:
                return "END Nambari sio sahihi. Anza tena."
        except ValueError:
            return "END Tafadhali ingiza nambari sahihi."
    
    return "END Samahani, hitilafu imetokea."

def format_search_results(facilities):
    """Format search results for USSD"""
    if not facilities:
        return "END Hakuna matokeo. Jaribu utafutaji mwingine."
    
    response = "CON Matokeo:\n"
    for i, fac in enumerate(facilities, 1):
        response += f"{i}. {fac['name']}\n"
    
    response += "\n0. Rudi nyuma\n"
    response += "00. Menu kuu\n"
    response += "Chagua nambari:"
    
    return response

def format_facility_details(facility):
    """Format facility details for USSD"""
    return f"""END {facility['name']}
📞: {facility['phone']}
📍: {facility.get('distance', 'N/A')}

Kwa maelezo zaidi, tembelea tovuti yetu.

Asante kwa kutumia HudumaAfya!"""

def health_tips_menu():
    """Health tips menu"""
    return """CON Ushauri wa Afya:
1. Kunywa maji mengi kila siku
2. Lala saa 8 usiku
3. Kula mboga na matunda
4. Fanya mazoezi kila siku

0. Rudi nyuma
00. Menu kuu

Chagua:"""

def handle_health_tips_flow(text_array, last_input):
    """Handle health tips flow"""
    if len(text_array) == 2:
        tips = {
            "1": "Kunywa angalau lita 2 za maji kila siku kwa afya njema.",
            "2": "Usingizi wa saa 8 husaidia mwili kupumzika na kujipanga upya.",
            "3": "Mboga na matunda hutoa vitamini na madini muhimu kwa mwili.",
            "4": "Mazoezi ya angalau dakika 30 kila siku yanachangia afya ya moyo.",
        }
        
        if last_input in tips:
            return f"END {tips[last_input]}\n\nAsante! Kwa ushauri zaidi, piga *384#"
        elif last_input == "0":
            return main_menu()
        elif last_input == "00":
            return main_menu()
    
    return "END Chaguo sio sahihi."

def emergency_numbers():
    """Emergency numbers"""
    return """END 🚨 Nambari za Dharura:
Polisi: 999 / 112 / 911
Zima Moto: 999
Ambulansi: 999 / 0700395395
St. John Ambulance: 0703953953

Usisite kupiga wakati wa dharura!

0. Rudi nyuma
00. Menu kuu"""

def about_us():
    """About us information"""
    return """END HudumaAfya Kenya 🇰🇪
Tunasaidia Wakenya kupata huduma za afya karibu nao.

Tovuti: Inajengwa
Simu: *384#
Msaada: hudumaafya@gmail.com

Asante kwa kuwa miongoni mwetu!
"""

# SMS Functionality
@csrf_exempt
def sms_callback(request):
    """Handle SMS callbacks from Africa's Talking"""
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)
    
    data = request.POST
    print(f"SMS Callback: {data}")
    
    # This is where Africa's Talking sends delivery reports
    # You can log SMS delivery status here
    
    return HttpResponse(status=200)

def send_sms(phone_number, message):
    """Send SMS via Africa's Talking"""
    if not initialized or not sms_service:
        print(f"[SMS NOT SENT - API not initialized] To: {phone_number}, Message: {message}")
        return False
    
    try:
        response = sms_service.send(message, [phone_number])
        print(f"SMS sent to {phone_number}: {response}")
        return True
    except Exception as e:
        print(f"Failed to send SMS to {phone_number}: {e}")
        return False