from django.contrib import admin
from .models import HealthArticle, HealthTip

@admin.register(HealthArticle)
class HealthArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_verified', 'language', 'created_at']
    list_filter = ['category', 'is_verified', 'language']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ['title']}

@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ['tip', 'category', 'language', 'is_active']
    list_filter = ['category', 'language', 'is_active']
    search_fields = ['tip']