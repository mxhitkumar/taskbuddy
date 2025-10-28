"""
Booking Views
"""
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from apps.bookings.models import Booking, BookingStatusHistory, BookingAttachment
from apps.bookings.serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer, BookingUpdateSerializer,
    BookingStatusUpdateSerializer, BookingAttachmentSerializer,
    BookingStatusHistorySerializer
)
from apps.users.permissions import IsCustomer, IsServiceProvider, IsOwnerOrAdmin


class BookingCreateView(generics.CreateAPIView):
    """
    Create a new booking (Customer only)
    POST /api/bookings/create/
    """
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = BookingCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Trigger async task for notification
        from apps.bookings.tasks import send_booking_notification
        send_booking_notification.delay(booking.id)
        
        return Response(
            BookingDetailSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )


class BookingListView(generics.ListAPIView):
    """
    List bookings
    GET /api/bookings/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingListSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'CUSTOMER':
            queryset = Booking.objects.filter(customer=user)
        elif user.role == 'SERVICE_PROVIDER':
            queryset = Booking.objects.filter(provider=user)
        else:
            # Admin can see all bookings
            queryset = Booking.objects.all()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(scheduled_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_date__lte=end_date)
        
        return queryset.select_related(
            'customer', 'provider', 'service'
        ).order_by('-created_at')


class BookingDetailView(generics.RetrieveAPIView):
    """
    Get booking details
    GET /api/bookings/{booking_reference}/
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = BookingDetailSerializer
    lookup_field = 'booking_reference'
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'CUSTOMER':
            return Booking.objects.filter(customer=user)
        elif user.role == 'SERVICE_PROVIDER':
            return Booking.objects.filter(provider=user)
        else:
            return Booking.objects.all()


class BookingUpdateView(generics.UpdateAPIView):
    """
    Update booking details (Customer only, before confirmation)
    PUT /api/bookings/{booking_reference}/update/
    """
    permission_classes = [IsAuthenticated, IsCustomer, IsOwnerOrAdmin]
    serializer_class = BookingUpdateSerializer
    lookup_field = 'booking_reference'
    
    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user)


class BookingStatusUpdateView(views.APIView):
    """
    Update booking status
    POST /api/bookings/{booking_reference}/status/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, booking_reference):
        try:
            booking = Booking.objects.get(booking_reference=booking_reference)
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        if user.role == 'CUSTOMER' and booking.customer != user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        elif user.role == 'SERVICE_PROVIDER' and booking.provider != user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BookingStatusUpdateSerializer(
            data=request.data,
            context={'booking': booking}
        )
        serializer.is_valid(raise_exception=True)
        
        old_status = booking.status
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        # Update booking status
        booking.status = new_status
        
        if new_status == Booking.BookingStatus.CONFIRMED:
            booking.confirmed_at = timezone.now()
        elif new_status == Booking.BookingStatus.COMPLETED:
            booking.completed_at = timezone.now()
            if not booking.actual_end_time:
                booking.actual_end_time = timezone.now()
        elif new_status == Booking.BookingStatus.CANCELLED:
            booking.cancelled_at = timezone.now()
            booking.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')
        elif new_status == Booking.BookingStatus.IN_PROGRESS:
            if not booking.actual_start_time:
                booking.actual_start_time = timezone.now()
        
        booking.save()
        
        # Create status history
        BookingStatusHistory.objects.create(
            booking=booking,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            notes=notes
        )
        
        # Send notification
        from apps.bookings.tasks import send_status_update_notification
        send_status_update_notification.delay(booking.id, old_status, new_status)
        
        return Response(BookingDetailSerializer(booking).data)


class BookingCancelView(views.APIView):
    """
    Cancel booking
    POST /api/bookings/{booking_reference}/cancel/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, booking_reference):
        try:
            booking = Booking.objects.get(booking_reference=booking_reference)
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        if booking.customer != user and booking.provider != user:
            if user.role not in ['SUPERADMIN', 'ADMIN']:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if can cancel
        if not booking.can_cancel():
            return Response(
                {'error': 'Booking cannot be cancelled in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cancellation_reason = request.data.get('cancellation_reason', '')
        if not cancellation_reason:
            return Response(
                {'error': 'Cancellation reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = booking.status
        booking.status = Booking.BookingStatus.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = cancellation_reason
        booking.save()
        
        # Create status history
        BookingStatusHistory.objects.create(
            booking=booking,
            from_status=old_status,
            to_status=Booking.BookingStatus.CANCELLED,
            changed_by=user,
            notes=f"Cancelled by {user.get_role_display()}"
        )
        
        return Response(BookingDetailSerializer(booking).data)


class BookingAttachmentView(generics.ListCreateAPIView):
    """
    Manage booking attachments
    GET/POST /api/bookings/{booking_reference}/attachments/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingAttachmentSerializer
    
    def get_queryset(self):
        booking_reference = self.kwargs['booking_reference']
        return BookingAttachment.objects.filter(
            booking__booking_reference=booking_reference
        )
    
    def perform_create(self, serializer):
        booking_reference = self.kwargs['booking_reference']
        booking = Booking.objects.get(booking_reference=booking_reference)
        
        # Determine attachment type
        if self.request.user == booking.customer:
            attachment_type = 'CUSTOMER'
        else:
            attachment_type = 'PROVIDER'
        
        serializer.save(
            booking=booking,
            uploaded_by=self.request.user,
            attachment_type=attachment_type
        )


class BookingHistoryView(generics.ListAPIView):
    """
    Get booking status history
    GET /api/bookings/{booking_reference}/history/
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = BookingStatusHistorySerializer
    
    def get_queryset(self):
        booking_reference = self.kwargs['booking_reference']
        return BookingStatusHistory.objects.filter(
            booking__booking_reference=booking_reference
        ).order_by('-created_at')