from django.conf import settings
from django.db import models


class Brand(models.Model):
    """Марка (Tesla, Toyota, John Deere, Harley…)."""

    class VehicleType(models.TextChoices):
        AUTO = "auto", "Легковая"
        SPECIAL = "special", "Спецтехника"
        MOTO = "moto", "Мото"

    slug = models.SlugField("Код", max_length=50, unique=True)
    name = models.CharField("Название", max_length=80)
    vehicle_type = models.CharField(
        "Тип техники", max_length=10, choices=VehicleType.choices, default=VehicleType.AUTO
    )
    logo = models.ImageField("Логотип", upload_to="brands/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Марка"
        verbose_name_plural = "Марки"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """Модель в рамках марки (Land Cruiser 300, X5, …)."""

    brand = models.ForeignKey(Brand, related_name="models", on_delete=models.CASCADE)
    slug = models.SlugField("Код", max_length=80)
    name = models.CharField("Название", max_length=120)

    class Meta:
        verbose_name = "Модель"
        verbose_name_plural = "Модели"
        unique_together = ("brand", "slug")
        ordering = ["name"]

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class BodyType(models.Model):
    """Справочник типов кузова (Седан, Купе, Внедорожник…)."""

    slug = models.SlugField("Код", max_length=40, unique=True)
    name = models.CharField("Название", max_length=60)
    image = models.ImageField("Силуэт", upload_to="body_types/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Тип кузова"
        verbose_name_plural = "Типы кузова"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Generation(models.Model):
    """Поколение модели (период)."""

    car_model = models.ForeignKey(CarModel, related_name="generations", on_delete=models.CASCADE)
    name = models.CharField("Название", max_length=80)  # напр. "2021-2014"
    image = models.ImageField("Фото", upload_to="generations/", blank=True, null=True)
    year_from = models.PositiveIntegerField("Год от", blank=True, null=True)
    year_to = models.PositiveIntegerField("Год до", blank=True, null=True)

    class Meta:
        verbose_name = "Поколение"
        verbose_name_plural = "Поколения"
        ordering = ["-year_from"]

    def __str__(self):
        return f"{self.car_model} · {self.name}"


class Listing(models.Model):
    """Объявление о продаже."""

    class VehicleType(models.TextChoices):
        AUTO = "auto", "Автомобиль"
        SPECIAL = "special", "Спецтехника"
        MOTO = "moto", "Мото"

    class Condition(models.TextChoices):
        NEW = "new", "Новый"
        USED = "used", "С пробегом"

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        MODERATION = "moderation", "На модерации"
        ACTIVE = "active", "Активно"
        SOLD = "sold", "Продано"
        ARCHIVED = "archived", "В архиве"

    class Currency(models.TextChoices):
        USD = "USD", "$"
        KGS = "KGS", "сом"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="listings", on_delete=models.CASCADE
    )
    title = models.CharField("Заголовок", max_length=160)
    description = models.TextField("Описание", blank=True)

    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)

    brand = models.ForeignKey(Brand, related_name="listings", on_delete=models.PROTECT)
    car_model = models.ForeignKey(
        CarModel, related_name="listings", on_delete=models.SET_NULL, blank=True, null=True
    )
    generation = models.ForeignKey(
        Generation, related_name="listings", on_delete=models.SET_NULL, blank=True, null=True
    )

    vehicle_type = models.CharField(
        max_length=10, choices=VehicleType.choices, default=VehicleType.AUTO
    )
    condition = models.CharField(max_length=4, choices=Condition.choices, default=Condition.USED)
    year = models.PositiveIntegerField("Год выпуска", blank=True, null=True)
    mileage = models.PositiveIntegerField("Пробег, км", blank=True, null=True)
    city = models.CharField("Город", max_length=120, blank=True)

    body_type = models.CharField("Тип кузова", max_length=40, blank=True)
    engine = models.CharField("Тип двигателя", max_length=40, blank=True)
    drive = models.CharField("Привод", max_length=40, blank=True)
    gearbox = models.CharField("Коробка передач", max_length=40, blank=True)
    color = models.CharField("Цвет", max_length=40, blank=True)
    owners = models.CharField("Владельцев", max_length=20, blank=True)
    wheel = models.CharField("Руль", max_length=20, blank=True)  # left / right
    customs = models.CharField("Растаможен", max_length=20, blank=True)
    availability = models.CharField("Наличие", max_length=20, blank=True)  # in_stock / on_order
    engine_volume = models.CharField("Объём двигателя", max_length=20, blank=True)
    mileage_unit = models.CharField("Ед. пробега", max_length=10, blank=True)  # km / mile
    vin = models.CharField("VIN", max_length=40, blank=True)
    registration = models.CharField("Учёт", max_length=80, blank=True)
    region = models.CharField("Регион продажи", max_length=80, blank=True)

    # Контакты продавца
    phone = models.CharField("Телефон", max_length=30, blank=True)
    extra_phone = models.CharField("Доп. телефон", max_length=30, blank=True)
    call_from = models.CharField("Звонить с", max_length=10, blank=True)
    call_to = models.CharField("Звонить до", max_length=10, blank=True)

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    is_urgent = models.BooleanField("Срочно", default=False)
    # Дополнительные опции расчёта (выкуп/аренда/рассрочка/обмен…).
    deal_options = models.JSONField("Опции сделки", default=list, blank=True)

    # Доп. характеристики (двигатель, КПП, цвет…) — гибко.
    specs = models.JSONField("Характеристики", default=dict, blank=True)

    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["brand", "car_model"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.title


class ListingPhoto(models.Model):
    """Фото объявления."""

    listing = models.ForeignKey(Listing, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="listings/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Фото объявления"
        verbose_name_plural = "Фото объявлений"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Фото #{self.pk} → {self.listing_id}"


class Favorite(models.Model):
    """Избранное (закладка пользователя)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="favorites", on_delete=models.CASCADE
    )
    listing = models.ForeignKey(Listing, related_name="favorited_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ("user", "listing")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.listing_id}"


class CurrencyRate(models.Model):
    """Курс валюты к сому (для экрана «Курс валют»). Редактируется из админки."""

    code = models.CharField("Код", max_length=3, unique=True)  # USD/EUR/KZT/RUB
    flag = models.CharField("Флаг (emoji)", max_length=8, blank=True)
    buy = models.DecimalField("Покупка", max_digits=10, decimal_places=4)
    sell = models.DecimalField("Продажа", max_digits=10, decimal_places=4)
    order = models.PositiveIntegerField("Порядок", default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Курс валюты"
        verbose_name_plural = "Курсы валют"
        ordering = ["order", "code"]

    def __str__(self):
        return f"{self.code}: {self.buy}/{self.sell}"


class ViewHistory(models.Model):
    """История просмотров объявлений пользователем (для экрана «История»)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="view_history", on_delete=models.CASCADE
    )
    listing = models.ForeignKey(Listing, related_name="views", on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Просмотр"
        verbose_name_plural = "История просмотров"
        unique_together = ("user", "listing")  # один листинг — одна запись (обновляем время)
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.user} 👁 {self.listing_id}"


class PartsShop(models.Model):
    """Магазин запчастей (партнёр) — экран «Сервис :»."""

    slug = models.SlugField(max_length=60, unique=True)
    title = models.CharField("Название", max_length=120)
    lines = models.JSONField("Строки описания", default=list, blank=True)
    schedule = models.CharField("График работы", max_length=120, blank=True)
    color = models.CharField("Цвет карточки (hex)", max_length=9, default="#F4A6A0")
    logo = models.ImageField("Логотип", upload_to="parts/", blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Магазин запчастей"
        verbose_name_plural = "Магазины запчастей"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
