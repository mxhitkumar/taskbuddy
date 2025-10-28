"""
User Serializers for Authentication and User Management
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from apps.users.models import User, UserProfile, ServiceProviderProfile, OTPVerification


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'date_of_birth', 'address_line1', 
            'address_line2', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude'
        ]


class ServiceProviderProfileSerializer(serializers.ModelSerializer):
    """Serializer for service provider profile"""
    verification_status_display = serializers.CharField(
        source='get_verification_status_display',
        read_only=True
    )
    
    class Meta:
        model = ServiceProviderProfile
        fields = [
            'business_name', 'business_description', 'years_of_experience',
            'verification_status', 'verification_status_display', 'verified_at',
            'id_proof', 'business_license', 'certificate',
            'average_rating', 'total_reviews', 'total_bookings', 
            'completed_bookings', 'is_available', 'max_concurrent_bookings'
        ]
        read_only_fields = [
            'verification_status', 'verified_at', 'average_rating',
            'total_reviews', 'total_bookings', 'completed_bookings'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Base user serializer"""
    profile = UserProfileSerializer(read_only=True)
    provider_profile = ServiceProviderProfileSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'is_verified',
            'profile', 'provider_profile', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'full_name', 'is_verified', 'created_at', 'last_login']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    profile = UserProfileSerializer(required=False)
    provider_profile = ServiceProviderProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'email', 'phone', 'first_name', 'last_name',
            'password', 'password_confirm', 'role',
            'profile', 'provider_profile'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        
        # Validate role
        if attrs.get('role') == User.UserRole.SUPERADMIN:
            raise serializers.ValidationError({"role": "Cannot register as superadmin."})
        
        # Require provider_profile for SERVICE_PROVIDER role
        if attrs.get('role') == User.UserRole.SERVICE_PROVIDER:
            if not attrs.get('provider_profile'):
                raise serializers.ValidationError({
                    "provider_profile": "Provider profile is required for service providers."
                })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        profile_data = validated_data.pop('profile', None)
        provider_profile_data = validated_data.pop('provider_profile', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create profile
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(user=user)
        
        # Create provider profile if service provider
        if user.role == User.UserRole.SERVICE_PROVIDER and provider_profile_data:
            ServiceProviderProfile.objects.create(user=user, **provider_profile_data)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class ProviderVerificationSerializer(serializers.ModelSerializer):
    """Serializer for provider verification (Admin use)"""
    
    class Meta:
        model = ServiceProviderProfile
        fields = [
            'verification_status', 'id_proof', 'business_license', 
            'certificate', 'business_name', 'business_description',
            'years_of_experience'
        ]
        read_only_fields = ['business_name', 'business_description', 'years_of_experience']


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)
    otp_type = serializers.ChoiceField(choices=OTPVerification.OTPType.choices)