from django.contrib import admin
from .models import USSDsession

@admin.register(USSDsession)
class USSDsessionAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'menu_level', 'created_at', 'is_active']
    list_filter = ['menu_level', 'is_active']
    search_fields = ['phone_number', 'session_id']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'session_data_display']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'phone_number', 'menu_level', 'is_active')
        }),
        ('Session Data', {
            'fields': ('session_data_display',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def session_data_display(self, obj):
        import json
        return json.dumps(obj.session_data, indent=2)
    session_data_display.short_description = 'Session Data (JSON)'