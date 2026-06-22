from rest_framework.routers import DefaultRouter

from .views import (
    BodyTypeViewSet,
    BrandViewSet,
    CarModelViewSet,
    CurrencyRateViewSet,
    FavoriteViewSet,
    GenerationViewSet,
    ListingViewSet,
    PartsShopViewSet,
    ViewHistoryViewSet,
)

router = DefaultRouter()
router.register("brands", BrandViewSet)
router.register("body-types", BodyTypeViewSet)
router.register("models", CarModelViewSet)
router.register("generations", GenerationViewSet)
router.register("listings", ListingViewSet, basename="listing")
router.register("favorites", FavoriteViewSet, basename="favorite")
router.register("currency", CurrencyRateViewSet)
router.register("history", ViewHistoryViewSet, basename="history")
router.register("parts-shops", PartsShopViewSet)

urlpatterns = router.urls
