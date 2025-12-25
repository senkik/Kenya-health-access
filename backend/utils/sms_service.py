# sms_service.py
from django.conf import settings

def send_sms(phone, message):
    """Send SMS - uses mock in development, real in production"""
    
    if settings.DEBUG or getattr(settings, 'USE_MOCK_SMS', True):
        # Mock for development
        print(f"📱 [DEV SMS] To: {phone}")
        print(f"📝 Message: {message}")
        print("✅ SMS logged (would send in production)")
        return True
    else:
        # Real Africa's Talking in production
        import africastalking
        africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
        sms = africastalking.SMS
        try:
            response = sms.send(message, [phone])
            return True
        except:
            return False