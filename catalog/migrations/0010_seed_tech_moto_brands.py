from django.db import migrations

# Примеры марок спецтехники и мото, чтобы сегменты «К. техника» и «Мото»
# не были пустыми. Логотипы загружаются админом позже.
BRANDS = [
    # (slug, name, vehicle_type, order)
    ("john-deere", "John Deere", "special", 0),
    ("kamaz", "КамАЗ", "special", 1),
    ("caterpillar", "Caterpillar", "special", 2),
    ("mtz-belarus", "МТЗ Беларус", "special", 3),
    ("komatsu", "Komatsu", "special", 4),
    ("harley-davidson", "Harley-Davidson", "moto", 0),
    ("yamaha-moto", "Yamaha", "moto", 1),
    ("kawasaki", "Kawasaki", "moto", 2),
    ("ducati", "Ducati", "moto", 3),
    ("bmw-moto", "BMW Motorrad", "moto", 4),
]


def seed(apps, schema_editor):
    Brand = apps.get_model("catalog", "Brand")
    for slug, name, vtype, order in BRANDS:
        Brand.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "vehicle_type": vtype, "order": order},
        )


def unseed(apps, schema_editor):
    Brand = apps.get_model("catalog", "Brand")
    Brand.objects.filter(slug__in=[b[0] for b in BRANDS]).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0009_brand_vehicle_type")]
    operations = [migrations.RunPython(seed, unseed)]
