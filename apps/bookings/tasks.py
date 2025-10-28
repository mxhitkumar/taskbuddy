"""
Celery tasks for bookings
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_notification(booking_id):
    """
    Send notification when a new booking is created
    """
    from apps.bookings.models import Booking
    
    try:
        booking = Booking.objects.select_related(
            'customer', 'provider', 'service'
        ).get(id=booking_id)
        
        # Send email to provider
        subject = f'New Booking: {booking.service.title}'
        message = f"""
        You have a new booking!
        
        Booking Reference: {booking.booking_reference}
        Customer: {booking.customer.full_name}
        Service: {booking.service.title}
        Date: {booking.scheduled_date}
        Time: {booking.scheduled_time}
        
        Please log in to confirm or decline this booking.
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [booking.provider.email],
            fail_silently=True,
        )
        
        # Send confirmation to customer
        customer_subject = 'Booking Confirmation'
        customer_message = f"""
        Thank you for your booking!
        
        Booking Reference: {booking.booking_reference}
        Service: {booking.service.title}
        Provider: {booking.provider.full_name}
        Date: {booking.scheduled_date}
        Time: {booking.scheduled_time}
        
        We will notify you once the provider confirms your booking.
        """
        
        send_mail(
            customer_subject,
            customer_message,
            settings.EMAIL_HOST_USER,
            [booking.customer.email],
            fail_silently=True,
        )
        
    except Booking.DoesNotExist:
        pass


@shared_task
def send_status_update_notification(booking_id, old_status, new_status):
    """
    Send notification when booking status changes
    """
    from apps.bookings.models import Booking
    
    try:
        booking = Booking.objects.select_related(
            'customer', 'provider', 'service'
        ).get(id=booking_id)
        
        subject = f'Booking Status Update: {booking.booking_reference}'
        message = f"""
        Your booking status has been updated.
        
        Booking Reference: {booking.booking_reference}
        Service: {booking.service.title}
        Status: {new_status}
        
        Please log in to view more details.
        """
        
        # Send to both customer and provider
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [booking.customer.email, booking.provider.email],
            fail_silently=True,
        )
        
    except Booking.DoesNotExist:
        pass


@shared_task
def send_booking_reminders():
    """
    Send reminders for bookings scheduled tomorrow
    """
    from apps.bookings.models import Booking
    
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    bookings = Booking.objects.filter(
        scheduled_date=tomorrow,
        status__in=['CONFIRMED', 'PENDING']
    ).select_related('customer', 'provider', 'service')
    
    for booking in bookings:
        # Reminder to customer
        subject = f'Booking Reminder: {booking.service.title}'
        message = f"""
        This is a reminder for your upcoming booking.
        
        Service: {booking.service.title}
        Provider: {booking.provider.full_name}
        Date: {booking.scheduled_date}
        Time: {booking.scheduled_time}
        Address: {booking.service_address}
        
        See you tomorrow!
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [booking.customer.email],
            fail_silently=True,
        )
        
        # Reminder to provider
        send_mail(
            f'Booking Reminder: {booking.booking_reference}',
            f"""
            Reminder: You have a booking scheduled tomorrow.
            
            Booking Reference: {booking.booking_reference}
            Customer: {booking.customer.full_name}
            Service: {booking.service.title}
            Date: {booking.scheduled_date}
            Time: {booking.scheduled_time}
            """,
            settings.EMAIL_HOST_USER,
            [booking.provider.email],
            fail_silently=True,
        )


@shared_task
def auto_complete_bookings():
    """
    Automatically mark bookings as completed after scheduled time + duration
    """
    from apps.bookings.models import Booking, BookingStatusHistory
    
    # Find bookings that should be completed
    cutoff_time = timezone.now() - timedelta(hours=2)
    
    bookings = Booking.objects.filter(
        status='IN_PROGRESS',
        actual_start_time__lte=cutoff_time
    )
    
    for booking in bookings:
        booking.status = 'COMPLETED'
        booking.completed_at = timezone.now()
        booking.actual_end_time = timezone.now()
        booking.save()
        
        # Create history entry
        BookingStatusHistory.objects.create(
            booking=booking,
            from_status='IN_PROGRESS',
            to_status='COMPLETED',
            notes='Auto-completed by system'
        )