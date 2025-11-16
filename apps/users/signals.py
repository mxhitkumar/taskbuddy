"""
User signals for automatic profile creation and updates
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User, UserProfile, ServiceProviderProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when User is created
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
        
        # Create ServiceProviderProfile if user is a service provider
        if instance.role == User.UserRole.SERVICE_PROVIDER:
            ServiceProviderProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save profile when user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()