import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class NetworkLocationService:
    """
    Interface with mobile operator location APIs
    Supports Safaricom, Airtel, Telkom
    """
    
    OPERATOR_APIS = {
        'safaricom': {
            'url': 'https://api.safaricom.co.ke/location/v1/query',
            'auth_type': 'oauth2',
            'provider_code': '63901'
        },
        'airtel': {
            'url': 'https://openapi.airtel.co.ke/location/v1',
            'auth_type': 'api_key',
            'provider_code': '63902'
        },
        'telkom': {
            'url': 'https://api.telkom.co.ke/lbs/v1/location',
            'auth_type': 'basic',
            'provider_code': '63903'
        }
    }
    
    def __init__(self):
        self.api_keys = {
            'safaricom': getattr(settings, 'SAFARICOM_API_KEY', None),
            'airtel': getattr(settings, 'AIRTEL_API_KEY', None),
            'telkom': getattr(settings, 'TELKOM_API_KEY', None)
        }
    
    def detect_operator(self, phone_number):
        """Detect mobile operator from phone number prefix"""
        prefixes = {
            'safaricom': ['0710', '0711', '0712', '0713', '0714', '0715', '0716', '0717', '0718', '0719', 
                         '0720', '0721', '0722', '0723', '0724', '0725', '0726', '0727', '0728', '0729',
                         '0740', '0741', '0742', '0743', '0745', '0746', '0748', '0757', '0758', '0768',
                         '0790', '0791', '0792', '0793', '0794', '0795', '0796', '0797', '0798', '0799'],
            'airtel': ['0730', '0731', '0732', '0733', '0734', '0735', '0736', '0737', '0738', '0739',
                      '0750', '0751', '0752', '0753', '0754', '0755', '0756', '0759', '0760', '0761',
                      '0762', '0763', '0764', '0765', '0766', '0767', '0769', '0770', '0771', '0772'],
            'telkom': ['0773', '0774', '0775', '0776', '0777', '0778', '0779', '0780', '0781', '0782',
                      '0783', '0784', '0785', '0786', '0787', '0788', '0789']
        }
        
        # Normalize phone number to local format (remove +254, add 0)
        if phone_number.startswith('+254'):
            phone_number = '0' + phone_number[4:]
        
        for operator, prefixes_list in prefixes.items():
            for prefix in prefixes_list:
                if phone_number.startswith(prefix):
                    return operator
        
        return 'unknown'
    
    def get_operator_token(self, operator):
        """Get OAuth token for operator API"""
        cache_key = f"operator_token_{operator}"
        token = cache.get(cache_key)
        
        if token:
            return token
        
        # Request new token (implementation varies by operator)
        if operator == 'safaricom':
            api_key = self.api_keys.get('safaricom')
            api_secret = getattr(settings, 'SAFARICOM_API_SECRET', None)
            if not api_key or not api_secret:
                return None
                
            response = requests.post(
                "https://api.safaricom.co.ke/oauth/v1/generate",
                auth=(api_key, api_secret)
            )
            if response.status_code == 200:
                token = response.json()['access_token']
                cache.set(cache_key, token, 3500)  # 1 hour expiry
                return token
        
        return None
    
    def get_location(self, phone_number):
        """
        Request location from operator API
        Returns: dict with lat, lon, accuracy, source
        """
        operator = self.detect_operator(phone_number)
        
        if operator not in self.OPERATOR_APIS:
            logger.warning(f"Unknown operator for {phone_number}")
            return None
        
        api_config = self.OPERATOR_APIS[operator]
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Add auth header based on type
            if api_config['auth_type'] == 'oauth2':
                token = self.get_operator_token(operator)
                if not token:
                    return None
                headers['Authorization'] = f"Bearer {token}"
            elif api_config['auth_type'] == 'api_key':
                api_key = self.api_keys.get(operator)
                if not api_key:
                    return None
                headers['X-API-Key'] = api_key
            elif api_config['auth_type'] == 'basic':
                api_key = self.api_keys.get(operator)
                operator_secrets = getattr(settings, 'OPERATOR_SECRETS', {})
                api_secret = operator_secrets.get(operator)
                
                if not api_key or not api_secret:
                    return None
                    
                import base64
                auth = base64.b64encode(
                    f"{api_key}:{api_secret}".encode()
                ).decode()
                headers['Authorization'] = f"Basic {auth}"
            
            # Prepare request body
            payload = {
                'msisdn': phone_number,
                'accuracy': 'high',  # or 'medium', 'low'
                'response_format': 'json',
                'provider_code': api_config['provider_code']
            }
            
            # Make API call
            response = requests.post(
                api_config['url'],
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response (format varies by operator)
                location = {
                    'lat': data.get('location', {}).get('latitude') or data.get('lat'),
                    'lon': data.get('location', {}).get('longitude') or data.get('lng'),
                    'accuracy': data.get('accuracy', 'unknown'),
                    'source': operator,
                    'timestamp': data.get('timestamp')
                }
                
                return location
            else:
                logger.error(f"Location API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Location request failed: {e}")
            return None

    def get_location_fallback(self, phone_number):
        """
        Fallback method using Africa's Talking location service
        """
        import africastalking
        at_username = getattr(settings, 'AT_USERNAME', None)
        at_api_key = getattr(settings, 'AT_API_KEY', None)
        
        if not at_username or not at_api_key:
            return None
            
        africastalking.initialize(at_username, at_api_key)
        location = africastalking.Location
        
        try:
            response = location.get_location(phone_number)
            if response['status'] == 'Success':
                return {
                    'lat': response['latitude'],
                    'lon': response['longitude'],
                    'accuracy': response['accuracy'],
                    'source': 'africastalking'
                }
        except Exception as e:
            logger.error(f"AT location failed: {e}")
        
        return None
