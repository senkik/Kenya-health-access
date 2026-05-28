import africastalking
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    """SMS service that initializes lazily only when needed"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.username = getattr(settings, 'AFRICASTALKING_USERNAME', '')
        self.api_key = getattr(settings, 'AFRICASTALKING_API_KEY', '')
        self.sender_id = getattr(settings, 'SMS_SENDER_ID', None)
        self._client = None
    
    def _get_client(self):
        """Initialize the Africa's Talking client only when first needed"""
        if self._client is None:
            if not self.username or not self.api_key:
                logger.warning("Africa's Talking credentials not set. SMS sending disabled.")
                return None
            try:
                africastalking.initialize(self.username, self.api_key)
                self._client = africastalking.SMS
                logger.info("Africa's Talking SMS service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Africa's Talking: {e}")
                self._client = False
        return self._client if self._client is not False else None
    
    def send_sms(self, phone_number, message, sender_id=None):
        """Send SMS - initializes client only when this method is called"""
        client = self._get_client()
        if not client:
            logger.warning(f"SMS not sent: client not available for {phone_number}")
            return {'success': False, 'error': 'SMS service not configured'}
        
        try:
            formatted_phone = self._format_phone(phone_number)
            sender = sender_id or self.sender_id
            options = {'enqueue': True}
            if sender:
                options['sender_id'] = sender
            
            response = client.send(message, [formatted_phone], options)
            return {'success': True, 'response': response}
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_phone(self, phone):
        """Format Kenyan phone number to international format"""
        cleaned = ''.join(filter(str.isdigit, phone))
        if cleaned.startswith('254'):
            return f"+{cleaned}"
        elif cleaned.startswith('0'):
            return f"+254{cleaned[1:]}"
        elif len(cleaned) == 9:
            return f"+254{cleaned}"
        return phone

# Create a singleton instance
sms_service = SMSService()