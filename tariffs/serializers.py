from rest_framework import serializers

from .models import PaymentMethod, Tariff


class PaymentMethodSerializer(serializers.ModelSerializer):
    # id отдаём как slug, чтобы фронт-тип (id: string) совпал.
    id = serializers.CharField(source="slug", read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = ("id", "title", "subtitle", "logo", "accent", "emblem")

    def get_logo(self, obj):
        if not obj.logo:
            return None
        url = obj.logo.url
        # S3/R2 (CDN) — абсолютный URL отдаём как есть; локальный — достраиваем.
        if url.startswith("http"):
            return url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class TariffSerializer(serializers.ModelSerializer):
    """Тариф в формате, который ждёт мобильное приложение.

    Цена и срок отдаются уже строками для прямого вывода в UI:
    free → «Бесплатно», иначе «500 KGS»; period → «30 дней» или пусто.
    """

    price = serializers.SerializerMethodField()
    period = serializers.SerializerMethodField()
    free = serializers.SerializerMethodField()

    class Meta:
        model = Tariff
        fields = (
            "id",
            "slug",
            "name",
            "tagline",
            "description",
            "icon",
            "price",
            "period",
            "free",
            "features",
            "is_popular",
        )

    def get_free(self, obj) -> bool:
        return obj.price == 0

    def get_price(self, obj) -> str:
        if obj.price == 0:
            return "Бесплатно"
        # 500.00 → «500 KGS» (отбрасываем нулевую дробную часть)
        amount = obj.price.normalize()
        amount = int(amount) if amount == amount.to_integral() else amount
        return f"{amount} {obj.currency}"

    def get_period(self, obj) -> str:
        if obj.price == 0 or not obj.duration_days:
            return ""
        return f"{obj.duration_days} дней"
