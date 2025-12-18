from rest_framework import serializers
from .models import Facility, FacilityType, Service

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id', 'name', 'county', 'town', 'phone', 'address', 
                 'emergency_available', 'accepts_nhif', 'is_verified']

class FacilityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityType
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'