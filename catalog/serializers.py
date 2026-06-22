from rest_framework import serializers

from .models import (
    BodyType,
    Brand,
    CarModel,
    CurrencyRate,
    Generation,
    Listing,
    ListingPhoto,
    PartsShop,
    ViewHistory,
)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "slug", "name", "vehicle_type", "logo", "order")


class BodyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyType
        fields = ("id", "slug", "name", "image", "order")


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = ("id", "slug", "name", "brand")


class GenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ("id", "name", "image", "year_from", "year_to", "car_model")


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ("id", "image", "order")


class ListingSerializer(serializers.ModelSerializer):
    """Карточка/деталь объявления для приложения."""

    brand_name = serializers.CharField(source="brand.name", read_only=True)
    brand_slug = serializers.CharField(source="brand.slug", read_only=True)
    model_name = serializers.CharField(source="car_model.name", read_only=True, default=None)
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    photos = ListingPhotoSerializer(many=True, read_only=True)
    cover = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            "id",
            "title",
            "description",
            "price",
            "currency",
            "brand",
            "brand_name",
            "brand_slug",
            "car_model",
            "model_name",
            "generation",
            "vehicle_type",
            "condition",
            "year",
            "mileage",
            "city",
            "body_type",
            "engine",
            "drive",
            "gearbox",
            "color",
            "owners",
            "wheel",
            "customs",
            "availability",
            "engine_volume",
            "mileage_unit",
            "vin",
            "registration",
            "region",
            "phone",
            "extra_phone",
            "call_from",
            "call_to",
            "status",
            "is_urgent",
            "deal_options",
            "specs",
            "view_count",
            "seller",
            "seller_name",
            "photos",
            "cover",
            "is_favorited",
            "created_at",
        )
        read_only_fields = ("status", "view_count", "seller", "created_at")

    def get_cover(self, obj):
        photo = obj.photos.first()
        if not photo:
            return None
        request = self.context.get("request")
        url = photo.image.url
        return request.build_absolute_uri(url) if request else url

    def get_is_favorited(self, obj):
        # Берётся из аннотации queryset (Exists); для анонима — False.
        return bool(getattr(obj, "is_favorited", False))

    def create(self, validated_data):
        # Продавец — текущий пользователь.
        validated_data["seller"] = self.context["request"].user
        return super().create(validated_data)


class CurrencyRateSerializer(serializers.ModelSerializer):
    # Decimal → строка, как в моке (UI выводит как есть).
    buy = serializers.SerializerMethodField()
    sell = serializers.SerializerMethodField()

    class Meta:
        model = CurrencyRate
        fields = ("code", "flag", "buy", "sell")

    def _fmt(self, value):
        # Убираем хвостовые нули: 89.5000 → «89.5», 0.1215 → «0.1215».
        return format(value.normalize(), "f")

    def get_buy(self, obj):
        return self._fmt(obj.buy)

    def get_sell(self, obj):
        return self._fmt(obj.sell)


class ViewHistorySerializer(serializers.ModelSerializer):
    """История просмотров в формате карточки приложения."""

    id = serializers.IntegerField(source="listing_id", read_only=True)
    title = serializers.CharField(source="listing.title", read_only=True)
    price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = ViewHistory
        fields = ("id", "title", "price", "image", "date")

    def get_price(self, obj):
        from .views import format_price_display  # локальный импорт, чтобы не плодить циклы

        return format_price_display(obj.listing.price, obj.listing.currency)

    def get_image(self, obj):
        photo = obj.listing.photos.first()
        if not photo:
            return None
        request = self.context.get("request")
        url = photo.image.url
        return request.build_absolute_uri(url) if request else url

    def get_date(self, obj):
        from django.utils import timezone

        days = (timezone.now().date() - obj.viewed_at.date()).days
        if days <= 0:
            return "Просмотрено сегодня"
        if days == 1:
            return "Просмотрено вчера"
        return f"{days} дн. назад"


class PartsShopSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = PartsShop
        fields = ("id", "title", "lines", "schedule", "color", "logo")

    def get_logo(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        url = obj.logo.url
        return request.build_absolute_uri(url) if request else url
