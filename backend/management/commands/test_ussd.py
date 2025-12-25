from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = 'Test USSD callback flow'
    
    def handle(self, *args, **options):
        base_url = "http://localhost:8000"
        
        test_cases = [
            {"text": "", "description": "Main Menu"},
            {"text": "1", "description": "Search Menu"},
            {"text": "1*1", "description": "Enter County"},
            {"text": "1*1*Nairobi", "description": "Search Results"},
        ]
        
        for test in test_cases:
            self.stdout.write(f"\n🧪 Testing: {test['description']}")
            self.stdout.write(f"Input: {test['text']}")
            
            try:
                response = requests.post(
                    f"{base_url}/ussd/callback/",
                    data={
                        "sessionId": "test_" + test['description'].replace(" ", "_"),
                        "phoneNumber": "254712345678",
                        "serviceCode": "*384#",
                        "text": test['text']
                    },
                    timeout=5
                )
                
                self.stdout.write(f"Response:\n{response.text}")
                
            except requests.exceptions.ConnectionError:
                self.stdout.write(self.style.ERROR("❌ Server not running. Run: python manage.py runserver"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))