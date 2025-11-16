"""
Booking Serializers
"""
from rest_framework import serializers
from django.utils import timezone
from bookings.models import Booking, BookingStatusHistory, BookingAttachment
from services.serializers import ServiceListSerializer
from users.serializers import UserSerializer


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for booking listings"""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'status', 'status_display',
            'customer', 'customer_name', 'provider', 'provider_name',
            'service', 'service_title', 'scheduled_date', 'scheduled_time',
            'total_amount', 'currency', 'created_at'
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for booking detail view"""
    customer = UserSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    service = ServiceListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'customer', 'provider', 'service',
            'status', 'status_display', 'scheduled_date', 'scheduled_time',
            'estimated_duration_minutes', 'actual_start_time', 'actual_end_time',
            'service_address', 'service_city', 'service_state', 'service_postal_code',
            'latitude', 'longitude', 'base_price', 'additional_charges',
            'discount_amount', 'tax_amount', 'total_amount', 'currency',
            'customer_notes', 'provider_notes', 'cancellation_reason',
            'confirmed_at', 'completed_at', 'cancelled_at',
            'created_at', 'updated_at'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'service', 'scheduled_date', 'scheduled_time',
            'estimated_duration_minutes', 'service_address',
            'service_city', 'service_state', 'service_postal_code',
            'latitude', 'longitude', 'customer_notes'
        ]
    
    def validate_scheduled_date(self, value):
        """Ensure booking is for future date"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot book for past dates.")
        return value
    
    def validate(self, attrs):
        """Additional validation"""
        service = attrs['service']
        
        # Check if service is active
        if not service.is_active:
            raise serializers.ValidationError(
                {"service": "This service is not currently available."}
            )
        
        # Check if provider is available
        if not service.provider.provider_profile.is_available:
            raise serializers.ValidationError(
                {"service": "This provider is not currently accepting bookings."}
            )
        
        return attrs
    
    def create(self, validated_data):
        request = self.context['request']
        service = validated_data['service']
        
        # Set customer and provider
        booking = Booking(
            customer=request.user,
            provider=service.provider,
            base_price=service.base_price,
            currency=service.currency,
            **validated_data
        )
        
        # Calculate tax (example: 10%)
        booking.tax_amount = booking.base_price * 0.10
        
        booking.save()
        
        # Create status history
        BookingStatusHistory.objects.create(
            booking=booking,
            from_status='',
            to_status=booking.status,
            changed_by=request.user,
            notes='Booking created'
        )
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking details"""
    
    class Meta:
        model = Booking
        fields = [
            'scheduled_date', 'scheduled_time', 'service_address',
            'service_city', 'service_state', 'service_postal_code',
            'customer_notes'
        ]
    
    def validate(self, attrs):
        """Only allow updates for pending/confirmed bookings"""
        if self.instance.status not in [
            Booking.BookingStatus.PENDING,
            Booking.BookingStatus.CONFIRMED
        ]:
            raise serializers.ValidationError(
                "Cannot update booking in current status."
            )
        return attrs


class BookingStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating booking status"""
    status = serializers.ChoiceField(choices=Booking.BookingStatus.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate status transitions"""
        booking = self.context['booking']
        new_status = attrs['status']
        
        # Define allowed transitions
        allowed_transitions = {
            Booking.BookingStatus.PENDING: [
                Booking.BookingStatus.CONFIRMED,
                Booking.BookingStatus.CANCELLED
            ],
            Booking.BookingStatus.CONFIRMED: [
                Booking.BookingStatus.IN_PROGRESS,
                Booking.BookingStatus.CANCELLED
            ],
            Booking.BookingStatus.IN_PROGRESS: [
                Booking.BookingStatus.COMPLETED,
                Booking.BookingStatus.CANCELLED
            ],
            Booking.BookingStatus.COMPLETED: [],
            Booking.BookingStatus.CANCELLED: [Booking.BookingStatus.REFUNDED],
        }
        
        if new_status not in allowed_transitions.get(booking.status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {booking.status} to {new_status}"
            )
        
        # Require cancellation reason for cancelled status
        if new_status == Booking.BookingStatus.CANCELLED:
            if not attrs.get('cancellation_reason'):
                raise serializers.ValidationError(
                    {"cancellation_reason": "Cancellation reason is required."}
                )
        
        return attrs


class BookingAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for booking attachments"""
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.full_name',
        read_only=True
    )
    attachment_type_display = serializers.CharField(
        source='get_attachment_type_display',
        read_only=True
    )
    
    class Meta:
        model = BookingAttachment
        fields = [
            'id', 'attachment_type', 'attachment_type_display',
            'file', 'description', 'uploaded_by', 'uploaded_by_name',
            'created_at'
        ]
        read_only_fields = ['uploaded_by']


class BookingStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for booking status history"""
    changed_by_name = serializers.CharField(
        source='changed_by.full_name',
        read_only=True
    )
    
    class Meta:
        model = BookingStatusHistory
        fields = [
            'id', 'from_status', 'to_status', 'changed_by',
            'changed_by_name', 'notes', 'created_at'
        ]