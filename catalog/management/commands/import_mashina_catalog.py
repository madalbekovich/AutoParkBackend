"""Импорт справочника марок / моделей с mashina.kg.

Запуск:
    python manage.py import_mashina_catalog                 # все марки авто
    python manage.py import_mashina_catalog --limit 20       # первые 20 марок (тест)

Источники mashina (options API):
    ads/16 → марки   (parent=None)
    ads/17 → модели  (parent = id марки)

Поколения (ads/13) НЕ импортируем: их parent_option_id не совпадает с id моделей
(дерево поколений недоступно для связывания без браузерного контекста mashina).

Идемпотентно: матчит по external_id, повторный запуск обновляет.
"""

import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Brand, CarModel

BASE = "https://api.mashina.kg/api/mbank-proxy/v1/ads"
HEADERS = {"accept": "application/json", "x-project-id": "1"}
CATEGORY = 1  # легковые (марки/модели общие)


def fetch(level, parent=None):
    params = {"category_id": CATEGORY}
    if parent is not None:
        params["parent_option_id"] = parent
    try:
        r = requests.get(f"{BASE}/{level}/options", params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001
        return []


class Command(BaseCommand):
    help = "Импорт марок/моделей/поколений с mashina.kg"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, help="Сколько марок обработать (для теста)")

    def handle(self, *args, **opts):
        brands = fetch(16)
        if opts.get("limit"):
            brands = brands[: opts["limit"]]
        self.stdout.write(f"Марок к обработке: {len(brands)}\n")

        n_models = 0
        for b in brands:
            brand = self._brand(b)
            models = fetch(17, parent=b["id"])  # модели этой марки
            for m in models:
                self._model(brand, m)
                n_models += 1
            self.stdout.write(f"  {brand.name}: {len(models)} моделей")

        self.stdout.write(
            self.style.SUCCESS(f"\nГотово. Марок: {len(brands)}, моделей: {n_models}")
        )

    def _brand(self, b):
        name = b["value"]
        slug = slugify(name) or f"brand-{b['id']}"
        brand, _ = Brand.objects.get_or_create(
            slug=slug, defaults={"name": name, "vehicle_type": "auto"}
        )
        return brand

    def _model(self, brand, m):
        name = m["value"]
        slug = (slugify(name) or f"model-{m['id']}")[:80]
        car_model, _ = CarModel.objects.update_or_create(
            brand=brand,
            slug=slug,
            defaults={"name": name[:120], "external_id": str(m["id"])},
        )
        return car_model
