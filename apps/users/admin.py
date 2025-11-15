"""
Django Admin configuration for User models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from apps.users.models import User, UserProfile, ServiceProviderProfile, EmailOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_active', 'is_email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_email_verified', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_email_verified')}),
        ('Important Dates', {'fields': ('last_login', 'email_verified_at', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'email_verified_at']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'state', 'country']
    search_fields = ['user__email', 'city', 'state']
    list_filter = ['city', 'state', 'country']


@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'verification_status', 'average_rating', 'total_bookings', 'is_available']
    list_filter = ['verification_status', 'is_available', 'created_at']
    search_fields = ['user__email', 'business_name']
    readonly_fields = ['average_rating', 'total_reviews', 'total_bookings', 'completed_bookings']
    
    fieldsets = (
        ('Business Information', {
            'fields': ('user', 'business_name', 'business_description', 'years_of_experience')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verified_at', 'verified_by', 'id_proof', 'business_license', 'certificate')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_reviews', 'total_bookings', 'completed_bookings')
        }),
        ('Availability', {
            'fields': ('is_available', 'max_concurrent_bookings')
        }),
    )


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'purpose', 'otp_code_display', 'is_used', 'is_expired', 'attempts', 'expires_at', 'created_at']
    list_filter = ['purpose', 'is_used', 'is_expired', 'created_at']
    search_fields = ['user__email', 'email', 'otp_code', 'ip_address']
    readonly_fields = ['created_at', 'verified_at', 'ip_address', 'user_agent']
    ordering = ['-created_at']
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('user', 'email', 'otp_code', 'purpose')
        }),
        ('Status', {
            'fields': ('is_used', 'is_expired', 'attempts', 'max_attempts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'verified_at')
        }),
        ('Tracking', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def otp_code_display(self, obj):
        """Display OTP code with status color"""
        if obj.is_used:
            color = 'green'
            status = '✓ Used'
        elif obj.is_expired:
            color = 'red'
            status = '✗ Expired'
        elif obj.expires_at < timezone.now():
            color = 'orange'
            status = '⏰ Expired (auto)'
        else:
            color = 'blue'
            status = '◷ Active'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span> <small>({})</small>',
            color, obj.otp_code, status
        )
    otp_code_display.short_description = 'OTP Code'
    
    actions = ['mark_as_expired', 'delete_old_otps']
    
    def mark_as_expired(self, request, queryset):
        """Mark selected OTPs as expired"""
        count = queryset.update(is_expired=True)
        self.message_user(request, f'{count} OTP(s) marked as expired.')
    mark_as_expired.short_description = "Mark selected as expired"
    
    def delete_old_otps(self, request, queryset):
        """Delete OTPs older than 30 days"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(days=30)
        count = queryset.filter(created_at__lt=cutoff).delete()[0]
        self.message_user(request, f'{count} old OTP(s) deleted.')
    delete_old_otps.short_description = "Delete OTPs older than 30 days"


# Import timezone for the admin display
from django.utils import timezone