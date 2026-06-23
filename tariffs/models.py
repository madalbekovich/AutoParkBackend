from django.conf import settings
from django.db import models


class PaymentMethod(models.Model):
    """Доступный способ оплаты (VISA / Элкарт / Mbank…). Управляется из админки."""

    slug = models.SlugField(max_length=40, unique=True)
    title = models.CharField("Название", max_length=60)
    subtitle = models.CharField("Подпись", max_length=80, blank=True)
    logo = models.ImageField("Логотип", upload_to="payments/", blank=True, null=True)
    # Фолбэк-заглушка, если логотип не загружен: цветной кружок с буквами.
    accent = models.CharField("Цвет акцента (hex)", max_length=9, default="#1A1F71")
    emblem = models.CharField("Эмблема (текст)", max_length=10, blank=True)
    is_active = models.BooleanField("Включён", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Tariff(models.Model):
    """Тарифный план продвижения (Бесплатно / PREMIUM / VIP / Турбо / Аукцион)."""

    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField("Название", max_length=80)
    tagline = models.CharField("Подзаголовок", max_length=160, blank=True)
    description = models.TextField("Описание", blank=True)
    icon = models.CharField("Иконка (Ionicons)", max_length=40, blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="KGS")
    duration_days = models.PositiveIntegerField("Срок, дней", default=7)
    features = models.JSONField("Что входит", default=list, blank=True)
    is_popular = models.BooleanField("Популярный", default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        ordering = ["order", "price"]

    def __str__(self):
        return self.name


class Purchase(models.Model):
    """Покупка тарифа (применяется к объявлению или аккаунту)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает оплаты"
        PAID = "paid", "Оплачено"
        FAILED = "failed", "Ошибка"
        EXPIRED = "expired", "Истёк"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="purchases", on_delete=models.CASCADE
    )
    tariff = models.ForeignKey(Tariff, related_name="purchases", on_delete=models.PROTECT)
    listing = models.ForeignKey(
        "catalog.Listing",
        related_name="purchases",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="KGS")
    payment_method = models.CharField(max_length=40, blank=True)  # Visa/Элкарт/Mbank…
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Покупка тарифа"
        verbose_name_plural = "Покупки тарифов"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} · {self.tariff} · {self.status}"
