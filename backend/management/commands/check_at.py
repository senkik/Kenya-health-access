from django.core.management.base import BaseCommand
import africastalking
from django.conf import settings

class Command(BaseCommand):
    help = 'Check Africa\'s Talking API status'
    
    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking Africa's Talking Status...")
        
        self.stdout.write(f"Username: {settings.AT_USERNAME}")
        self.stdout.write(f"API Key: {'*' * len(settings.AT_API_KEY) if settings.AT_API_KEY else 'NOT SET'}")
        
        if not settings.AT_API_KEY:
            self.stdout.write(self.style.ERROR("❌ API Key not set in .env file"))
            return
        
        try:
            africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
            app = africastalking.Application
            
            # Fetch application data
            user_data = app.fetch_application_data()
            
            self.stdout.write(self.style.SUCCESS("✅ Africa's Talking is working!"))
            self.stdout.write(f"User Data: {user_data}")
            
            # Check balance
            try:
                balance = app.fetch_user_data()
                self.stdout.write(f"Account Balance: {balance}")
            except:
                self.stdout.write("Note: Could not fetch balance (sandbox limitation)")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Africa's Talking error: {e}"))