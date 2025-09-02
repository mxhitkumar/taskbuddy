from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_provider_verification_email(user_id, approved=True):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        u = User.objects.get(id=user_id)
        subject = "Verification Approved" if approved else "Verification Rejected"
        message = f"Hello {u.username}, your verification status: {'Approved' if approved else 'Rejected'}"
        if u.email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [u.email])
        return True
    except User.DoesNotExist:
        return False
