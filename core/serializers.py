from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ServiceProviderProfile, Booking, Review
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=[("customer","Customer"),("provider","Service Provider")])

    class Meta:
        model = User
        fields = ("id","username","email","phone_number","password","role","location_lat","location_long","location_text","govt_id")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        pw = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(pw)
        # if provider, keep verification pending
        if user.role != "provider":
            user.verification_status = "approved"
        user.save()
        if user.role == "provider":
            ServiceProviderProfile.objects.create(user=user, designation="")
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","email","phone_number","role","location_lat","location_long","location_text","verification_status")


class ServiceProviderProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ServiceProviderProfile
        fields = ("user","designation","skills","pricing","availability","average_rating")


class BookingSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    provider_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="provider"), write_only=True, source="provider")
    class Meta:
        model = Booking
        fields = ("id","customer","provider","provider_id","service_date","status","issue_description","payment_status","created_at")

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["customer"] = request.user
        # provider passed in provider attr
        booking = Booking.objects.create(**validated_data)
        # Optionally enqueue notification task
        return booking


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id","booking","customer","provider","rating","comment","created_at")
        read_only_fields = ("customer","provider","created_at")

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["customer"] = request.user
        booking = validated_data["booking"]
        validated_data["provider"] = booking.provider
        return super().create(validated_data)
