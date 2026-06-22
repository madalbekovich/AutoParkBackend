from django.db import migrations

BODY_TYPES = [
    ("sedan", "Седан"),
    ("wagon", "Универсал"),
    ("hatchback", "Хэтчбек"),
    ("coupe", "Купе"),
    ("cabrio", "Кабриолет"),
    ("suv", "Внедорожник"),
    ("crossover", "Кроссовер"),
    ("pickup", "Пикап"),
    ("minivan", "Минивэн"),
    ("van", "Фургон"),
    ("limousine", "Лимузин"),
    ("targa", "Тарга"),
]


def seed(apps, schema_editor):
    BodyType = apps.get_model("catalog", "BodyType")
    for i, (slug, name) in enumerate(BODY_TYPES):
        BodyType.objects.get_or_create(slug=slug, defaults={"name": name, "order": i})


def unseed(apps, schema_editor):
    BodyType = apps.get_model("catalog", "BodyType")
    BodyType.objects.filter(slug__in=[s for s, _ in BODY_TYPES]).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0003_bodytype_generation_image")]
    operations = [migrations.RunPython(seed, unseed)]
