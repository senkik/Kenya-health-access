class DemoLocationService:
    """Simulate location for development/demo"""
    
    def get_location(self, phone_number):
        # Return Nairobi coordinates for demo (Central Business District)
        return {
            'lat': -1.286389,
            'lon': 36.817223,
            'accuracy': 'demo',
            'source': 'demo'
        }
    
    def get_location_fallback(self, phone_number):
        return self.get_location(phone_number)
