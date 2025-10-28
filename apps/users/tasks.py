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
    from apps.users.models import OTPVerification
    
    expired_time = timezone.now()
    deleted_count = OTPVerification.objects.filter(
        expires_at__lt=expired_time,
        is_used=False
    ).delete()[0]
    
    return f"Deleted {deleted_count} expired OTPs"


@shared_task
def send_welcome_email(user_id):
    """
    Send welcome email to new users
    """
    from apps.users.models import User
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to Service Marketplace!'
        message = f"""
        Hi {user.first_name},
        
        Welcome to our Service Marketplace platform!
        
        Your account has been created successfully.
        Role: {user.get_role_display()}
        
        Please verify your email address to get started.
        
        Best regards,
        Service Marketplace Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=True,
        )
        
    except User.DoesNotExist:
        pass


@shared_task
def send_verification_email(user_id, otp_code):
    """
    Send email verification OTP
    """
    from apps.users.models import User
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Email Verification - Service Marketplace'
        message = f"""
        Hi {user.first_name},
        
        Your email verification code is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Service Marketplace Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=True,
        )
        
    except User.DoesNotExist:
        pass