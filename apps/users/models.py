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
    is_email_verified = models.BooleanField(default=False, db_index=True)  # Email verification only
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
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
            models.Index(fields=['is_email_verified']),
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


class EmailOTP(models.Model):
    """
    Email OTP for verification and password reset
    Improved with better security and tracking
    """
    
    class OTPPurpose(models.TextChoices):
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', _('Email Verification')
        PASSWORD_RESET = 'PASSWORD_RESET', _('Password Reset')
        LOGIN_2FA = 'LOGIN_2FA', _('Two-Factor Authentication')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_otps')
    email = models.EmailField()  # Store email for reference
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=OTPPurpose.choices)
    
    # Security
    is_used = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)  # Track verification attempts
    max_attempts = models.PositiveIntegerField(default=5)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'email_otps'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
            models.Index(fields=['email', 'otp_code']),
            models.Index(fields=['expires_at', 'is_used']),
        ]
    
    def __str__(self):
        return f"OTP for {self.email} - {self.purpose}"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        from django.utils import timezone
        return (
            not self.is_used and 
            not self.is_expired and 
            self.expires_at > timezone.now() and
            self.attempts < self.max_attempts
        )
    
    def verify(self, code):
        """Verify OTP code"""
        from django.utils import timezone
        
        self.attempts += 1
        
        if not self.is_valid():
            self.is_expired = True
            self.save()
            return False
        
        if self.otp_code == code:
            self.is_used = True
            self.verified_at = timezone.now()
            self.save()
            return True
        
        self.save()
        return False