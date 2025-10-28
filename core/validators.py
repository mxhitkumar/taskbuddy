"""
Custom validators
"""
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re


def validate_phone_number(value):
    """
    Validate phone number format
    """
    pattern = re.compile(r'^\+?1?\d{9,15}$')
    if not pattern.match(value):
        raise ValidationError(
            'Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )


def validate_file_size(value, max_size_mb=10):
    """
    Validate file size
    """
    filesize = value.size
    if filesize > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Maximum file size is {max_size_mb}MB')


def validate_image_file(value):
    """
    Validate image file type
    """
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if ext.lower() not in valid_extensions:
        raise ValidationError(f'Unsupported file extension. Allowed: {", ".join(valid_extensions)}')


def validate_rating(value):
    """
    Validate rating value (1-5)
    """
    if value < 1 or value > 5:
        raise ValidationError('Rating must be between 1 and 5')


phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


postal_code_regex = RegexValidator(
    regex=r'^\d{5}(-\d{4})?$',
    message="Postal code must be in format: '12345' or '12345-6789'"
)