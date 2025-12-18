from rest_framework import serializers
from .models import County

class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = '__all__'
