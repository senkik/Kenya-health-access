from rest_framework import serializers
from .models import Facility, FacilityType, Service, Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'facility', 'rating', 'comment', 'user_name', 'created_at']
        read_only_fields = ['created_at']

class FacilitySerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    facility_type_name = serializers.CharField(source='facility_type.name', read_only=True)
    county_name = serializers.CharField(source='county.name', read_only=True)

    class Meta:
        model = Facility
        fields = ['id', 'uuid', 'name', 'facility_type', 'facility_type_name', 
                 'county', 'county_name', 'town', 'phone', 'address', 
                 'emergency_available', 'accepts_nhif', 'is_verified',
                 'average_rating', 'total_reviews', 
                 'availability_status', 'last_status_update']

class FacilityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityType
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'