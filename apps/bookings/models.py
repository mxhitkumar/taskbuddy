"""
Booking Management Models
Handles booking lifecycle with optimized queries
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from users.models import User
from services.models import Service


class Booking(models.Model):
    """
    Service booking model
    """
    
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending Confirmation')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REFUNDED = 'REFUNDED', _('Refunded')
    
    # Unique booking reference
    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Relationships
    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bookings_as_customer',
        limit_choices_to={'role': User.UserRole.CUSTOMER}
    )
    provider = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bookings_as_provider',
        limit_choices_to={'role': User.UserRole.SERVICE_PROVIDER}
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    
    # Booking Details
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        db_index=True
    )
    
    # Schedule
    scheduled_date = models.DateField(db_index=True)
    scheduled_time = models.TimeField()
    estimated_duration_minutes = models.PositiveIntegerField()
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Location
    service_address = models.TextField()
    service_city = models.CharField(max_length=100, db_index=True)
    service_state = models.CharField(max_length=100)
    service_postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Notes
    customer_notes = models.TextField(blank=True)
    provider_notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Timestamps
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['service', 'status']),
            models.Index(fields=['scheduled_date', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.booking_reference} - {self.service.title}"
    
    def save(self, *args, **kwargs):
        # Generate booking reference if new
        if not self.booking_reference:
            import uuid
            self.booking_reference = f"BK{uuid.uuid4().hex[:12].upper()}"
        
        # Calculate total amount
        self.total_amount = (
            self.base_price + 
            self.additional_charges + 
            self.tax_amount - 
            self.discount_amount
        )
        
        super().save(*args, **kwargs)
    
    def can_cancel(self):
        """Check if booking can be cancelled"""
        return self.status in [
            self.BookingStatus.PENDING,
            self.BookingStatus.CONFIRMED
        ]
    
    def can_complete(self):
        """Check if booking can be marked as completed"""
        return self.status == self.BookingStatus.IN_PROGRESS
    
    def can_review(self):
        """Check if customer can leave a review"""
        from reviews.models import Review
        return (
            self.status == self.BookingStatus.COMPLETED and
            not Review.objects.filter(booking=self, customer=self.customer).exists()
        )


class BookingStatusHistory(models.Model):
    """
    Track booking status changes for audit trail
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20, db_index=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='booking_status_changes'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'booking_status_history'
        ordering = ['-created_at']
        verbose_name_plural = 'Booking Status Histories'
        indexes = [
            models.Index(fields=['booking', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.booking.booking_reference}: {self.from_status} → {self.to_status}"


class BookingAttachment(models.Model):
    """
    File attachments for bookings (e.g., photos of the problem, before/after)
    """
    
    class AttachmentType(models.TextChoices):
        CUSTOMER_UPLOAD = 'CUSTOMER', _('Customer Upload')
        PROVIDER_UPLOAD = 'PROVIDER', _('Provider Upload')
    
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    attachment_type = models.CharField(max_length=10, choices=AttachmentType.choices)
    file = models.FileField(upload_to='bookings/attachments/')
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_attachments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'attachment_type']),
        ]
    
    def __str__(self):
        return f"Attachment for {self.booking.booking_reference}"