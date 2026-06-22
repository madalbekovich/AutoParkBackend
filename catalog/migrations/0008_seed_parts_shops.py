from django.db import migrations

LINES = ["Немецкий авто", "Японский авто", "Корейский авто", "На заказ і наличие запчасти"]
SCHEDULE = "График работы 24/7 10:00–22:00"

# Логотипы загружаются админом из админки; при пустом logo фронт показывает текст-заглушку.
SHOPS = [
    ("arsenal", "Арсенал авто запчасти", "#F4A6A0", 0),
    ("partskg", "PARTS.KG", "#FBD24B", 1),
    ("bishkek-trade", "Bishkek Trade Service", "#AFC6E9", 2),
]


def seed(apps, schema_editor):
    PartsShop = apps.get_model("catalog", "PartsShop")
    for slug, title, color, order in SHOPS:
        PartsShop.objects.update_or_create(
            slug=slug,
            defaults={
                "title": title,
                "lines": LINES,
                "schedule": SCHEDULE,
                "color": color,
                "order": order,
                "is_active": True,
            },
        )


def unseed(apps, schema_editor):
    PartsShop = apps.get_model("catalog", "PartsShop")
    PartsShop.objects.filter(slug__in=[s[0] for s in SHOPS]).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0007_partsshop")]
    operations = [migrations.RunPython(seed, unseed)]
