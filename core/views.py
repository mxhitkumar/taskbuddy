from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSignupSerializer, UserSerializer, ServiceProviderProfileSerializer, BookingSerializer, ReviewSerializer
from .models import ServiceProviderProfile, Booking, Review
from .permissions import IsAdmin, IsProvider
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q

User = get_user_model()

class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

class ProviderProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ServiceProviderProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user.provider_profile

class ProviderListView(generics.ListAPIView):
    serializer_class = ServiceProviderProfileSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "designation", "skills"]
    filterset_fields = ["designation"]
    ordering_fields = ["average_rating", "pricing"]

    def get_queryset(self):
        qs = ServiceProviderProfile.objects.select_related("user").all()
        # optional proximity filter: ?lat=..&lng=..&radius_km=..
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")
        radius_km = self.request.query_params.get("radius_km")
        if lat and lng and radius_km:
            # NOTE: for production use PostGIS: here is a naive placeholder
            try:
                latf = float(lat); lngf = float(lng); rad = float(radius_km)
            except:
                return qs
            # naive bounding box filter:
            deg_delta = rad / 111.0
            qs = qs.filter(user__location_lat__gte=latf-deg_delta, user__location_lat__lte=latf+deg_delta,
                           user__location_long__gte=lngf-deg_delta, user__location_long__lte=lngf+deg_delta)
        return qs

class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status","provider","customer"]
    ordering_fields = ["service_date","created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "customer":
            return Booking.objects.filter(customer=user).select_related("provider","customer")
        if user.role == "provider":
            return Booking.objects.filter(provider=user).select_related("provider","customer")
        if user.role == "admin":
            return Booking.objects.all().select_related("provider","customer")
        return Booking.objects.none()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
