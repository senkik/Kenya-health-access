from django.contrib import admin
from .models import County

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'capital']
    search_fields = ['name', 'code']
    
    