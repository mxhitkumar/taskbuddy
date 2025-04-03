"""
Django Admin configuration for User models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User, UserProfile, ServiceProviderProfile, OTPVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_active', 'is_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_verified', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
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


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_type', 'otp_code', 'is_used', 'expires_at', 'created_at']
    list_filter = ['otp_type', 'is_used', 'created_at']
    search_fields = ['user__email', 'otp_code']
    readonly_fields = ['created_at']Commit at 2025-01-13T15:40:45
Commit at 2025-01-13T16:02:21
Commit at 2025-01-15T12:34:10
Commit at 2025-01-16T14:31:02
Commit at 2025-01-20T14:02:17
Commit at 2025-01-31T16:00:23
Commit at 2025-02-12T12:16:16
Commit at 2025-02-18T10:50:04
Commit at 2025-02-20T14:50:42
Commit at 2025-02-21T09:38:56
Commit at 2025-02-26T10:55:17
Commit at 2025-02-26T12:55:24
Commit at 2025-03-03T09:16:48
Commit at 2025-03-10T13:31:36
Commit at 2025-03-11T14:00:02
Commit at 2025-03-12T14:57:05
Commit at 2025-03-13T15:41:51
Commit at 2025-03-19T16:30:36
Commit at 2025-03-20T09:27:48
Commit at 2025-03-20T14:12:06
Commit at 2025-03-26T11:31:39
Commit at 2025-03-27T14:50:12
Commit at 2025-04-02T13:34:21
Commit at 2025-04-03T10:05:45
