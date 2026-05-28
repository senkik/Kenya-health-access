from django.core.management.base import BaseCommand
from facilities.models import FacilityType, Service, Facility
from locations.models import County

class Command(BaseCommand):
    help = 'Seed initial data for the health platform'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding initial data...')
        
        counties = [
                     {'name': 'Nairobi', 'code': '047', 'capital': 'Nairobi City'},
            {'name': 'Mombasa', 'code': '001', 'capital': 'Mombasa'},
            {'name': 'Kisumu', 'code': '042', 'capital': 'Kisumu'},
            {'name': 'Uasin Gishu', 'code': '027', 'capital': 'Eldoret'},
            {'name': 'Nakuru', 'code': '032', 'capital': 'Nakuru'},
            {'name': 'Kiambu', 'code': '022', 'capital': 'Kiambu'},
            {'name': 'Machakos', 'code': '016', 'capital': 'Machakos'},
            {'name': 'Meru', 'code': '012', 'capital': 'Meru'},
        ]           
        
        county_objects ={}
        for county_data in counties:
            county, created = County.objects.get_or_create(**county_data)
            if created:
                self.stdout.write(f'Created County: {county.name}')
        
        # Create Facility Types
        facility_types = [
            {'name': 'National Referral Hospital', 'icon': '🏥'},
            {'name': 'County Hospital', 'icon': '🏥'},
            {'name': 'Health Centre', 'icon': '🏥'},
            {'name': 'Dispensary', 'icon': '🏥'},
            {'name': 'Medical Clinic', 'icon': '🏥'},
            {'name': 'Pharmacy', 'icon': '💊'},
            {'name': 'Laboratory', 'icon': '🔬'},
        ]
        
        for ft_data in facility_types:
            ft, created = FacilityType.objects.get_or_create(**ft_data)
            if created:
                self.stdout.write(f'Created Facility Type: {ft.name}')
        
        # Create Services
        services = [
            {'name': 'General Consultation', 'category': 'general'},
            {'name': 'Maternal Care', 'category': 'maternal'},
            {'name': 'Child Immunization', 'category': 'maternal'},
            {'name': 'Emergency Services', 'category': 'emergency'},
            {'name': 'Laboratory Tests', 'category': 'diagnostic'},
            {'name': 'Pharmacy', 'category': 'pharmacy'},
            {'name': 'X-Ray Services', 'category': 'diagnostic'},
            {'name': 'Dental Services', 'category': 'specialist'},
            {'name': 'Eye Care', 'category': 'specialist'},
        ]
        
        for service_data in services:
            service, created = Service.objects.get_or_create(**service_data)
            if created:
                self.stdout.write(f'Created Service: {service.name}')
        
        # Create Sample Facilities
        sample_facilities = [
            {
                'name': 'Kenyatta National Hospital',
                'county': 'Nairobi',
                'town': 'Nairobi',
                'phone': '020-2726300',
                'emergency_available': True,
                'ambulance_available': True,
                'accepts_sha': True,
                'is_verified': True,
            },
            {
                'name': 'Moi Teaching and Referral Hospital',
                'county': 'Uasin Gishu',
                'town': 'Eldoret',
                'phone': '053-2033471',
                'emergency_available': True,
                'ambulance_available': True,
                'accepts_sha': True,
                'is_verified': True,
            },
            {
                'name': 'Coast General Hospital',
                'county': 'Mombasa',
                'town': 'Mombasa',
                'phone': '041-2314201',
                'emergency_available': True,
                'accepts_sha': True,
                'is_verified': True,
            },
        ]
        
        facility_type = FacilityType.objects.get(name='National Referral Hospital')
        general_service = Service.objects.get(name='General Consultation')
        lab_service = Service.objects.get(name='Laboratory Tests')  
        pharmacy_service = Service.objects.get(name='Pharmacy')
        
        for fac_data in sample_facilities:
            county = County.objects.get(name=fac_data['county'])    
            if not county:
                county = County.objects.create(fac_data['county_name'])
                if not county:
                    self.stdout.write(f"Warning: County {fac_data['county_name']} not found in database")       
                    
                    continue    
            
            facility, created = Facility.objects.get_or_create(
                name=fac_data['name'],
                defaults={
                    'facility_type': facility_type,
                    'county': fac_data['county'],
                    'town': fac_data['town'],
                    'phone': fac_data['phone'],
                    'latitude': fac_data['latitude', None],
                    'longitude': fac_data['longitude', None], 
                    'emergency_available': fac_data['emergency_available'],
                    'ambulance_available': fac_data.get('ambulance_available', False),
                    'accepts_sha': fac_data['accepts_sha'],
                    'is_verified': fac_data['is_verified'],
                }
            )
            if created:
                facility.services.add(general_service)
                facility.services.add(emergency_services)
                facility.services.add(lab_service)
                facility.services.add(pharmacy_service) 
                self.stdout.write(f'Created Facility: {facility.name}')
        
        self.stdout.write(self.style.SUCCESS('✓ Seed data created successfully!'))