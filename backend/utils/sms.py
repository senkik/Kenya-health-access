"""
SMS Service using Africa's Talking
Handles all SMS sending with retry logic and logging
"""
import africastalking
from django.conf import settings
import logging
import time
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SMSService:
    """Production-ready SMS service with retry logic"""
    
    def __init__(self):
        self.username = settings.AFRICASTALKING_USERNAME
        self.api_key = settings.AFRICASTALKING_API_KEY
        self.sender_id = getattr(settings, 'SMS_SENDER_ID', 'HUDUMA')
        
        # Initialize Africa's Talking
        africastalking.initialize(self.username, self.api_key)
        self.sms = africastalking.SMS
        self._check_balance()
    
    def _check_balance(self):
        """Check SMS balance on startup"""
        try:
            balance = self.sms.fetch_balance()
            logger.info(f"SMS Balance: {balance}")
        except Exception as e:
            logger.warning(f"Could not fetch SMS balance: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def send_sms(self, phone_number: str, message: str, 
                 sender_id: Optional[str] = None) -> Dict:
        """
        Send SMS with retry logic
        
        Args:
            phone_number: Recipient's phone number (format: +2547XXXXXXXX)
            message: SMS content
            sender_id: Optional sender ID/shortcode
        
        Returns:
            Dict with status and message_id
        """
        try:
            # Validate and format phone number
            phone_number = self._format_phone(phone_number)
            
            # Prepare recipients
            recipients = [phone_number]
            
            # Prepare options
            options = {
                'to': recipients,
                'message': message,
                'enqueue': True,
            }
            
            if sender_id:
                options['sender_id'] = sender_id
            elif self.sender_id:
                options['sender_id'] = self.sender_id
            
            # Send SMS
            response = self.sms.send(message, recipients, options)
            
            # Log success
            logger.info(f"SMS sent to {phone_number}: {response}")
            
            return {
                'success': True,
                'message_id': response.get('SMSMessageData', {}).get('Recipients', [{}])[0].get('messageId'),
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_bulk_sms(self, phone_numbers: List[str], message: str,
                      sender_id: Optional[str] = None) -> List[Dict]:
        """
        Send SMS to multiple recipients
        """
        results = []
        for phone in phone_numbers:
            result = self.send_sms(phone, message, sender_id)
            results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        return results
    
    def send_facility_list(self, phone_number: str, facilities: List[Dict]) -> Dict:
        """
        Send formatted list of nearby facilities
        """
        if not facilities:
            message = (
                "🏥 HUDUMA ZA AFYA\n\n"
                "Samahani, hakuna huduma zilizopatikana karibu nawe.\n\n"
                "Jaribu:\n"
                "• Kuongeza eneo la utafutaji\n"
                "• Kutafuta kwa kaunti\n"
                "• Kupiga *384*43149# tena"
            )
            return self.send_sms(phone_number, message)
        
        # Build message with facilities
        message = "🏥 HUDUMA ZA AFYA KARIBU NAWE\n\n"
        
        for i, facility in enumerate(facilities[:3], 1):
            message += f"{i}. {facility['name']}\n"
            message += f"   📍 {facility['distance']}km"
            if facility.get('town'):
                message += f" - {facility['town']}"
            message += f"\n   📞 {facility['phone']}"
            
            if facility.get('emergency'):
                message += " 🚨"
            
            message += "\n\n"
        
        message += (
            "📱 Piga *384*43149# kwa:\n"
            "• Huduma zaidi\n"
            "• Nambari za dharura\n"
            "• Ushauri wa afya"
        )
        
        return self.send_sms(phone_number, message)
    
    def send_emergency_contacts(self, phone_number: str) -> Dict:
        """
        Send emergency contacts via SMS
        """
        message = (
            "🚨 NAMBARI ZA DHARURA KENYA 🚨\n\n"
            "🚓 POLISI: 999 au 112\n"
            "🔥 ZIMA MOTO: 999\n"
            "🚑 AMBULANSI: 999\n\n"
            "ST. JOHN AMBULANCE:\n"
            "📞 0700 395 395\n\n"
            "🇰🇪 Huduma kwa wote - 24/7"
        )
        return self.send_sms(phone_number, message)
    
    def send_health_tip(self, phone_number: str, tip: Dict) -> Dict:
        """
        Send daily health tip
        """
        message = (
            f"💚 USHAURI WA AFYA\n\n"
            f"{tip['content']}\n\n"
            f"Piga *384*43149# kwa ushauri zaidi"
        )
        return self.send_sms(phone_number, message)
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number to international format"""
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Handle different formats
        if cleaned.startswith('254'):
            return f"+{cleaned}"
        elif cleaned.startswith('0'):
            return f"+254{cleaned[1:]}"
        elif len(cleaned) == 9:
            return f"+254{cleaned}"
        else:
            return f"+{cleaned}"