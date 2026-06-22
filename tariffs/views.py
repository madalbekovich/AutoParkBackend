from rest_framework import viewsets

from .models import PaymentMethod, Tariff
from .serializers import PaymentMethodSerializer, TariffSerializer


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тарифов продвижения (публичный, без пагинации)."""

    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    pagination_class = None  # тарифов мало — отдаём все


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """Доступные способы оплаты (только включённые, публичный)."""

    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    pagination_class = None
