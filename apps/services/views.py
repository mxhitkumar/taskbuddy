"""
Service Views
"""
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.db.models import Q, Count, Avg

from apps.services.models import (
    ServiceCategory, Service, ServiceAvailability, ServiceArea
)
from apps.services.serializers import (
    ServiceCategorySerializer, ServiceListSerializer,
    ServiceDetailSerializer, ServiceCreateUpdateSerializer,
    ServiceAvailabilitySerializer, ServiceAreaSerializer
)
from apps.services.filters import ServiceFilter
from apps.users.permissions import IsServiceProvider, IsOwnerOrAdmin


class ServiceCategoryListView(generics.ListAPIView):
    """
    List all service categories
    GET /api/services/categories/
    """
    permission_classes = [AllowAny]
    serializer_class = ServiceCategorySerializer
    queryset = ServiceCategory.objects.filter(is_active=True)
    
    def get_queryset(self):
        # Cache categories
        cache_key = 'service_categories_all'
        categories = cache.get(cache_key)
        
        if not categories:
            categories = list(
                ServiceCategory.objects.filter(
                    is_active=True,
                    parent__isnull=True
                ).prefetch_related('subcategories')
            )
            cache.set(cache_key, categories, 3600)  # Cache for 1 hour
        
        return categories


class ServiceListView(generics.ListAPIView):
    """
    List all services with filtering
    GET /api/services/
    """
    permission_classes = [AllowAny]
    serializer_class = ServiceListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['title', 'description', 'provider__first_name', 'provider__last_name']
    ordering_fields = ['created_at', 'average_rating', 'base_price', 'booking_count']
    ordering = ['-is_featured', '-average_rating']
    
    def get_queryset(self):
        queryset = Service.objects.filter(
            is_active=True
        ).select_related(
            'category', 'provider', 'provider__profile', 'provider__provider_profile'
        )
        
        # Filter by verified providers only
        verified_only = self.request.query_params.get('verified_only', 'false')
        if verified_only.lower() == 'true':
            queryset = queryset.filter(
                provider__is_verified=True,
                provider__provider_profile__verification_status='VERIFIED',
                provider__provider_profile__is_available=True
            )
        
        return queryset


class ServiceDetailView(generics.RetrieveAPIView):
    """
    Get service details
    GET /api/services/{slug}/
    """
    permission_classes = [AllowAny]
    serializer_class = ServiceDetailSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Service.objects.filter(
            is_active=True
        ).select_related(
            'category', 'provider', 'provider__profile', 'provider__provider_profile'
        ).prefetch_related('images')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count asynchronously
        from apps.services.tasks import increment_service_views
        increment_service_views.delay(instance.id)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ServiceCreateView(generics.CreateAPIView):
    """
    Create a new service (Provider only)
    POST /api/services/create/
    """
    permission_classes = [IsAuthenticated, IsServiceProvider]
    serializer_class = ServiceCreateUpdateSerializer
    
    def perform_create(self, serializer):
        serializer.save()


class ServiceUpdateView(generics.UpdateAPIView):
    """
    Update service (Provider only - own services)
    PUT /api/services/{slug}/update/
    """
    permission_classes = [IsAuthenticated, IsServiceProvider, IsOwnerOrAdmin]
    serializer_class = ServiceCreateUpdateSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Service.objects.filter(provider=self.request.user)


class ServiceDeleteView(generics.DestroyAPIView):
    """
    Delete service (soft delete by setting is_active=False)
    DELETE /api/services/{slug}/delete/
    """
    permission_classes = [IsAuthenticated, IsServiceProvider, IsOwnerOrAdmin]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Service.objects.filter(provider=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


class MyServicesView(generics.ListAPIView):
    """
    List provider's own services
    GET /api/services/my-services/
    """
    permission_classes = [IsAuthenticated, IsServiceProvider]
    serializer_class = ServiceListSerializer
    
    def get_queryset(self):
        return Service.objects.filter(
            provider=self.request.user
        ).select_related('category').order_by('-created_at')


class ServiceAvailabilityView(generics.ListCreateAPIView):
    """
    Manage service provider availability
    GET/POST /api/services/availability/
    """
    permission_classes = [IsAuthenticated, IsServiceProvider]
    serializer_class = ServiceAvailabilitySerializer
    
    def get_queryset(self):
        return ServiceAvailability.objects.filter(
            provider=self.request.user
        ).order_by('day_of_week', 'start_time')
    
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class ServiceAreaView(generics.ListCreateAPIView):
    """
    Manage service areas
    GET/POST /api/services/areas/
    """
    permission_classes = [IsAuthenticated, IsServiceProvider]
    serializer_class = ServiceAreaSerializer
    
    def get_queryset(self):
        return ServiceArea.objects.filter(
            provider=self.request.user
        ).order_by('city')
    
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class FeaturedServicesView(generics.ListAPIView):
    """
    Get featured services
    GET /api/services/featured/
    """
    permission_classes = [AllowAny]
    serializer_class = ServiceListSerializer
    
    def get_queryset(self):
        # Cache featured services
        cache_key = 'featured_services'
        services = cache.get(cache_key)
        
        if not services:
            services = list(
                Service.objects.filter(
                    is_active=True,
                    is_featured=True
                ).select_related(
                    'category', 'provider'
                ).order_by('-average_rating')[:10]
            )
            cache.set(cache_key, services, 1800)  # Cache for 30 minutes
        
        return services


class PopularServicesView(generics.ListAPIView):
    """
    Get popular services (most bookings)
    GET /api/services/popular/
    """
    permission_classes = [AllowAny]
    serializer_class = ServiceListSerializer
    
    def get_queryset(self):
        return Service.objects.filter(
            is_active=True
        ).select_related(
            'category', 'provider'
        ).order_by('-booking_count', '-average_rating')[:20]