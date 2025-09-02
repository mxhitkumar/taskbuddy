from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ServiceProviderProfile

User = get_user_model()

@receiver(post_save, sender=User)
def ensure_provider_profile(sender, instance, created, **kwargs):
    if instance.role == "provider":
        ServiceProviderProfile.objects.get_or_create(user=instance)
