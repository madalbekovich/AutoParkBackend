"""Наполняет БД стартовыми данными: бренды, тарифы, демо-объявления.

Запуск:  python manage.py seed
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from catalog.models import Brand, CarModel, Generation, Listing
from tariffs.models import Tariff

User = get_user_model()

BRANDS = [
    ("tesla", "Tesla"),
    ("mercedes", "Mercedes"),
    ("toyota", "Toyota"),
    ("ferrari", "Ferrari"),
    ("lexus", "Lexus"),
    ("honda", "Honda"),
    ("bentley", "Bentley"),
    ("bmw", "BMW"),
]

TARIFFS = [
    ("free", "Бесплатно", 0, 7, ["Базовое размещение"], False),
    ("premium", "PREMIUM", 199, 14, ["Поднятие в топ", "Метка PREMIUM"], True),
    ("vip", "VIP", 499, 30, ["Топ выдачи", "VIP-бейдж", "Больше фото"], False),
    ("turbo", "Турбо", 99, 3, ["Турбо-продвижение 3 дня"], False),
    ("auction", "Аукцион", 0, 7, ["Участие в аукционе"], False),
]

# (title, brand_slug, model, price, currency, year, urgent)
LISTINGS = [
    ("BMW 760 Li", "bmw", "760 Li", 75000, "USD", 2021, True),
    ("Toyota crown", "toyota", "Crown", 42000, "USD", 2020, True),
    ("Mercedes E300", "mercedes", "E 300", 58000, "USD", 2019, False),
    ("Lexus RX350", "lexus", "RX 350", 39500, "USD", 2018, False),
    ("Honda Civic", "honda", "Civic", 21000, "USD", 2019, False),
    ("Lexus LX570", "lexus", "LX 570", 88000, "USD", 2021, False),
]


class Command(BaseCommand):
    help = "Наполняет БД стартовыми данными (бренды, тарифы, демо-объявления)."

    def handle(self, *args, **options):
        # --- Бренды ---
        brands = {}
        for order, (slug, name) in enumerate(BRANDS):
            brand, _ = Brand.objects.get_or_create(slug=slug, defaults={"name": name, "order": order})
            brands[slug] = brand
        self.stdout.write(self.style.SUCCESS(f"Бренды: {len(brands)}"))

        # --- Тарифы ---
        for order, (slug, name, price, days, features, popular) in enumerate(TARIFFS):
            Tariff.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "price": Decimal(price),
                    "duration_days": days,
                    "features": features,
                    "is_popular": popular,
                    "order": order,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Тарифы: {Tariff.objects.count()}"))

        # --- Демо-продавец ---
        seller, created = User.objects.get_or_create(
            phone="+996700000001",
            defaults={"name": "Демо продавец", "location": "Бишкек", "phone_verified": True},
        )
        if created:
            seller.set_password("demo12345")
            seller.save()

        # --- Демо-объявления ---
        for title, brand_slug, model_name, price, currency, year, urgent in LISTINGS:
            brand = brands[brand_slug]
            car_model, _ = CarModel.objects.get_or_create(
                brand=brand, slug=model_name.lower().replace(" ", "-"), defaults={"name": model_name}
            )
            Listing.objects.get_or_create(
                seller=seller,
                title=title,
                defaults={
                    "description": f"{title} — срочно продаётся, г. Бишкек",
                    "price": Decimal(price),
                    "currency": currency,
                    "brand": brand,
                    "car_model": car_model,
                    "year": year,
                    "city": "Бишкек",
                    "is_urgent": urgent,
                    "status": Listing.Status.ACTIVE,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Объявления: {Listing.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("Сидинг завершён ✓"))
