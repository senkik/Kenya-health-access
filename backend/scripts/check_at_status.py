import africastalking
from django.conf import settings

africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
app = africastalking.Application

try:
    user = app.fetch_application_data()
    print(f"✅ App Status: {user}")
except Exception as e:
    print(f"❌ Error: {e}")