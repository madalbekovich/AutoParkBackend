from django.utils.text import slugify

from django.db import migrations

# Модели по маркам (slug бренда → список названий моделей).
# Легковые зеркалят прежний мок; мото/спецтехника — реальные модели,
# чтобы при выборе мото-марки НЕ показывались машины Toyota.
MODELS_BY_BRAND = {
    # --- Легковая ---
    "toyota": ["CAMRY", "LAND CRUISER", "COROLLA", "RAV4", "YARIS", "CROWN"],
    "tesla": ["MODEL 3", "MODEL S", "MODEL X", "MODEL Y", "CYBERTRUCK"],
    "mercedes": ["C-CLASS", "E-CLASS", "S-CLASS", "GLE", "GLC", "AMG GT"],
    "lexus": ["RX", "LX", "ES", "NX", "GX", "LS"],
    "ferrari": ["ROMA", "PORTOFINO", "F8", "SF90", "296 GTB"],
    "honda": ["CIVIC", "ACCORD", "CR-V", "PILOT", "FIT"],
    "bentley": ["CONTINENTAL", "FLYING SPUR", "BENTAYGA"],
    "bmw": ["3 SERIES", "5 SERIES", "X5", "X7", "M3", "i4"],
    # --- Спецтехника ---
    "john-deere": ["5075E", "6155M", "8R 410", "1025R", "S780"],
    "kamaz": ["43118", "5490 NEO", "65115", "6520", "54901"],
    "caterpillar": ["320 GC", "D6", "950 GC", "424", "CT660"],
    "mtz-belarus": ["МТЗ 82.1", "МТЗ 1221", "МТЗ 320", "МТЗ 3522", "МТЗ 921"],
    "komatsu": ["PC200", "D65", "WA470", "HD465", "PC450"],
    # --- Мото ---
    "harley-davidson": ["IRON 883", "FAT BOY", "STREET GLIDE", "SPORTSTER S", "PAN AMERICA"],
    "yamaha-moto": ["YZF-R1", "MT-07", "MT-09", "TENERE 700", "XSR900"],
    "kawasaki": ["NINJA 400", "Z900", "VERSYS 650", "NINJA H2", "VULCAN S"],
    "ducati": ["PANIGALE V4", "MONSTER", "MULTISTRADA V4", "DIAVEL", "SCRAMBLER"],
    "bmw-moto": ["R 1250 GS", "S 1000 RR", "F 900 R", "R 18", "G 310 GS"],
}


def seed(apps, schema_editor):
    Brand = apps.get_model("catalog", "Brand")
    CarModel = apps.get_model("catalog", "CarModel")
    for brand_slug, names in MODELS_BY_BRAND.items():
        brand = Brand.objects.filter(slug=brand_slug).first()
        if not brand:
            continue
        for name in names:
            CarModel.objects.update_or_create(
                brand=brand, slug=slugify(name) or name.lower(), defaults={"name": name}
            )


def unseed(apps, schema_editor):
    Brand = apps.get_model("catalog", "Brand")
    CarModel = apps.get_model("catalog", "CarModel")
    for brand_slug, names in MODELS_BY_BRAND.items():
        brand = Brand.objects.filter(slug=brand_slug).first()
        if brand:
            CarModel.objects.filter(brand=brand).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0010_seed_tech_moto_brands")]
    operations = [migrations.RunPython(seed, unseed)]
