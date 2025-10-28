"""
Review signals for automatic rating updates
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.reviews.models import Review


@receiver(post_save, sender=Review)
def update_ratings_on_review_save(sender, instance, created, **kwargs):
    """
    Update provider and service ratings when review is created/updated
    """
    if created or instance.tracker.has_changed('rating'):
        # Queue async task to update ratings
        from apps.reviews.tasks import update_ratings
        update_ratings.delay(instance.provider.id, instance.service.id)


@receiver(post_delete, sender=Review)
def update_ratings_on_review_delete(sender, instance, **kwargs):
    """
    Update ratings when review is deleted
    """
    from apps.reviews.tasks import update_ratings
    update_ratings.delay(instance.provider.id, instance.service.id)