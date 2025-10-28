"""
User URLs
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Password Management
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Verification
    path('verify/send-otp/', views.SendVerificationOTPView.as_view(), name='send_otp'),
    path('verify/confirm-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    
    # Provider Management
    path('providers/', views.ProviderListView.as_view(), name='provider_list'),
    path('providers/<int:pk>/verify/', views.ProviderVerificationView.as_view(), name='provider_verify'),
    
    # Statistics
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),
]