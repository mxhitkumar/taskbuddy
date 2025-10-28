"""
Django Admin configuration for Booking models
"""
from django.contrib import admin
from apps.bookings.models import Booking, BookingStatusHistory, BookingAttachment


class BookingStatusHistoryInline(admin.TabularInline):
    model = BookingStatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'notes', 'created_at']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'customer', 'provider', 'service', 'status', 'scheduled_date', 'total_amount', 'created_at']
    list_filter = ['status', 'scheduled_date', 'created_at']
    search_fields = ['booking_reference', 'customer__email', 'provider__email', 'service__title']
    readonly_fields = ['booking_reference', 'total_amount', 'created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at']
    inlines = [BookingStatusHistoryInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'customer', 'provider', 'service', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'scheduled_time', 'estimated_duration_minutes', 'actual_start_time', 'actual_end_time')
        }),
        ('Location', {
            'fields': ('service_address', 'service_city', 'service_state', 'service_postal_code', 'latitude', 'longitude')
        }),
        ('Pricing', {
            'fields': ('base_price', 'additional_charges', 'tax_amount', 'discount_amount', 'total_amount', 'currency')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'provider_notes', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('confirmed_at', 'completed_at', 'cancelled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['booking', 'from_status', 'to_status', 'changed_by', 'created_at']
    list_filter = ['from_status', 'to_status', 'created_at']
    search_fields = ['booking__booking_reference', 'notes']
    readonly_fields = ['created_at']


@admin.register(BookingAttachment)
class BookingAttachmentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'attachment_type', 'uploaded_by', 'created_at']
    list_filter = ['attachment_type', 'created_at']
    search_fields = ['booking__booking_reference', 'description']