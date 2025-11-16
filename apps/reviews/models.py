"""
Review and Rating Models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import User
from services.models import Service
from bookings.models import Booking


class Review(models.Model):
    """
    Customer reviews for service providers
    """
    # Relationships
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review'
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        limit_choices_to={'role': User.UserRole.CUSTOMER}
    )
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        limit_choices_to={'role': User.UserRole.SERVICE_PROVIDER}
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # Rating (1-5 stars)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_index=True
    )
    
    # Review Content
    title = models.CharField(max_length=255)
    comment = models.TextField()
    
    # Sub-ratings (optional)
    quality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    punctuality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    professionalism_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    value_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False)  # Verified purchase
    is_featured = models.BooleanField(default=False)
    
    # Moderation
    is_flagged = models.BooleanField(default=False)
    flagged_reason = models.TextField(blank=True)
    moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews'
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    helpful_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider', 'is_active', '-rating']),
            models.Index(fields=['service', 'is_active', '-rating']),
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['-rating', '-helpful_count']),
        ]
    
    def __str__(self):
        return f"Review by {self.customer.full_name} for {self.provider.full_name}"
    
    def save(self, *args, **kwargs):
        # Mark as verified if linked to completed booking
        if self.booking and self.booking.status == 'COMPLETED':
            self.is_verified = True
        
        super().save(*args, **kwargs)


class ReviewResponse(models.Model):
    """
    Provider responses to reviews
    """
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response'
    )
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_responses'
    )
    response_text = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'review_responses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Response to review #{self.review.id}"


class ReviewImage(models.Model):
    """
    Images attached to reviews
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='reviews/images/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_images'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for review #{self.review.id}"


class ReviewHelpful(models.Model):
    """
    Track which users found a review helpful
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_helpful'
        unique_together = [['review', 'user']]
        indexes = [
            models.Index(fields=['review', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} found review #{self.review.id} helpful"