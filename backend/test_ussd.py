import os
import django
import africastalking

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

print("=== Testing Africa's Talking Integration ===")

# Test initialization

try:
    africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
    print("✅ Africa's Talking initialized successfully")
    
    # Test SMS service

    sms = africastalking.SMS
    print("✅ SMS service available")
    
    # Test USSD service

    ussd = africastalking.USSD
    print("✅ USSD service available")
    
    print(f"\nCredentials:")
    print(f"Username: {settings.AT_USERNAME}")
    print(f"API Key: {'*' * len(settings.AT_API_KEY) if settings.AT_API_KEY else 'NOT SET'}")
    
except Exception as e:
    print(f"❌ Africa's Talking initialization failed: {e}")
    print("\nPlease check:")
    print("1. Is africastalking package installed? (pip install africastalking)")
    print("2. Are AT_USERNAME and AT_API_KEY set in .env file?")
    print("3. Is your API key valid?")