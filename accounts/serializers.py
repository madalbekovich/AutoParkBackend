from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone", "name", "avatar", "location", "phone_verified", "push_token")
        read_only_fields = ("id", "phone", "phone_verified")
        extra_kwargs = {"push_token": {"write_only": True, "required": False}}


class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    name = serializers.CharField(max_length=120, required=False, allow_blank=True)
