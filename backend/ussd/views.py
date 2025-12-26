import africastalking
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import redis
from datetime import datetime, timedelta
from .handler import USSDHandler, create_session 
from utils.sms_service import send_sms

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
    service_code = request.POST.get("serviceCode", "*384*43149#")
    phone_number = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "")
    
    print(f"USSD Request: session={session_id}, phone={phone_number}, text={text}")
    
    # Get or create session
    session = get_session(session_id, phone_number)

    # Parse USSD text
    text_array = text.split("*") if text else []
    last_input = text_array[-1] if text_array else ""

    # Use USSD Handler for processing
    handler = USSDHandler(session)
    response = handler.process_input(text_array, last_input)
    
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
    
    return create_session(session_id, phone_number)  

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

@csrf_exempt
def sms_callback(request):
    """Handle SMS callbacks from Africa's Talking"""
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)
    
    data = request.POST
    print(f"SMS Callback: {data}")
    
    return HttpResponse(status=200)
