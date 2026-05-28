from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q
from facilities.models import Facility, Service, FacilityType, Review
from facilities.serializers import FacilitySerializer, ServiceSerializer, FacilityTypeSerializer, ReviewSerializer
from content.models import HealthArticle, HealthTip
from locations.models import County

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """API for Kenyan counties"""
    queryset = County.objects.all()
    
    def get_serializer_class(self):
        # serializer for counties
        class CountySerializer(serializers.Serializer):
            id = serializers.IntegerField()
            name = serializers.CharField()
            code = serializers.CharField()
            capital = serializers.CharField()
        
        return CountySerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def list(self, request, *args, **kwargs):
        """List all counties with caching"""
        cache_key = 'counties_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=3600)  # Cache for 1 hour
        return response

class FacilityTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """API for facility types"""
    queryset = FacilityType.objects.all()
    serializer_class = FacilityTypeSerializer
    
    def list(self, request, *args, **kwargs):
        """List all facility types with caching"""
        cache_key = 'facility_types_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=3600)  # Cache for 1 hour
        return response

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """API for medical services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

class FacilityViewSet(viewsets.ModelViewSet):
    """Main API for healthcare facilities with advanced filtering.
    
    Supports the following query params:
        county          - Filter by county name (exact, case-insensitive)
        constituency    - Filter by constituency (partial, case-insensitive)
        town            - Filter by town/area (partial, case-insensitive)
        services        - Comma-separated service names (any match)
        is_24_hours     - Boolean filter for 24/7 facilities
        lat, lng, radius- PostGIS proximity search (radius in km, default 10)
        search          - Full-text search on name, town, address, constituency
        facility_type   - Filter by facility_type id
        accepts_sha     - Boolean filter
        emergency_available - Boolean filter
    """
    queryset = Facility.objects.filter(is_active=True)
    serializer_class = FacilitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['facility_type', 'accepts_sha', 'emergency_available']
    search_fields = ['name', 'town', 'address', 'constituency']
    ordering_fields = ['name', 'created_at']
    # Use uuid field for detail lookups instead of integer pk
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = Facility.objects.filter(is_active=True).select_related(
            'facility_type', 'county'
        ).prefetch_related('services')
        
        params = self.request.query_params

        # --- County filter (exact, case-insensitive) ---
        county = params.get('county', '').strip()
        if county:
            queryset = queryset.filter(county__name__iexact=county)

        # --- Constituency filter (partial, case-insensitive) ---
        constituency = params.get('constituency', '').strip()
        if constituency:
            queryset = queryset.filter(constituency__icontains=constituency)

        # --- Town / Area filter (partial, case-insensitive) ---
        town = params.get('town', '').strip()
        if town:
            queryset = queryset.filter(
                Q(town__icontains=town) | Q(address__icontains=town)
            )

        # --- Services filter (comma-separated names, match any) ---
        services_param = params.get('services', '').strip()
        if services_param:
            service_names = [s.strip() for s in services_param.split(',') if s.strip()]
            if service_names:
                queryset = queryset.filter(
                    services__name__in=service_names
                ).distinct()

        # --- 24/7 filter ---
        is_24 = params.get('is_24_hours', '').strip().lower()
        if is_24 in ('true', '1', 'yes'):
            queryset = queryset.filter(is_24_hours=True)
        elif is_24 in ('false', '0', 'no'):
            queryset = queryset.filter(is_24_hours=False)

        # --- Near Me (PostGIS distance) ---
        lat = params.get('lat', '').strip()
        lng = params.get('lng', '').strip()
        if lat and lng:
            try:
                from django.contrib.gis.geos import Point
                from django.contrib.gis.db.models.functions import Distance
                from django.contrib.gis.measure import D

                lat_f = float(lat)
                lng_f = float(lng)
                radius_km = float(params.get('radius', '10'))

                user_location = Point(lng_f, lat_f, srid=4326)
                queryset = queryset.filter(
                    location__isnull=False,
                    location__distance_lte=(user_location, D(km=radius_km))
                ).annotate(
                    distance=Distance('location', user_location)
                ).order_by('distance')
            except (ValueError, TypeError):
                pass  # silently ignore bad coordinates

        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Simple search endpoint"""
        query = request.query_params.get('q', '')
        county = request.query_params.get('county', '')

        facilities = self.get_queryset()

        if query:
            facilities = facilities.filter(name__icontains=query)

        if county:
            facilities = facilities.filter(county__name__iexact=county)

        # Limit to 20 results
        facilities = facilities[:20]
        serializer = self.get_serializer(facilities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_county(self, request):
        """Get facilities by county"""
        county = request.query_params.get('county', '')
        if not county:
            return Response(
                {'error': 'County parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        facilities = self.get_queryset().filter(county__name__iexact=county)
        serializer = self.get_serializer(facilities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def constituencies(self, request):
        """Return distinct constituency values for dropdowns."""
        values = (
            Facility.objects
            .filter(is_active=True)
            .exclude(constituency='')
            .values_list('constituency', flat=True)
            .distinct()
            .order_by('constituency')
        )
        return Response(list(values))

    @action(detail=False, methods=['get'])
    def towns(self, request):
        """Return distinct town values for autocomplete."""
        q = request.query_params.get('q', '').strip()
        qs = (
            Facility.objects
            .filter(is_active=True)
            .exclude(town='')
        )
        if q:
            qs = qs.filter(town__icontains=q)
        values = qs.values_list('town', flat=True).distinct().order_by('town')[:50]
        return Response(list(values))

    @action(detail=True, methods=['post'])
    def update_availability(self, request, uuid=None):
        """Update facility availability status"""
        facility = self.get_object()
        status_value = request.data.get('status')
        
        if status_value not in dict(Facility.AVAILABILITY_CHOICES):
            return Response(
                {'error': 'Invalid status. Choose from: available, busy, emergency_only, closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        facility.availability_status = status_value
        facility.save()
        
        return Response({
            'status': facility.availability_status,
            'last_updated': facility.last_status_update
        })

class HealthArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """API for health articles"""
    queryset = HealthArticle.objects.filter(is_published=True)
    
    def get_serializer_class(self):
        class ArticleSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            title = serializers.CharField()
            slug = serializers.CharField()
            category = serializers.CharField()
            excerpt = serializers.CharField()
            author = serializers.CharField()
            language = serializers.CharField()
            created_at = serializers.DateTimeField()
        
        return ArticleSerializer
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'language']

class HealthTipViewSet(viewsets.ReadOnlyModelViewSet):
    """API for health tips"""
    queryset = HealthTip.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        class TipSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            tip = serializers.CharField()
            category = serializers.CharField()
            language = serializers.CharField()
        
        return TipSerializer
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get a random health tip"""
        tip = self.get_queryset().order_by('?').first()
        if tip:
            serializer = self.get_serializer(tip)
            return Response(serializer.data)
        return Response({'tip': 'No health tips available'})

class ReviewViewSet(viewsets.ModelViewSet):
    """API for facility reviews"""
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['facility']
    ordering_fields = ['created_at', 'rating']

    def perform_create(self, serializer):
        # By default reviews are approved in this demo
        serializer.save(is_approved=True)