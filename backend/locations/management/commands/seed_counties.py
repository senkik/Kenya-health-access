from django.core.management.base import BaseCommand
from locations.models import County

class Command(BaseCommand):
    help = 'Seed Kenyan counties data'
    
    def handle(self, *args, **kwargs):
        counties_data = [
            {'name': 'Mombasa', 'code': '001', 'capital': 'Mombasa', 'region': 'Coast'},
            {'name': 'Kwale', 'code': '002', 'capital': 'Kwale', 'region': 'Coast'},
            {'name': 'Kilifi', 'code': '003', 'capital': 'Kilifi', 'region': 'Coast'},
            {'name': 'Tana River', 'code': '004', 'capital': 'Hola', 'region': 'Coast'},
            {'name': 'Lamu', 'code': '005', 'capital': 'Lamu', 'region': 'Coast'},
            {'name': 'Taita–Taveta', 'code': '006', 'capital': 'Voi', 'region': 'Coast'},
            {'name': 'Garissa', 'code': '007', 'capital': 'Garissa', 'region': 'North Eastern'},
            {'name': 'Wajir', 'code': '008', 'capital': 'Wajir', 'region': 'North Eastern'},
            {'name': 'Mandera', 'code': '009', 'capital': 'Mandera', 'region': 'North Eastern'},
            {'name': 'Marsabit', 'code': '010', 'capital': 'Marsabit', 'region': 'Eastern'},
            {'name': 'Isiolo', 'code': '011', 'capital': 'Isiolo', 'region': 'Eastern'},
            {'name': 'Meru', 'code': '012', 'capital': 'Meru', 'region': 'Eastern'},
            {'name': 'Tharaka-Nithi', 'code': '013', 'capital': 'Chuka', 'region': 'Eastern'},
            {'name': 'Embu', 'code': '014', 'capital': 'Embu', 'region': 'Eastern'},
            {'name': 'Kitui', 'code': '015', 'capital': 'Kitui', 'region': 'Eastern'},
            {'name': 'Machakos', 'code': '016', 'capital': 'Machakos', 'region': 'Eastern'},
            {'name': 'Makueni', 'code': '017', 'capital': 'Wote', 'region': 'Eastern'},
            {'name': 'Nyandarua', 'code': '018', 'capital': 'Ol Kalou', 'region': 'Central'},
            {'name': 'Nyeri', 'code': '019', 'capital': 'Nyeri', 'region': 'Central'},
            {'name': 'Kirinyaga', 'code': '020', 'capital': 'Kerugoya / Kutus', 'region': 'Central'},
            {'name': 'Murang\'a', 'code': '021', 'capital': 'Murang\'a', 'region': 'Central'},
            {'name': 'Kiambu', 'code': '022', 'capital': 'Kiambu', 'region': 'Central'},
            {'name': 'Turkana', 'code': '023', 'capital': 'Lodwar', 'region': 'Rift Valley'},
            {'name': 'West Pokot', 'code': '024', 'capital': 'Kapenguria', 'region': 'Rift Valley'},
            {'name': 'Samburu', 'code': '025', 'capital': 'Maralal', 'region': 'Rift Valley'},
            {'name': 'Trans-Nzoia', 'code': '026', 'capital': 'Kitale', 'region': 'Rift Valley'},
            {'name': 'Uasin Gishu', 'code': '027', 'capital': 'Eldoret', 'region': 'Rift Valley'},
            {'name': 'Elgeyo-Marakwet', 'code': '028', 'capital': 'Iten', 'region': 'Rift Valley'},
            {'name': 'Nandi', 'code': '029', 'capital': 'Kapsabet', 'region': 'Rift Valley'},
            {'name': 'Baringo', 'code': '030', 'capital': 'Kabarnet', 'region': 'Rift Valley'},
            {'name': 'Laikipia', 'code': '031', 'capital': 'Rumuruti', 'region': 'Rift Valley'},
            {'name': 'Nakuru', 'code': '032', 'capital': 'Nakuru', 'region': 'Rift Valley'},
            {'name': 'Narok', 'code': '033', 'capital': 'Narok', 'region': 'Rift Valley'},
            {'name': 'Kajiado', 'code': '034', 'capital': 'Kajiado', 'region': 'Rift Valley'},
            {'name': 'Kericho', 'code': '035', 'capital': 'Kericho', 'region': 'Rift Valley'},
            {'name': 'Bomet', 'code': '036', 'capital': 'Bomet', 'region': 'Rift Valley'},
            {'name': 'Kakamega', 'code': '037', 'capital': 'Kakamega', 'region': 'Western'},
            {'name': 'Vihiga', 'code': '038', 'capital': 'Vihiga', 'region': 'Western'},
            {'name': 'Bungoma', 'code': '039', 'capital': 'Bungoma', 'region': 'Western'},
            {'name': 'Busia', 'code': '040', 'capital': 'Busia', 'region': 'Western'},
            {'name': 'Siaya', 'code': '041', 'capital': 'Siaya', 'region': 'Nyanza'},
            {'name': 'Kisumu', 'code': '042', 'capital': 'Kisumu', 'region': 'Nyanza'},
            {'name': 'Homa Bay', 'code': '043', 'capital': 'Homa Bay', 'region': 'Nyanza'},
            {'name': 'Migori', 'code': '044', 'capital': 'Migori', 'region': 'Nyanza'},
            {'name': 'Kisii', 'code': '045', 'capital': 'Kisii', 'region': 'Nyanza'},
            {'name': 'Nyamira', 'code': '046', 'capital': 'Nyamira', 'region': 'Nyanza'},
            {'name': 'Nairobi', 'code': '047', 'capital': 'Nairobi City', 'region': 'Nairobi'},
        ]
        
        count = 0
        for county_data in counties_data:
            county, created = County.objects.get_or_create(
                code=county_data['code'],
                defaults=county_data
            )
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} counties'))