from django.core.management.base import BaseCommand
import africastalking
from django.conf import settings

class Command(BaseCommand):
    help = 'Test Africa\'s Talking SMS functionality'
    
    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Phone number to send SMS to')
        parser.add_argument('message', type=str, help='Message to send')
    
    def handle(self, *args, **options):
        phone = options['phone']
        message = options['message']
        
        # Initialize Africa's Talking
        africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
        sms = africastalking.SMS
        
        try:
            self.stdout.write(f"Sending SMS to {phone}...")
            response = sms.send(message, [phone])
            self.stdout.write(self.style.SUCCESS(f"✅ SMS sent successfully!"))
            self.stdout.write(f"Response: {response}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send SMS: {e}"))
            self.stdout.write("\nTroubleshooting tips:")
            self.stdout.write("1. Check if africastalking is installed: pip install africastalking")
            self.stdout.write("2. Check .env file has AT_USERNAME and AT_API_KEY")
            self.stdout.write("3. Check your Africa's Talking dashboard for sandbox status")
            self.stdout.write("4. Verify your API key is valid")