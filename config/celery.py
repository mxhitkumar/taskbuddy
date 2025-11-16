"""
Celery configuration for async task processing
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('marketplace')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    # Clean expired OTPs every hour
    'clean-expired-otps': {
        'task': 'users.tasks.clean_expired_otps',
        'schedule': crontab(minute=0),  # Every hour
    },
    # Send booking reminders
    'send-booking-reminders': {
        'task': 'bookings.tasks.send_booking_reminders',
        'schedule': crontab(hour=8, minute=0),  # Every day at 8 AM
    },
    # Update service statistics
    'update-service-stats': {
        'task': 'services.tasks.update_service_statistics',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')