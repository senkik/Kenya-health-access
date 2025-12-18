from rest_framework import serializers
from .models import HealthArticle

class HealthArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthArticle
        fields = '__all__'
