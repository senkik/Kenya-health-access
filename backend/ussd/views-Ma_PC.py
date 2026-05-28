"""
USSD Views for Africa's Talking - OPTIMIZED FOR RENDER FREE TIER
Lazy loading prevents timeout issues on cold starts
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from datetime import datetime, timedelta

# Don't import heavy modules at top level - they'll load lazily
# import africastalking  # REMOVED - will load only when needed
# import redis  # REMOVED - will load only when needed

# Lazy-loaded module holders
_redis_client = None
_redis_available = None
_session_store = {}

def _get_redis_client():
    """Lazy load Redis client - only when needed"""
    global _redis_client, _redis_available
    if _redis_available is None:
        try:
            import redis
            _redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            _redis_client.ping()
            _redis_available = True
            print("Redis connected successfully")
        except Exception as e:
            _redis_available = False
            print(f"Redis not available: {e}")
    return _redis_client if _redis_available else None


@csrf_exempt
@require_POST
def ussd_callback(request):
    """
    Handle USSD requests from Africa's Talking
    OPTIMIZED: Minimal processing on first request
    """
    # Extract parameters - FAST (no external calls)
    session_id = request.POST.get("sessionId", "")
    service_code = request.POST.get("serviceCode", "*384*43149#")
    phone_number = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "").strip()
    
    # Log request (use print for Render logs)
    print(f"USSD: {phone_number} -> '{text}'")
    
    # FAST PATH: Main menu requires no session or heavy processing
    if text == "":
        from .handler import USSDHandler, create_session
        # Create minimal session
        session = create_session(session_id, phone_number)
        handler = USSDHandler(session)
        response = handler.process_input([], "")
        # Store session asynchronously (don't block response)
        _store_session_async(session_id, session)
        return HttpResponse(response, content_type='text/plain')
    
    # For subsequent requests, get session and process
    session = _get_session(session_id, phone_number)
    
    # Parse USSD text
    text_array = text.split("*") if text else []
    last_input = text_array[-1] if text_array else ""
    
    # Import handler lazily (only when needed)
    from .handler import USSDHandler
    handler = USSDHandler(session)
    response = handler.process_input(text_array, last_input)
    
    # Update session
    _update_session(session_id, session)
    
    return HttpResponse(response, content_type='text/plain')


def _get_session(session_id, phone_number):
    """Get or create USSD session - with lazy loading"""
    # Check memory store first (fastest)
    if session_id in _session_store:
        return _session_store[session_id]
    
    # Check Redis if available (slower, but persistent)
    redis_client = _get_redis_client()
    if redis_client:
        try:
            session_data = redis_client.get(f"ussd:{session_id}")
            if session_data:
                session = json.loads(session_data)
                _session_store[session_id] = session
                return session
        except Exception as e:
            print(f"Redis get error: {e}")
    
    # Create new session
    from .handler import create_session
    return create_session(session_id, phone_number)


def _update_session(session_id, session):
    """Update session storage - async-friendly"""
    session['updated_at'] = datetime.now().isoformat()
    
    # Always update memory store
    _session_store[session_id] = session
    
    # Update Redis if available (don't block on failure)
    redis_client = _get_redis_client()
    if redis_client:
        try:
            redis_client.setex(
                f"ussd:{session_id}",
                int(timedelta(minutes=5).total_seconds()),
                json.dumps(session)
            )
        except Exception as e:
            print(f"Redis set error: {e}")


def _store_session_async(session_id, session):
    """Store session without blocking response"""
    session['updated_at'] = datetime.now().isoformat()
    _session_store[session_id] = session
    
    # Try Redis but don't wait
    redis_client = _get_redis_client()
    if redis_client:
        try:
            redis_client.setex(
                f"ussd:{session_id}",
                int(timedelta(minutes=5).total_seconds()),
                json.dumps(session)
            )
        except:
            pass  # Silent fail - memory store is fine


@csrf_exempt
@require_POST
def sms_callback(request):
    """Handle SMS callbacks from Africa's Talking"""
    data = request.POST
    print(f"SMS Callback: {data}")
    
    # Import SMS service lazily if needed
    if 'text' in data:
        from utils.sms import SMSService
        sms = SMSService()
        # Process SMS callback (delivery reports, etc.)
    
    return HttpResponse(status=200)


def health_check(request):
    """Simple health check endpoint - returns fast response"""
    return HttpResponse("OK", content_type='text/plain')
