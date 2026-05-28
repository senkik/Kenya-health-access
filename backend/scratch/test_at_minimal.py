import africastalking
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('AT_USERNAME', 'sandbox')
api_key = os.getenv('AT_API_KEY')

print(f"Testing AT with Username: {username}")
print(f"API Key: {api_key[:10]}...")

try:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
    # We can't really "test" without sending unless we fetch app data
    app = africastalking.Application
    data = app.fetch_application_data()
    print("Success!")
    print(data)
except Exception as e:
    print(f"Error: {e}")
