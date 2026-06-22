"""Импорт объявлений с mashina.kg (по разрешению) в нашу БД.

Запуск:
    python manage.py import_mashina                 # все категории, по 2 страницы
    python manage.py import_mashina --pages 5        # 5 страниц на категорию
    python manage.py import_mashina --category auto  # только легковые

Идемпотентно: повторный запуск обновляет объявления по external_id, не дублирует.
"""

from decimal import Decimal, InvalidOperation

import requests
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Brand, Listing, ListingPhoto

User = get_user_model()

API = "https://mashina.kg/api/mbank-proxy/v1/ads/listings"
HEADERS = {"accept": "application/json", "x-project-id": "1"}

# category_id mashina → наш vehicle_type.
CATEGORIES = {
    "auto": 1,      # легковые
    "moto": 18,     # мото
    "special": 16,  # коммерческий / спецтехника
}


def attr(attributes, slug):
    """Достаёт значение атрибута по slug (текст или число)."""
    for a in attributes or []:
        if a.get("slug") == slug:
            return a.get("value_text") or a.get("value_number")
    return None


class Command(BaseCommand):
    help = "Импорт объявлений с mashina.kg"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=2, help="Страниц на категорию")
        parser.add_argument("--size", type=int, default=21, help="Объявлений на страницу")
        parser.add_argument(
            "--category", choices=list(CATEGORIES), help="Только одна категория"
        )

    def handle(self, *args, **opts):
        # Системный продавец для импортных объявлений (seller обязателен в модели).
        seller, _ = User.objects.get_or_create(
            phone="+000000000000", defaults={"name": "mashina.kg", "is_active": False}
        )

        cats = {opts["category"]: CATEGORIES[opts["category"]]} if opts["category"] else CATEGORIES
        total_saved = 0

        for vtype, cat_id in cats.items():
            self.stdout.write(f"\n=== {vtype} (category_id={cat_id}) ===")
            for page in range(1, opts["pages"] + 1):
                items = self._fetch(cat_id, page, opts["size"])
                if not items:
                    break
                for it in items:
                    if self._save(it, vtype, seller):
                        total_saved += 1
                self.stdout.write(f"  стр.{page}: обработано {len(items)}")

        self.stdout.write(self.style.SUCCESS(f"\nГотово. Сохранено/обновлено: {total_saved}"))

    def _fetch(self, cat_id, page, size):
        params = {
            "category_id": cat_id,
            "sort_by": "created_at",
            "order": "desc",
            "page": page,
            "size": size,
        }
        try:
            r = requests.get(API, params=params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r.json().get("items", [])
        except Exception as e:  # noqa: BLE001
            self.stderr.write(f"  ошибка загрузки стр.{page}: {e}")
            return []

    def _save(self, it, vtype, seller):
        ext_id = str(it["id"])
        attrs = it.get("attributes", [])

        # Цена: берём оригинальную (is_original) либо первую.
        prices = it.get("prices") or []
        orig = next((p for p in prices if p.get("is_original")), prices[0] if prices else None)
        if not orig:
            return False
        try:
            price = Decimal(str(orig["amount"]))
        except (InvalidOperation, KeyError):
            return False
        currency = "USD" if orig.get("currency") == "USD" else "KGS"

        # Бренд: первое слово из title (Lexus, Toyota…) → матчим/создаём.
        brand = self._brand_for(it, vtype)
        # Модель: ищем среди моделей этой марки по названию в title.
        car_model = self._model_for(brand, it.get("title", ""))

        year = attr(attrs, "year")
        mileage = attr(attrs, "mileage")
        mileage_num = None
        if mileage:
            digits = "".join(c for c in str(mileage) if c.isdigit())
            mileage_num = int(digits) if digits else None

        wheel = attr(attrs, "steering_wheel") or ""
        wheel = "left" if "лев" in str(wheel).lower() else ("right" if "прав" in str(wheel).lower() else "")

        defaults = {
            "seller": seller,
            "title": it.get("title", "")[:160],
            "description": it.get("description", "") or "",
            "price": price,
            "currency": currency,
            "brand": brand,
            "car_model": car_model,
            "vehicle_type": vtype,
            "year": int(year) if year else None,
            "mileage": mileage_num,
            "city": str(attr(attrs, "city") or "")[:120],
            "body_type": str(attr(attrs, "body_type") or "")[:40],
            "gearbox": str(attr(attrs, "gearbox") or "")[:40],
            "engine_volume": str(attr(attrs, "engine_volume") or "")[:20],
            "wheel": wheel,
            "view_count": (it.get("counters") or {}).get("views_count", 0),
            "is_urgent": bool(it.get("is_urgent")),
            "status": "active",
            "source": "mashina",
        }

        listing, _ = Listing.objects.update_or_create(
            source="mashina", external_id=ext_id, defaults=defaults
        )

        # Фото: сохраняем URL'ы (medium) как ListingPhoto, без перезаливки.
        images = it.get("images") or []
        if images:
            listing.photos.all().delete()
            for i, img in enumerate(images[:10]):
                url = img.get("medium") or img.get("big") or img.get("thumb")
                if url:
                    ListingPhoto.objects.create(listing=listing, external_url=url, order=i)
        return True

    def _brand_for(self, it, vtype):
        """Бренд: сначала ищем существующий по началу title (учитывая
        составные «Mercedes-Benz»), иначе создаём по первому слову."""
        title = it.get("title", "").replace("Продажа", "").strip()
        # Среди уже импортированных марок ищем ту, с которой начинается title.
        for brand in Brand.objects.all():
            if title.lower().startswith(brand.name.lower()):
                return brand
        words = [w for w in title.split() if w]
        name = words[0] if words else "Прочее"
        slug = slugify(name) or "brand"
        brand, _ = Brand.objects.get_or_create(
            slug=slug, defaults={"name": name, "vehicle_type": vtype}
        )
        return brand

    def _model_for(self, brand, title):
        """Модель марки: ищем самое длинное совпадение названия модели в title."""
        rest = title.replace("Продажа", "").strip()
        # Убираем имя марки из начала.
        if rest.lower().startswith(brand.name.lower()):
            rest = rest[len(brand.name):].strip()
        rest_low = rest.lower()
        best = None
        for m in brand.models.all():
            if m.name and rest_low.startswith(m.name.lower()):
                if best is None or len(m.name) > len(best.name):
                    best = m
        return best
