"""
User models with role-based access control
Optimized for high-scale operations with proper indexing
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model supporting 4 roles: Superadmin, Admin, Service Provider, Customer
    """
    
    class UserRole(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', _('Superadmin')
        ADMIN = 'ADMIN', _('Admin')
        SERVICE_PROVIDER = 'SERVICE_PROVIDER', _('Service Provider')
        CUSTOMER = 'CUSTOMER', _('Customer')
    
    # Basic Information
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    # Role & Status
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # Email/Phone verification
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_superadmin(self):
        return self.role == self.UserRole.SUPERADMIN
    
    def is_admin(self):
        return self.role in [self.UserRole.SUPERADMIN, self.UserRole.ADMIN]
    
    def is_service_provider(self):
        return self.role == self.UserRole.SERVICE_PROVIDER
    
    def is_customer(self):
        return self.role == self.UserRole.CUSTOMER


class UserProfile(models.Model):
    """
    Extended profile information for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True, db_index=True)
    state = models.CharField(max_length=100, blank=True, db_index=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Geolocation for proximity-based searches
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        indexes = [
            models.Index(fields=['city', 'state']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"Profile: {self.user.email}"


class ServiceProviderProfile(models.Model):
    """
    Additional information for service providers
    """
    
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        UNDER_REVIEW = 'UNDER_REVIEW', _('Under Review')
        VERIFIED = 'VERIFIED', _('Verified')
        REJECTED = 'REJECTED', _('Rejected')
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='provider_profile',
        limit_choices_to={'role': User.UserRole.SERVICE_PROVIDER}
    )
    
    # Business Information
    business_name = models.CharField(max_length=255)
    business_description = models.TextField()
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Verification
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_providers',
        limit_choices_to={'role__in': [User.UserRole.SUPERADMIN, User.UserRole.ADMIN]}
    )
    
    # Documents
    id_proof = models.FileField(upload_to='verifications/id_proofs/', null=True, blank=True)
    business_license = models.FileField(upload_to='verifications/licenses/', null=True, blank=True)
    certificate = models.FileField(upload_to='verifications/certificates/', null=True, blank=True)
    
    # Ratings & Performance (denormalized for faster queries)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, db_index=True)
    total_reviews = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    
    # Availability
    is_available = models.BooleanField(default=True, db_index=True)
    max_concurrent_bookings = models.PositiveIntegerField(default=5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_provider_profiles'
        ordering = ['-average_rating', '-total_reviews']
        indexes = [
            models.Index(fields=['verification_status', 'is_available']),
            models.Index(fields=['average_rating', 'total_reviews']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.business_name} - {self.user.email}"
    
    def update_rating_stats(self):
        """
        Update denormalized rating statistics
        Called by signals when reviews are added/updated
        """
        from apps.reviews.models import Review
        from django.db.models import Avg, Count
        
        stats = Review.objects.filter(
            provider=self.user,
            is_active=True
        ).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        
        self.average_rating = stats['avg_rating'] or 0.00
        self.total_reviews = stats['count']
        self.save(update_fields=['average_rating', 'total_reviews', 'updated_at'])


class OTPVerification(models.Model):
    """
    OTP for email/phone verification
    """
    
    class OTPType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email Verification')
        PHONE = 'PHONE', _('Phone Verification')
        PASSWORD_RESET = 'PASSWORD_RESET', _('Password Reset')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_type = models.CharField(max_length=20, choices=OTPType.choices)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'otp_verifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp_type', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_type}"Commit at 2025-01-11T10:20:36
Commit at 2025-01-20T16:26:20
Commit at 2025-02-03T10:08:54
Commit at 2025-02-20T13:01:40
Commit at 2025-02-24T12:58:05
Commit at 2025-02-25T10:44:19
Commit at 2025-02-25T11:55:32
Commit at 2025-03-03T11:51:51
Commit at 2025-03-04T11:09:27
