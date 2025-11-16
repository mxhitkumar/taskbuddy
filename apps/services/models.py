"""
Service and Category Models
Optimized with proper indexing and caching strategies
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class ServiceCategory(models.Model):
    """
    Service categories (e.g., Plumbing, Electrical, Cooking, Cleaning)
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='categories/icons/', null=True, blank=True)
    
    # Hierarchy support
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    
    # Display order
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Statistics (denormalized)
    service_count = models.PositiveIntegerField(default=0)
    provider_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_categories'
        ordering = ['order', 'name']
        verbose_name_plural = 'Service Categories'
        indexes = [
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['parent', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_full_path(self):
        """Get category hierarchy path"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Service(models.Model):
    """
    Services offered by providers
    """
    
    class PricingType(models.TextChoices):
        FIXED = 'FIXED', _('Fixed Price')
        HOURLY = 'HOURLY', _('Hourly Rate')
        CUSTOM = 'CUSTOM', _('Custom Quote')
    
    # Basic Information
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    
    # Relationships
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='services',
        limit_choices_to={'role': User.UserRole.SERVICE_PROVIDER}
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='services',
        db_index=True
    )
    
    # Pricing
    pricing_type = models.CharField(
        max_length=10,
        choices=PricingType.choices,
        default=PricingType.FIXED
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Service Details
    duration_minutes = models.PositiveIntegerField(
        help_text='Estimated duration in minutes',
        null=True,
        blank=True
    )
    
    # Media
    thumbnail = models.ImageField(upload_to='services/thumbnails/', null=True, blank=True)
    
    # Availability
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    
    # Statistics (denormalized for performance)
    view_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        db_index=True
    )
    review_count = models.PositiveIntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        ordering = ['-is_featured', '-average_rating', '-created_at']
        indexes = [
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['-average_rating', '-review_count']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.provider.full_name}"
    
    def increment_view_count(self):
        """Increment view count atomically"""
        self.__class__.objects.filter(pk=self.pk).update(
            view_count=models.F('view_count') + 1
        )


class ServiceImage(models.Model):
    """
    Additional images for services
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='services/images/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_images'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['service', 'order']),
        ]
    
    def __str__(self):
        return f"Image for {self.service.title}"


class ServiceAvailability(models.Model):
    """
    Provider's availability schedule
    """
    
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')
    
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='availability_schedule',
        limit_choices_to={'role': User.UserRole.SERVICE_PROVIDER}
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices, db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_availability'
        ordering = ['day_of_week', 'start_time']
        unique_together = [['provider', 'day_of_week', 'start_time']]
        indexes = [
            models.Index(fields=['provider', 'day_of_week', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.provider.full_name} - {self.get_day_of_week_display()}"


class ServiceArea(models.Model):
    """
    Geographic service areas for providers
    """
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_areas',
        limit_choices_to={'role': User.UserRole.SERVICE_PROVIDER}
    )
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Radius in kilometers
    service_radius_km = models.PositiveIntegerField(default=10)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_areas'
        unique_together = [['provider', 'city', 'state']]
        indexes = [
            models.Index(fields=['city', 'state', 'is_active']),
            models.Index(fields=['provider', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.city}, {self.state} - {self.provider.full_name}"