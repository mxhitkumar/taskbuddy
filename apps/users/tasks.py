"""
Celery tasks for user management
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def clean_expired_otps():
    """
    Clean up expired OTP verification codes
    """
    from users.models import EmailOTP
    
    # Mark as expired
    expired_time = timezone.now()
    updated_count = EmailOTP.objects.filter(
        expires_at__lt=expired_time,
        is_used=False,
        is_expired=False
    ).update(is_expired=True)
    
    # Delete old OTPs (older than 30 days)
    delete_time = timezone.now() - timedelta(days=30)
    deleted_count = EmailOTP.objects.filter(
        created_at__lt=delete_time
    ).delete()[0]
    
    return f"Marked {updated_count} OTPs as expired, Deleted {deleted_count} old OTPs"


@shared_task
def send_welcome_email_async(user_id):
    """
    Send welcome email to new users
    """
    from users.models import User
    from core.email_utils import EmailService
    
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_welcome_email(user)
        return f"Welcome email sent to {user.email}"
    except User.DoesNotExist:
        return "User not found"


@shared_task
def send_verification_email_async(user_id, otp_code):
    """
    Send email verification OTP
    """
    from users.models import User
    from core.email_utils import EmailService
    
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_otp_email(user, otp_code, 'EMAIL_VERIFICATION')
        return f"Verification email sent to {user.email}"
    except User.DoesNotExist:
        return "User not found"


@shared_task
def send_password_reset_email_async(user_id, otp_code):
    """
    Send password reset OTP
    """
    from users.models import User
    from core.email_utils import EmailService
    
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_otp_email(user, otp_code, 'PASSWORD_RESET')
        return f"Password reset email sent to {user.email}"
    except User.DoesNotExist:
        return "User not found"


@shared_task
def check_unverified_users():
    """
    Send reminder emails to unverified users after 24 hours
    """
    from users.models import User
    from core.email_utils import EmailService
    
    # Find users who registered more than 24 hours ago but haven't verified
    cutoff_time = timezone.now() - timedelta(hours=24)
    unverified_users = User.objects.filter(
        is_email_verified=False,
        is_active=True,
        created_at__lte=cutoff_time,
        created_at__gte=timezone.now() - timedelta(days=7)  # Within last 7 days
    )
    
    count = 0
    for user in unverified_users:
        # Check if reminder already sent
        cache_key = f'verification_reminder_{user.id}'
        from django.core.cache import cache
        
        if not cache.get(cache_key):
            EmailService.send_otp_email(user, None, 'EMAIL_VERIFICATION')
            cache.set(cache_key, True, 86400 * 7)  # Don't remind again for 7 days
            count += 1
    
    return f"Sent {count} verification reminders"