from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

ROLE_CHOICES = [
    ("admin", "Admin"),
    ("customer", "Customer"),
    ("provider", "Service Provider"),
]

VERIF_CHOICES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True, default="customer")

    # Location
    location_lat = models.FloatField(null=True, blank=True, db_index=True)
    location_long = models.FloatField(null=True, blank=True, db_index=True)
    location_text = models.CharField(max_length=255, blank=True, null=True)

    # For providers
    govt_id = models.FileField(upload_to="govt_ids/", null=True, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIF_CHOICES, default="pending", db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        indexes = [
            models.Index(fields=["role", "verification_status"]),
            models.Index(fields=["location_lat", "location_long"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"


class ServiceProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="provider_profile")
    designation = models.CharField(max_length=100)
    skills = models.TextField(blank=True)
    pricing = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability = models.JSONField(default=dict, blank=True)  # e.g. {"mon": ["09:00-12:00", ...]}
    average_rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.designation}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_bookings")
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="provider_bookings")
    service_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    issue_description = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, default="pending", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["customer", "provider", "status"]),
            models.Index(fields=["service_date"]),
        ]

    def __str__(self):
        return f"Booking {self.id}: {self.customer} -> {self.provider} at {self.service_date}"


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
