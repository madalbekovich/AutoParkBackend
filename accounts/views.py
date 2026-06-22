import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPCode, User
from .serializers import RequestOTPSerializer, UserSerializer, VerifyOTPSerializer
from .sms import send_sms

OTP_TTL_MINUTES = 5


def _issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@api_view(["POST"])
@permission_classes([AllowAny])
def request_otp(request):
    """Шаг 1: запросить код подтверждения на телефон."""
    serializer = RequestOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone = serializer.validated_data["phone"]

    code = f"{random.randint(0, 9999):04d}"
    OTPCode.objects.create(
        phone=phone,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    send_sms(phone, f"Auto Park: ваш код {code}")

    data = {"detail": "Код отправлен", "ttl": OTP_TTL_MINUTES * 60}
    # В dev возвращаем код в ответе — чтобы тестировать без SMS-шлюза.
    if settings.DEBUG:
        data["dev_code"] = code
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """Шаг 2: проверить код → создать/войти в аккаунт, выдать JWT."""
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone = serializer.validated_data["phone"]
    code = serializer.validated_data["code"]
    name = serializer.validated_data.get("name", "")

    otp = (
        OTPCode.objects.filter(phone=phone, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if not otp or not otp.is_valid():
        return Response({"detail": "Неверный или истёкший код"}, status=status.HTTP_400_BAD_REQUEST)

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    user, created = User.objects.get_or_create(phone=phone, defaults={"name": name})
    if not user.phone_verified:
        user.phone_verified = True
    if created and name:
        user.name = name
    user.save()

    return Response(
        {"user": UserSerializer(user, context={"request": request}).data, **_issue_tokens(user)},
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    """Текущий пользователь (GET) / обновить профиль (PATCH)."""
    if request.method == "PATCH":
        serializer = UserSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(UserSerializer(request.user, context={"request": request}).data)
