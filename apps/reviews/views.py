"""
Review Views
"""
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg

from apps.reviews.models import Review, ReviewResponse, ReviewHelpful
from apps.reviews.serializers import (
    ReviewListSerializer, ReviewDetailSerializer,
    ReviewCreateSerializer, ReviewUpdateSerializer,
    ReviewResponseCreateSerializer, ReviewHelpfulSerializer
)
from apps.users.permissions import IsCustomer, IsServiceProvider, IsOwnerOrAdmin


class ReviewCreateView(generics.CreateAPIView):
    """
    Create a review (Customer only, for completed bookings)
    POST /api/reviews/create/
    """
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = ReviewCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        # Update provider and service ratings
        from apps.reviews.tasks import update_ratings
        update_ratings.delay(review.provider.id, review.service.id)
        
        return Response(
            ReviewDetailSerializer(review).data,
            status=status.HTTP_201_CREATED
        )


class ReviewListView(generics.ListAPIView):
    """
    List reviews with filtering
    GET /api/reviews/
    """
    permission_classes = [AllowAny]
    serializer_class = ReviewListSerializer
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_active=True)
        
        # Filter by provider
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Filter by service
        service_id = self.request.query_params.get('service')
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        
        # Order by
        order = self.request.query_params.get('order', '-created_at')
        if order == 'helpful':
            queryset = queryset.order_by('-helpful_count', '-created_at')
        elif order == 'rating_high':
            queryset = queryset.order_by('-rating', '-created_at')
        elif order == 'rating_low':
            queryset = queryset.order_by('rating', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset.select_related(
            'customer', 'customer__profile', 'provider', 'service'
        )


class ReviewDetailView(generics.RetrieveAPIView):
    """
    Get review details
    GET /api/reviews/{id}/
    """
    permission_classes = [AllowAny]
    serializer_class = ReviewDetailSerializer
    queryset = Review.objects.filter(is_active=True)


class ReviewUpdateView(generics.UpdateAPIView):
    """
    Update review (Customer only, own reviews)
    PUT /api/reviews/{id}/update/
    """
    permission_classes = [IsAuthenticated, IsCustomer, IsOwnerOrAdmin]
    serializer_class = ReviewUpdateSerializer
    
    def get_queryset(self):
        return Review.objects.filter(customer=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    """
    Delete review (soft delete)
    DELETE /api/reviews/{id}/delete/
    """
    permission_classes = [IsAuthenticated, IsCustomer, IsOwnerOrAdmin]
    
    def get_queryset(self):
        return Review.objects.filter(customer=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()
        
        # Update ratings
        from apps.reviews.tasks import update_ratings
        update_ratings.delay(instance.provider.id, instance.service.id)


class MyReviewsView(generics.ListAPIView):
    """
    Get customer's own reviews
    GET /api/reviews/my-reviews/
    """
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = ReviewListSerializer
    
    def get_queryset(self):
        return Review.objects.filter(
            customer=self.request.user
        ).select_related(
            'provider', 'service', 'booking'
        ).order_by('-created_at')


class ProviderReviewsView(generics.ListAPIView):
    """
    Get reviews for a provider
    GET /api/reviews/provider/{provider_id}/
    """
    permission_classes = [AllowAny]
    serializer_class = ReviewListSerializer
    
    def get_queryset(self):
        provider_id = self.kwargs['provider_id']
        return Review.objects.filter(
            provider_id=provider_id,
            is_active=True
        ).select_related(
            'customer', 'customer__profile', 'service'
        ).order_by('-created_at')


class ServiceReviewsView(generics.ListAPIView):
    """
    Get reviews for a service
    GET /api/reviews/service/{service_id}/
    """
    permission_classes = [AllowAny]
    serializer_class = ReviewListSerializer
    
    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return Review.objects.filter(
            service_id=service_id,
            is_active=True
        ).select_related(
            'customer', 'customer__profile', 'provider'
        ).order_by('-created_at')


class ReviewResponseCreateView(views.APIView):
    """
    Create a response to a review (Provider only)
    POST /api/reviews/{review_id}/respond/
    """
    permission_classes = [IsAuthenticated, IsServiceProvider]
    
    def post(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id, is_active=True)
        except Review.DoesNotExist:
            return Response(
                {'error': 'Review not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ReviewResponseCreateSerializer(
            data=request.data,
            context={'review': review, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        
        return Response(
            ReviewResponseSerializer(response).data,
            status=status.HTTP_201_CREATED
        )


class ReviewHelpfulView(views.APIView):
    """
    Mark review as helpful/unhelpful
    POST /api/reviews/{review_id}/helpful/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id, is_active=True)
        except Review.DoesNotExist:
            return Response(
                {'error': 'Review not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ReviewHelpfulSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        helpful = serializer.validated_data['helpful']
        
        if helpful:
            # Add helpful vote
            obj, created = ReviewHelpful.objects.get_or_create(
                review=review,
                user=request.user
            )
            if created:
                review.helpful_count += 1
                review.save(update_fields=['helpful_count'])
                message = 'Marked as helpful'
            else:
                message = 'Already marked as helpful'
        else:
            # Remove helpful vote
            deleted = ReviewHelpful.objects.filter(
                review=review,
                user=request.user
            ).delete()[0]
            
            if deleted:
                review.helpful_count = max(0, review.helpful_count - 1)
                review.save(update_fields=['helpful_count'])
                message = 'Removed helpful mark'
            else:
                message = 'Not marked as helpful'
        
        return Response({
            'message': message,
            'helpful_count': review.helpful_count
        })


class ReviewStatsView(views.APIView):
    """
    Get review statistics for a provider or service
    GET /api/reviews/stats/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        provider_id = request.query_params.get('provider')
        service_id = request.query_params.get('service')
        
        if not provider_id and not service_id:
            return Response(
                {'error': 'Provider or service ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Review.objects.filter(is_active=True)
        
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        
        # Calculate statistics
        stats = queryset.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            average_quality=Avg('quality_rating'),
            average_punctuality=Avg('punctuality_rating'),
            average_professionalism=Avg('professionalism_rating'),
            average_value=Avg('value_rating')
        )
        
        # Rating distribution
        from django.db.models import Count
        rating_distribution = {}
        for i in range(1, 6):
            count = queryset.filter(rating=i).count()
            rating_distribution[f'{i}_star'] = count
        
        stats['rating_distribution'] = rating_distribution
        
        return Response(stats)