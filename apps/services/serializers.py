"""
Service Serializers
"""
from rest_framework import serializers
from services.models import (
    ServiceCategory, Service, ServiceImage, 
    ServiceAvailability, ServiceArea
)
from users.serializers import UserSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories"""
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 
            'parent', 'order', 'is_active', 'service_count',
            'provider_count', 'subcategories'
        ]
        read_only_fields = ['service_count', 'provider_count']
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return ServiceCategorySerializer(
                obj.subcategories.filter(is_active=True),
                many=True
            ).data
        return []


class ServiceImageSerializer(serializers.ModelSerializer):
    """Serializer for service images"""
    
    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'caption', 'order', 'created_at']


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for service listings"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    pricing_type_display = serializers.CharField(
        source='get_pricing_type_display',
        read_only=True
    )
    
    class Meta:
        model = Service
        fields = [
            'id', 'slug', 'title', 'short_description', 'thumbnail',
            'category', 'category_name', 'provider', 'provider_name',
            'pricing_type', 'pricing_type_display', 'base_price', 'currency',
            'duration_minutes', 'is_featured', 'average_rating',
            'review_count', 'booking_count', 'created_at'
        ]


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for service detail view"""
    category = ServiceCategorySerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    images = ServiceImageSerializer(many=True, read_only=True)
    pricing_type_display = serializers.CharField(
        source='get_pricing_type_display',
        read_only=True
    )
    
    class Meta:
        model = Service
        fields = [
            'id', 'slug', 'title', 'description', 'short_description',
            'thumbnail', 'images', 'category', 'provider',
            'pricing_type', 'pricing_type_display', 'base_price', 'currency',
            'duration_minutes', 'is_active', 'is_featured',
            'view_count', 'booking_count', 'average_rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'updated_at'
        ]


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating services"""
    images = ServiceImageSerializer(many=True, required=False, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Service
        fields = [
            'title', 'slug', 'description', 'short_description',
            'category', 'pricing_type', 'base_price', 'currency',
            'duration_minutes', 'thumbnail', 'is_active',
            'meta_title', 'meta_description', 'images', 'uploaded_images'
        ]
    
    def validate_slug(self, value):
        """Ensure slug is unique"""
        instance = self.instance
        if instance:
            if Service.objects.exclude(pk=instance.pk).filter(slug=value).exists():
                raise serializers.ValidationError("Service with this slug already exists.")
        else:
            if Service.objects.filter(slug=value).exists():
                raise serializers.ValidationError("Service with this slug already exists.")
        return value
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        provider = self.context['request'].user
        
        service = Service.objects.create(provider=provider, **validated_data)
        
        # Create service images
        for index, image in enumerate(uploaded_images):
            ServiceImage.objects.create(
                service=service,
                image=image,
                order=index
            )
        
        return service
    
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images
        if uploaded_images:
            current_max_order = instance.images.count()
            for index, image in enumerate(uploaded_images):
                ServiceImage.objects.create(
                    service=instance,
                    image=image,
                    order=current_max_order + index
                )
        
        return instance


class ServiceAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for service provider availability"""
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )
    
    class Meta:
        model = ServiceAvailability
        fields = [
            'id', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'is_available'
        ]
    
    def validate(self, attrs):
        """Ensure start_time is before end_time"""
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError(
                "Start time must be before end time."
            )
        return attrs


class ServiceAreaSerializer(serializers.ModelSerializer):
    """Serializer for service areas"""
    
    class Meta:
        model = ServiceArea
        fields = [
            'id', 'city', 'state', 'postal_code',
            'service_radius_km', 'is_active'
        ]