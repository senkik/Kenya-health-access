from rest_framework import serializers
from .models import Facility, FacilityType, Service, Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'facility', 'rating', 'comment', 'user_name', 'created_at']
        read_only_fields = ['created_at']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class FacilityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityType
        fields = '__all__'

class FacilitySerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    facility_type_name = serializers.CharField(source='facility_type.name', read_only=True)
    county_name = serializers.CharField(source='county.name', read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = [
            'id', 'uuid', 'name', 'mfl_code',
            'facility_type', 'facility_type_name',
            'county', 'county_name',
            'constituency', 'ward', 'town',
            'phone', 'address',
            'latitude', 'longitude',
            'emergency_available', 'ambulance_available',
            'accepts_sha', 'is_verified',
            'is_24_hours', 'opening_hours',
            'services',
            'average_rating', 'total_reviews',
            'availability_status', 'last_status_update',
            'distance_km',
        ]

    def get_distance_km(self, obj):
        """Return distance in km if the queryset was annotated with distance."""
        if hasattr(obj, 'distance') and obj.distance is not None:
            return round(obj.distance.km, 2)
        return None