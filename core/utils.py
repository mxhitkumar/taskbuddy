"""
Core utility functions
"""
import random
import string
from django.utils.text import slugify
from datetime import datetime


def generate_unique_slug(model_class, text, field_name='slug'):
    """
    Generate a unique slug for a model instance
    """
    slug = slugify(text)
    unique_slug = slug
    num = 1
    
    while model_class.objects.filter(**{field_name: unique_slug}).exists():
        unique_slug = f'{slug}-{num}'
        num += 1
    
    return unique_slug


def generate_random_code(length=6, chars=string.digits):
    """
    Generate random code (for OTP, etc.)
    """
    return ''.join(random.choice(chars) for _ in range(length))


def generate_booking_reference():
    """
    Generate unique booking reference
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'BK{timestamp}{random_part}'


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula
    Returns distance in kilometers
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Convert to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def format_price(amount, currency='USD'):
    """
    Format price with currency symbol
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
    }
    symbol = symbols.get(currency, currency)
    return f'{symbol}{amount:.2f}'


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sanitize_filename(filename):
    """
    Sanitize uploaded filename
    """
    import re
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename


def time_ago(dt):
    """
    Convert datetime to human-readable time ago format
    """
    from django.utils import timezone
    
    now = timezone.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f'{weeks} week{"s" if weeks > 1 else ""} ago'
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f'{months} month{"s" if months > 1 else ""} ago'
    else:
        years = int(seconds / 31536000)
        return f'{years} year{"s" if years > 1 else ""} ago'