"""
Review Serializers
"""
from rest_framework import serializers
from apps.reviews.models import Review, ReviewResponse, ReviewImage, ReviewHelpful
from apps.bookings.models import Booking


class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for review images"""
    
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'caption', 'order']


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for review responses"""
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = [
            'id', 'provider', 'provider_name', 'response_text',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['provider']


class ReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review listings"""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)
    has_response = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'customer', 'customer_name',
            'provider', 'provider_name', 'service', 'service_title',
            'rating', 'title', 'comment', 'is_verified',
            'helpful_count', 'has_response', 'created_at'
        ]
    
    def get_has_response(self, obj):
        return hasattr(obj, 'response')


class ReviewDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for review detail view"""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_avatar = serializers.ImageField(
        source='customer.profile.avatar',
        read_only=True
    )
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    response = ReviewResponseSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'customer', 'customer_name', 'customer_avatar',
            'provider', 'provider_name', 'service', 'service_title',
            'rating', 'title', 'comment', 'quality_rating',
            'punctuality_rating', 'professionalism_rating', 'value_rating',
            'is_verified', 'is_featured', 'helpful_count',
            'images', 'response', 'created_at', 'updated_at'
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    images = ReviewImageSerializer(many=True, required=False, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Review
        fields = [
            'booking', 'rating', 'title', 'comment',
            'quality_rating', 'punctuality_rating',
            'professionalism_rating', 'value_rating',
            'images', 'uploaded_images'
        ]
    
    def validate_booking(self, value):
        """Validate booking eligibility for review"""
        request = self.context['request']
        
        # Check if booking belongs to customer
        if value.customer != request.user:
            raise serializers.ValidationError(
                "You can only review your own bookings."
            )
        
        # Check if booking is completed
        if value.status != Booking.BookingStatus.COMPLETED:
            raise serializers.ValidationError(
                "Can only review completed bookings."
            )
        
        # Check if review already exists
        if Review.objects.filter(booking=value, customer=request.user).exists():
            raise serializers.ValidationError(
                "You have already reviewed this booking."
            )
        
        return value
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        request = self.context['request']
        booking = validated_data['booking']
        
        review = Review.objects.create(
            customer=request.user,
            provider=booking.provider,
            service=booking.service,
            **validated_data
        )
        
        # Create review images
        for index, image in enumerate(uploaded_images):
            ReviewImage.objects.create(
                review=review,
                image=image,
                order=index
            )
        
        return review


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reviews"""
    
    class Meta:
        model = Review
        fields = [
            'rating', 'title', 'comment', 'quality_rating',
            'punctuality_rating', 'professionalism_rating', 'value_rating'
        ]


class ReviewResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating review responses"""
    
    class Meta:
        model = ReviewResponse
        fields = ['response_text']
    
    def validate(self, attrs):
        """Validate review response eligibility"""
        review = self.context['review']
        request = self.context['request']
        
        # Check if user is the provider
        if review.provider != request.user:
            raise serializers.ValidationError(
                "Only the service provider can respond to this review."
            )
        
        # Check if response already exists
        if hasattr(review, 'response'):
            raise serializers.ValidationError(
                "You have already responded to this review."
            )
        
        return attrs
    
    def create(self, validated_data):
        review = self.context['review']
        request = self.context['request']
        
        return ReviewResponse.objects.create(
            review=review,
            provider=request.user,
            **validated_data
        )


class ReviewHelpfulSerializer(serializers.Serializer):
    """Serializer for marking review as helpful"""
    helpful = serializers.BooleanField()