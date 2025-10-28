"""
Booking URLs
"""
from django.urls import path
from apps.bookings import views

app_name = 'bookings'

urlpatterns = [
    # Booking Management
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<str:booking_reference>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<str:booking_reference>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('<str:booking_reference>/status/', views.BookingStatusUpdateView.as_view(), name='booking_status'),
    path('<str:booking_reference>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    
    # Attachments & History
    path('<str:booking_reference>/attachments/', views.BookingAttachmentView.as_view(), name='booking_attachments'),
    path('<str:booking_reference>/history/', views.BookingHistoryView.as_view(), name='booking_history'),
]