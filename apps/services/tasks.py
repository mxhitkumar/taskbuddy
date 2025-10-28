"""
Celery tasks for services
"""
from celery import shared_task
from django.db.models import Count, Avg


@shared_task
def increment_service_views(service_id):
    """
    Increment service view count asynchronously
    """
    from apps.services.models import Service
    from django.db.models import F
    
    Service.objects.filter(id=service_id).update(
        view_count=F('view_count') + 1
    )


@shared_task
def update_service_statistics():
    """
    Update denormalized service statistics
    """
    from apps.services.models import Service, ServiceCategory
    from apps.reviews.models import Review
    from apps.bookings.models import Booking
    
    # Update service ratings and counts
    services = Service.objects.all()
    
    for service in services:
        # Update review stats
        review_stats = Review.objects.filter(
            service=service,
            is_active=True
        ).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        
        service.average_rating = review_stats['avg_rating'] or 0.00
        service.review_count = review_stats['count']
        
        # Update booking count
        service.booking_count = Booking.objects.filter(
            service=service
        ).count()
        
        service.save(update_fields=['average_rating', 'review_count', 'booking_count'])
    
    # Update category counts
    categories = ServiceCategory.objects.all()
    
    for category in categories:
        category.service_count = Service.objects.filter(
            category=category,
            is_active=True
        ).count()
        
        category.provider_count = Service.objects.filter(
            category=category,
            is_active=True
        ).values('provider').distinct().count()
        
        category.save(update_fields=['service_count', 'provider_count'])