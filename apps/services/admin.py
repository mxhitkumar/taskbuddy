"""
Django Admin configuration for Service models
"""
from django.contrib import admin
from apps.services.models import (
    ServiceCategory, Service, ServiceImage, 
    ServiceAvailability, ServiceArea
)


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'is_active', 'service_count', 'provider_count']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'category', 'pricing_type', 'base_price', 'average_rating', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'pricing_type', 'category', 'created_at']
    search_fields = ['title', 'description', 'provider__email', 'provider__first_name', 'provider__last_name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'booking_count', 'average_rating', 'review_count', 'created_at', 'updated_at']
    inlines = [ServiceImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'provider', 'category')
        }),
        ('Pricing', {
            'fields': ('pricing_type', 'base_price', 'currency', 'duration_minutes')
        }),
        ('Media', {
            'fields': ('thumbnail',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('view_count', 'booking_count', 'average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceAvailability)
class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['provider', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available', 'provider']
    search_fields = ['provider__email', 'provider__first_name', 'provider__last_name']


@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ['provider', 'city', 'state', 'service_radius_km', 'is_active']
    list_filter = ['city', 'state', 'is_active']
    search_fields = ['provider__email', 'city', 'state']