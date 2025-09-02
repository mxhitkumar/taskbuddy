from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import ServiceProviderProfile, Booking, Review

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username","email","role","verification_status","created_at")
    list_filter = ("role","verification_status")
    search_fields = ("username","email","phone_number")

@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    list_display = ("user","designation","pricing","average_rating")
    search_fields = ("user__username","designation")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id","customer","provider","service_date","status")
    list_filter = ("status","service_date")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id","booking","rating","created_at")
