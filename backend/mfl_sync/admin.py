from django.contrib import admin
from .models import MFLSyncLog

@admin.register(MFLSyncLog)
class MFLSyncLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'started_at', 'completed_at', 'status', 'facilities_created', 'facilities_updated']
    list_filter = ['status', 'started_at']
    readonly_fields = ['started_at', 'completed_at', 'status', 'facilities_created', 'facilities_updated', 'errors']
