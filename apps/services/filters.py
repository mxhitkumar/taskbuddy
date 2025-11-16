"""
Django filters for Service queries
"""
import django_filters
from services.models import Service


class ServiceFilter(django_filters.FilterSet):
    """
    Filter for service listings
    """
    category = django_filters.NumberFilter(field_name='category__id')
    min_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')
    city = django_filters.CharFilter(field_name='provider__profile__city', lookup_expr='iexact')
    state = django_filters.CharFilter(field_name='provider__profile__state', lookup_expr='iexact')
    pricing_type = django_filters.ChoiceFilter(choices=Service.PricingType.choices)
    is_featured = django_filters.BooleanFilter()
    
    class Meta:
        model = Service
        fields = [
            'category', 'min_price', 'max_price', 'min_rating',
            'city', 'state', 'pricing_type', 'is_featured'
        ]