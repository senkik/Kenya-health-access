"""
Sync facilities from Kenya Master Health Facility Registry (KMHFR) API
Usage: 
    python manage.py sync_mfl              # Incremental sync (last 7 days)
    python manage.py sync_mfl --full-sync  # Full sync of all facilities
    python manage.py sync_mfl --dry-run    # Preview changes without saving
"""
import requests
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from tenacity import retry, stop_after_attempt, wait_exponential
from facilities.models import Facility, FacilityType
from locations.models import County
from mfl_sync.models import MFLSyncLog

import os
from django.conf import settings

logger = logging.getLogger(__name__)

MFL_API_BASE = getattr(settings, 'MFL_API_BASE_URL', None) or os.getenv('MFL_API_BASE_URL', 'https://api.kmhfr.health.go.ke/api')
MFL_API_TOKEN = os.getenv('MFL_API_TOKEN', '')
MFL_PAGE_SIZE = 100

class Command(BaseCommand):
    help = 'Sync facilities from Kenya Master Health Facility Registry'
    
    def add_arguments(self, parser):
        parser.add_argument('--full-sync', action='store_true', help='Perform full sync of all facilities')
        parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving to database')
    
    def handle(self, *args, **options):
        self.is_dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        
        self.stdout.write("[SYNC] Starting MFL facility sync...")
        if self.is_dry_run:
            self.stdout.write(self.style.WARNING("[!] DRY RUN MODE - No changes will be saved"))
        
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'total_fetched': 0
        }
        
        # Create sync log
        if not self.is_dry_run:
            self.sync_log = MFLSyncLog.objects.create(status='running')
        else:
            self.sync_log = None
        
        try:
            # Ensure facility types exist
            self.ensure_facility_types()
            
            if options['full_sync']:
                stats = self.full_sync(stats)
            else:
                stats = self.incremental_sync(stats)
            
            if self.sync_log:
                self.sync_log.status = 'success'
                self.sync_log.completed_at = timezone.now()
                self.sync_log.facilities_created = stats['created']
                self.sync_log.facilities_updated = stats['updated']
                self.sync_log.facilities_skipped = stats['skipped']
                self.sync_log.errors = stats['errors']
                self.sync_log.save()
            
        except Exception as e:
            if self.sync_log:
                self.sync_log.status = 'failed'
                self.sync_log.error_message = str(e)
                self.sync_log.completed_at = timezone.now()
                self.sync_log.save()
            self.stdout.write(self.style.ERROR(f"[ERROR] Sync failed with exception: {e}"))
            
        self.print_summary(stats)
    
    def ensure_facility_types(self):
        """Ensure common facility types exist in database"""
        common_types = [
            'National Referral Hospital', 'County Hospital', 'Sub-County Hospital',
            'Health Centre', 'Dispensary', 'Medical Clinic', 'Nursing Home',
            'Pharmacy', 'Medical Laboratory', 'Maternity Home'
        ]
        for type_name in common_types:
            FacilityType.objects.get_or_create(name=type_name, defaults={'icon': 'H'})
        self.stdout.write(self.style.SUCCESS(f"[OK] Ensured {len(common_types)} facility types exist"))
    
    def incremental_sync(self, stats):
        """Sync facilities updated in the last 7 days"""
        sync_date = (timezone.now() - timedelta(days=7)).isoformat()
        self.stdout.write(f"[DATE] Incremental sync for facilities updated after {sync_date}")
        return self.sync_facilities({'updated_after': sync_date}, stats)
    
    def full_sync(self, stats):
        """Sync ALL published facilities"""
        self.stdout.write("[FULL] Full sync of ALL published facilities")
        return self.sync_facilities({}, stats)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def sync_facilities(self, params, stats):
        """Fetch and sync facilities from MFL API with retry logic"""
        url = f"{MFL_API_BASE}/facilities/facilities/"
        params.update({
            'is_published': 'true',
            'is_classified': 'false',
            'page_size': MFL_PAGE_SIZE
        })
        
        page = 1
        while url:
            self.stdout.write(f"[FETCH] Fetching page {page}...")
            
            try:
                headers = {}
                if MFL_API_TOKEN:
                    headers['Authorization'] = f'Bearer {MFL_API_TOKEN}'
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('results', [])
                stats['total_fetched'] += len(results)
                
                for facility_data in results:
                    result = self.process_facility(facility_data)
                    if result == 'created':
                        stats['created'] += 1
                    elif result == 'updated':
                        stats['updated'] += 1
                    elif result == 'skipped':
                        stats['skipped'] += 1
                    else:
                        stats['errors'] += 1
                
                url = data.get('next')
                params = {}  # Clear params after first request (next URL includes them)
                page += 1
                
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"[ERROR] API request failed: {e}"))
                stats['errors'] += 1
                break
        
        return stats
    
    def process_facility(self, data):
        """Process single facility from MFL API"""
        try:
            # Skip if no name
            name = data.get('name', '').strip()
            if not name:
                return 'skipped'
            
            # Get or create county
            county_name = data.get('county', {}).get('name', '')
            if not county_name:
                return 'skipped'
            county, _ = County.objects.get_or_create(name=county_name)
            
            # Get or create facility type
            type_name = data.get('facility_type', {}).get('name', 'Unknown')
            facility_type, _ = FacilityType.objects.get_or_create(name=type_name)
            
            # Only use coordinates if facility is NOT classified
            lat = None
            lng = None
            if not data.get('is_classified', True):
                lat_lng = data.get('lat_lng') or {}
                lat = lat_lng.get('lat') or data.get('latitude')
                lng = lat_lng.get('lng') or data.get('longitude')
            
            # Prepare update data
            defaults = {
                'mfl_code': str(data.get('code')),
                'name': name,
                'county': county,
                'facility_type': facility_type,
                'constituency': data.get('constituency', {}).get('name', '') if data.get('constituency') else '',
                'ward': data.get('ward', {}).get('name', '') if data.get('ward') else '',
                'address': data.get('location_desc', '') or '',
                'latitude': lat,
                'longitude': lng,
                'phone': data.get('phone', '') or '',
                'is_24_hours': data.get('open_whole_day', False),
                'is_published_in_mfl': data.get('is_published', False),
                'is_verified': data.get('is_published', False),
                'is_active': data.get('is_active', True),
                'last_mfl_sync': timezone.now(),
            }
            
            if self.verbosity >= 2:
                self.stdout.write(f"  Processing: {name}")
            
            if self.is_dry_run:
                action = 'update' if Facility.objects.filter(mfl_uuid=data.get('id')).exists() else 'create'
                self.stdout.write(f"  [DRY RUN] Would {action}: {name}")
                return 'skipped'
            
            # Update or create
            facility, created = Facility.objects.update_or_create(
                mfl_uuid=data.get('id'),
                defaults=defaults
            )
            
            return 'created' if created else 'updated'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  [ERROR] {e}"))
            return 'error'
    
    def print_summary(self, stats):
        """Print sync summary"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("SYNC SUMMARY")
        self.stdout.write("=" * 50)
        self.stdout.write(f"  Total fetched: {stats['total_fetched']}")
        self.stdout.write(self.style.SUCCESS(f"  Created: {stats['created']}"))
        self.stdout.write(f"  Updated: {stats['updated']}")
        self.stdout.write(f"  Skipped: {stats['skipped']}")
        if stats['errors']:
            self.stdout.write(self.style.ERROR(f"  Errors: {stats['errors']}"))
        else:
            self.stdout.write(f"  Errors: {stats['errors']}")
        
        if self.is_dry_run:
            self.stdout.write(self.style.WARNING("\n[!] This was a DRY RUN. No changes were saved."))
            self.stdout.write("   Run without --dry-run to apply changes.")
