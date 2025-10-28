"""
Custom exception handlers
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize error response format
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'status_code': response.status_code,
            }
        }
        
        # Add validation errors if present
        if isinstance(exc, ValidationError):
            custom_response_data['error']['validation_errors'] = response.data
        else:
            custom_response_data['error']['details'] = response.data
        
        response.data = custom_response_data
        
        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            extra={'context': context}
        )
    
    return response