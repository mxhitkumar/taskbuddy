"""
Cache utilities and decorators
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def cache_key_generator(*args, **kwargs):
    """
    Generate cache key from arguments
    """
    key_data = f"{args}:{kwargs}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cached_view(timeout=300, key_prefix='view'):
    """
    Decorator to cache view results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{request.path}:{request.GET.urlencode()}"
            
            # Try to get from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Execute view
            response = func(request, *args, **kwargs)
            
            # Cache the response
            cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def invalidate_cache(key_pattern):
    """
    Invalidate cache keys matching pattern
    """
    # Note: This requires Redis with key pattern support
    try:
        cache.delete_pattern(key_pattern)
    except AttributeError:
        # If delete_pattern not available, clear all cache
        cache.clear()


class CacheManager:
    """
    Centralized cache management
    """
    
    @staticmethod
    def get_or_set(key, callback, timeout=300):
        """
        Get from cache or set using callback
        """
        data = cache.get(key)
        if data is None:
            data = callback()
            cache.set(key, data, timeout)
        return data
    
    @staticmethod
    def invalidate(key):
        """
        Invalidate specific cache key
        """
        cache.delete(key)
    
    @staticmethod
    def invalidate_pattern(pattern):
        """
        Invalidate cache keys matching pattern
        """
        invalidate_cache(pattern)