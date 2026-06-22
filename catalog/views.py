from django.db.models import Exists, OuterRef
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    BodyType,
    Brand,
    CarModel,
    CurrencyRate,
    Favorite,
    Generation,
    Listing,
    ListingPhoto,
    PartsShop,
    ViewHistory,
)
from .serializers import (
    BodyTypeSerializer,
    BrandSerializer,
    CarModelSerializer,
    CurrencyRateSerializer,
    GenerationSerializer,
    ListingPhotoSerializer,
    ListingSerializer,
    PartsShopSerializer,
    ViewHistorySerializer,
)

CURRENCY_SYMBOL = {"USD": "$", "EUR": "€", "KGS": "сом", "RUB": "₽", "KZT": "₸"}


def format_price_display(price, currency):
    """«75000.00» + «USD» → «75 000 $» (как formatPrice на фронте)."""
    n = round(float(price or 0))
    grouped = f"{n:,}".replace(",", " ")
    return f"{grouped} {CURRENCY_SYMBOL.get(currency, currency)}"


def annotate_favorited(qs, user):
    """Помечает объявления флагом is_favorited для текущего пользователя."""
    if user and user.is_authenticated:
        return qs.annotate(
            is_favorited=Exists(Favorite.objects.filter(user=user, listing=OuterRef("pk")))
        )
    return qs


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Редактировать/удалять объявление может только его продавец."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller_id == getattr(request.user, "id", None)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filterset_fields = ("vehicle_type",)  # ?vehicle_type=auto|special|moto
    pagination_class = None  # брендов мало — отдаём все


class BodyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BodyType.objects.all()
    serializer_class = BodyTypeSerializer
    pagination_class = None


class CarModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CarModel.objects.select_related("brand").all()
    serializer_class = CarModelSerializer
    # brand — по числовому id; brand__slug — по слагу (его шлёт приложение).
    filterset_fields = ("brand", "brand__slug")
    pagination_class = None


class GenerationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Generation.objects.all()
    serializer_class = GenerationSerializer
    filterset_fields = ("car_model",)
    pagination_class = None


class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filterset_fields = (
        "brand",
        "brand__slug",  # фильтр по слагу бренда (его шлёт приложение)
        "car_model",
        "car_model__slug",
        "vehicle_type",
        "condition",
        "is_urgent",
        "status",
    )
    search_fields = ("title", "description")
    ordering_fields = ("price", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        qs = Listing.objects.select_related("brand", "car_model", "seller").prefetch_related("photos")
        qs = annotate_favorited(qs, self.request.user)
        # «Мои объявления»: ?mine=1 — только текущего пользователя.
        if self.request.query_params.get("mine") and self.request.user.is_authenticated:
            return qs.filter(seller=self.request.user)
        # Публичный список — только активные.
        if self.action == "list":
            return qs.filter(status=Listing.Status.ACTIVE)
        return qs

    @action(detail=True, methods=["post"], url_path="upload-photos")
    def upload_photos(self, request, pk=None):
        """Загрузить фото к объявлению (multipart, поле image[]/images). Только владелец."""
        listing = self.get_object()  # проверяет владельца (IsOwnerOrReadOnly)
        files = request.FILES.getlist("images") or request.FILES.getlist("image")
        if not files:
            return Response({"detail": "Нет файлов"}, status=status.HTTP_400_BAD_REQUEST)
        base = listing.photos.count()
        created = [
            ListingPhoto.objects.create(listing=listing, image=f, order=base + i)
            for i, f in enumerate(files)
        ]
        data = ListingPhotoSerializer(created, many=True, context={"request": request}).data
        return Response({"photos": data}, status=status.HTTP_201_CREATED)


class FavoriteViewSet(viewsets.ViewSet):
    """Избранное текущего пользователя.

    GET    /api/favorites/            — список избранных объявлений
    POST   /api/favorites/ {listing}  — добавить в избранное
    DELETE /api/favorites/<listing>/  — убрать из избранного (pk = id объявления)
    """

    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        qs = (
            Listing.objects.filter(favorited_by__user=request.user)
            .select_related("brand", "car_model", "seller")
            .prefetch_related("photos")
            .order_by("-favorited_by__created_at")
        )
        qs = annotate_favorited(qs, request.user)
        data = ListingSerializer(qs, many=True, context={"request": request}).data
        return Response(data)

    def create(self, request):
        listing_id = request.data.get("listing")
        if not Listing.objects.filter(pk=listing_id).exists():
            return Response({"detail": "Объявление не найдено"}, status=status.HTTP_404_NOT_FOUND)
        Favorite.objects.get_or_create(user=request.user, listing_id=listing_id)
        return Response({"listing": listing_id, "is_favorited": True}, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        Favorite.objects.filter(user=request.user, listing_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrencyRateViewSet(viewsets.ReadOnlyModelViewSet):
    """Курсы валют (публичные, без пагинации)."""

    queryset = CurrencyRate.objects.all()
    serializer_class = CurrencyRateSerializer
    pagination_class = None


class PartsShopViewSet(viewsets.ReadOnlyModelViewSet):
    """Магазины запчастей (только активные, публичный)."""

    queryset = PartsShop.objects.filter(is_active=True)
    serializer_class = PartsShopSerializer
    pagination_class = None


class ViewHistoryViewSet(viewsets.ViewSet):
    """История просмотров текущего пользователя.

    GET  /api/history/            — список просмотренных объявлений
    POST /api/history/ {listing}  — записать просмотр (создаёт/обновляет время)
    """

    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        qs = (
            ViewHistory.objects.filter(user=request.user)
            .select_related("listing")
            .prefetch_related("listing__photos")
        )
        data = ViewHistorySerializer(qs, many=True, context={"request": request}).data
        return Response(data)

    def create(self, request):
        listing_id = request.data.get("listing")
        if not Listing.objects.filter(pk=listing_id).exists():
            return Response({"detail": "Объявление не найдено"}, status=status.HTTP_404_NOT_FOUND)
        ViewHistory.objects.update_or_create(user=request.user, listing_id=listing_id)
        return Response({"listing": listing_id}, status=status.HTTP_201_CREATED)
