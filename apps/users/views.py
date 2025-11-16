"""
User Views with JWT Authentication
"""
from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
import random
# OTPVerifipacker andcation
# ServiceProviderProfile
from users.models import User
from users.serializers import (
    UserRegistrationSerializer, LoginSerializer, UserSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, UserUpdateSerializer,
    ProviderVerificationSerializer
)
    # OTPVerificationSerializer
from users.permissions import IsSuperAdminOrAdmin, IsServiceProvider


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    POST /api/users/register/
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    """
    User login endpoint
    POST /api/users/login/
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    GET/PUT /api/users/profile/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class PasswordChangeView(views.APIView):
    """
    Change password for authenticated user
    POST /api/users/password/change/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        })


class PasswordResetRequestView(views.APIView):
    """
    Request password reset OTP
    POST /api/users/password/reset/request/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            user = User.objects.get(email=email)
            otp = OTPVerification.objects.get(
                user=user,
                otp_code=otp_code,
                otp_type=OTPVerification.OTPType.PASSWORD_RESET,
                is_used=False,
                expires_at__gte=timezone.now()
            )
            
            # Reset password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Mark OTP as used
            otp.is_used = True
            otp.save()
            
            return Response({
                'message': 'Password reset successful'
            })
        except (User.DoesNotExist, OTPVerification.DoesNotExist):
            return Response({
                'error': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationOTPView(views.APIView):
    """
    Send verification OTP for email/phone
    POST /api/users/verify/send-otp/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        otp_type = request.data.get('otp_type')
        
        if otp_type not in [OTPVerification.OTPType.EMAIL, OTPVerification.OTPType.PHONE]:
            return Response({
                'error': 'Invalid OTP type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTPVerification.objects.create(
            user=user,
            otp_type=otp_type,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
        # TODO: Send OTP via email/SMS
        
        return Response({
            'message': f'OTP sent to your {otp_type.lower()}'
        })


# class VerifyOTPView(views.APIView):
#     """
#     Verify OTP
#     POST /api/users/verify/confirm-otp/
#     """
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         serializer = OTPVerificationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         user = request.user
#         otp_code = serializer.validated_data['otp_code']
#         otp_type = serializer.validated_data['otp_type']
        
#         try:
#             otp = OTPVerification.objects.get(
#                 user=user,
#                 otp_code=otp_code,
#                 otp_type=otp_type,
#                 is_used=False,
#                 expires_at__gte=timezone.now()
#             )
            
#             # Mark user as verified
#             user.is_verified = True
#             user.save()
            
#             # Mark OTP as used
#             otp.is_used = True
#             otp.save()
            
#             return Response({
#                 'message': 'Verification successful'
#             })
#         except OTPVerification.DoesNotExist:
#             return Response({
#                 'error': 'Invalid or expired OTP'
#             }, status=status.HTTP_400_BAD_REQUEST)


class ProviderListView(generics.ListAPIView):
    """
    List all service providers (for customers)
    GET /api/users/providers/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.filter(
            role=User.UserRole.SERVICE_PROVIDER,
            is_active=True
        ).select_related('profile', 'provider_profile')
        
        # Filter by verification status
        verified_only = self.request.query_params.get('verified', 'false')
        if verified_only.lower() == 'true':
            queryset = queryset.filter(
                is_verified=True,
                provider_profile__verification_status='VERIFIED'
            )
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(profile__city__iexact=city)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                provider_profile__business_name__icontains=search
            )
        
        return queryset


class ProviderVerificationView(generics.UpdateAPIView):
    """
    Verify service provider (Admin only)
    PUT /api/users/providers/{id}/verify/
    """
    permission_classes = [IsSuperAdminOrAdmin]
    serializer_class = ProviderVerificationSerializer
    queryset = ServiceProviderProfile.objects.all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        verification_status = request.data.get('verification_status')
        
        if verification_status == 'VERIFIED':
            instance.verification_status = 'VERIFIED'
            instance.verified_at = timezone.now()
            instance.verified_by = request.user
            instance.user.is_verified = True
            instance.user.save()
        elif verification_status == 'REJECTED':
            instance.verification_status = 'REJECTED'
        
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserStatsView(views.APIView):
    """
    Get user statistics (Admin only)
    GET /api/users/stats/
    """
    permission_classes = [IsSuperAdminOrAdmin]
    
    def get(self, request):
        # Use cache for stats
        cache_key = 'user_stats'
        stats = cache.get(cache_key)
        
        if not stats:
            stats = {
                'total_users': User.objects.count(),
                'total_customers': User.objects.filter(role='CUSTOMER').count(),
                'total_providers': User.objects.filter(role='SERVICE_PROVIDER').count(),
                'verified_providers': User.objects.filter(
                    role='SERVICE_PROVIDER',
                    is_verified=True,
                    provider_profile__verification_status='VERIFIED'
                ).count(),
                'pending_verifications': ServiceProviderProfile.objects.filter(
                    verification_status='PENDING'
                ).count(),
            }
            cache.set(cache_key, stats, 300)  # Cache for 5 minutes
        
        return Response(stats).validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate OTP
            otp_code = str(random.randint(100000, 999999))
            expires_at = timezone.now() + timedelta(minutes=10)
            
            OTPVerification.objects.create(
                user=user,
                otp_type=OTPVerification.OTPType.PASSWORD_RESET,
                otp_code=otp_code,
                expires_at=expires_at
            )
            
            # TODO: Send OTP via email
            # send_mail(...)
            
            return Response({
                'message': 'Password reset OTP sent to your email'
            })
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'message': 'If the email exists, an OTP has been sent'
            })


class PasswordResetConfirmView(views.APIView):
    """
    Confirm password reset with OTP
    POST /api/users/password/reset/confirm/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # email = serializer.
        pass