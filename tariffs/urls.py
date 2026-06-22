from rest_framework.routers import DefaultRouter

from .views import PaymentMethodViewSet, TariffViewSet

router = DefaultRouter()
router.register("tariffs", TariffViewSet, basename="tariff")
router.register("payment-methods", PaymentMethodViewSet, basename="payment-method")

urlpatterns = router.urls
