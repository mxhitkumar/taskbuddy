from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignupView, MeView, ProviderProfileView, ProviderListView, BookingViewSet, ReviewCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("providers/", ProviderListView.as_view(), name="providers"),
    path("provider/profile/", ProviderProfileView.as_view(), name="provider_profile"),
    path("reviews/", ReviewCreateView.as_view(), name="create_review"),
    path("", include(router.urls)),
]
    