from django.contrib import admin
from .models import USSDsession

@admin.register(USSDsession)
class USSDsessionAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'menu_level', 'is_active', 'created_at']
    list_filter = ['menu_level', 'is_active']
    search_fields = ['phone_number', 'session_id']