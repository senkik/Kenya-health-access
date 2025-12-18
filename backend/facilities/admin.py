from django.contrib import admin
from .models import FacilityType, Service, Facility

@admin.register(FacilityType)
class FacilityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'facility_type', 'phone', 'is_verified']
    list_filter = ['county', 'is_verified', 'accepts_nhif']
    search_fields = ['name', 'county', 'phone']
    filter_horizontal = ['services']