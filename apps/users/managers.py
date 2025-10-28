"""
Custom User Manager for user creation
"""
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    """
    
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'SUPERADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
    
    def get_active_users(self):
        """Get all active users"""
        return self.filter(is_active=True)
    
    def get_service_providers(self):
        """Get all service providers"""
        return self.filter(role='SERVICE_PROVIDER', is_active=True)
    
    def get_customers(self):
        """Get all customers"""
        return self.filter(role='CUSTOMER', is_active=True)
    
    def get_verified_providers(self):
        """Get verified service providers"""
        return self.filter(
            role='SERVICE_PROVIDER',
            is_active=True,
            is_verified=True,
            provider_profile__verification_status='VERIFIED'
        )