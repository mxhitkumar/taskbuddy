"""
Celery tasks for reviews
"""
from celery import shared_task
from django.db.models import Avg, Count


@shared_task
def update_ratings(provider_id, service_id):
    """
    Update provider and service ratings after review changes
    """
    from users.models import ServiceProviderProfile
    from services.models import Service
    from reviews.models import Review
    
    # Update provider profile ratings
    try:
        provider_profile = ServiceProviderProfile.objects.get(user_id=provider_id)
        provider_profile.update_rating_stats()
    except ServiceProviderProfile.DoesNotExist:
        pass
    
    # Update service ratings
    try:
        service = Service.objects.get(id=service_id)
        review_stats = Review.objects.filter(
            service=service,
            is_active=True
        ).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        
        service.average_rating = review_stats['avg_rating'] or 0.00
        service.review_count = review_stats['count']
        service.save(update_fields=['average_rating', 'review_count'])
    except Service.DoesNotExist:
        pass