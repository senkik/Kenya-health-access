from django.contrib import admin
from .models import FacilityType, Service, Facility, Review

@admin.register(FacilityType)
class FacilityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['facility', 'user_name', 'rating', 'created_at', 'is_approved']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['facility__name', 'user_name', 'comment']
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    reject_reviews.short_description = "Reject/Hide selected reviews"

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'facility_type', 'availability_status', 'is_verified', 'average_rating']
    list_filter = ['county', 'is_verified', 'availability_status', 'accepts_sha']
    search_fields = ['name', 'county__name', 'phone']
    filter_horizontal = ['services']
    readonly_fields = ['last_status_update', 'uuid']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'facility_type', 'is_verified', 'verified_date', 'uuid')
        }),
        ('Location', {
            'fields': ('county', 'constituency', 'town', 'address', 'latitude', 'longitude')
        }),
        ('Availability & Status', {
            'fields': ('availability_status', 'last_status_update', 'opening_hours', 'is_24_hours')
        }),
        ('Services & Features', {
            'fields': ('services', 'emergency_available', 'ambulance_available', 'accepts_sha', 'sha_code')
        }),
        ('Contact Info', {
            'fields': ('phone', 'email', 'website')
        }),
    )