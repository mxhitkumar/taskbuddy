"""
Booking signals for automatic updates
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking


@receiver(post_save, sender=Booking)
def update_booking_count(sender, instance, created, **kwargs):
    """
    Update service booking count when booking is created
    """
    if created:
        service = instance.service
        service.booking_count += 1
        service.save(update_fields=['booking_count'])
        
        # Update provider total bookings
        provider_profile = instance.provider.provider_profile
        provider_profile.total_bookings += 1
        
        # Update completed bookings if applicable
        if instance.status == 'COMPLETED':
            provider_profile.completed_bookings += 1
        
        provider_profile.save(update_fields=['total_bookings', 'completed_bookings'])


@receiver(post_save, sender=Booking)
def update_completed_bookings(sender, instance, created, **kwargs):
    """
    Update completed bookings count when status changes to completed
    """
    if not created and instance.status == 'COMPLETED':
        provider_profile = instance.provider.provider_profile
        
        # Check if this is the first time marked as completed
        if instance.tracker.has_changed('status'):
            provider_profile.completed_bookings += 1
            provider_profile.save(update_fields=['completed_bookings'])