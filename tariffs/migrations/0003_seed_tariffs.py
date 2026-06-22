from django.db import migrations

# Базовый набор тарифов (зеркалит мок мобильного приложения).
# price = 0 → «Бесплатно». Срок в днях; в UI станет «N дней».
TARIFFS = [
    {
        "slug": "free",
        "name": "Бесплатно",
        "tagline": "Бесплатная реклама",
        "icon": "gift-outline",
        "price": 0,
        "duration_days": 0,
        "order": 0,
        "description": (
            "Приветствуем вас на нашем бесплатном рекламном сервисе! Мы предоставляем "
            "возможность разместить вашу рекламу абсолютно бесплатно на нашей платформе. "
            "Наша цель — помочь вам достичь большей аудитории и увеличить продажи вашего "
            "автомобиля."
        ),
    },
    {
        "slug": "premium",
        "name": "PREMIUM",
        "tagline": "Максимальное продвижение",
        "icon": "diamond-outline",
        "price": 500,
        "duration_days": 30,
        "is_popular": True,
        "order": 1,
        "description": (
            "Мы предлагаем Вам мощный инструмент для продвижения Вашего объявления. С нашим "
            "сервисом Вы можете достичь невероятных результатов в продажах и расширении "
            "аудитории. Мы сосредоточены на высококачественных рекламных кампаниях."
        ),
    },
    {
        "slug": "vip",
        "name": "VIP",
        "tagline": "250 сомов. 30 дней. Безлимитное удовольствие.",
        "icon": "star-outline",
        "price": 250,
        "duration_days": 30,
        "order": 2,
        "description": (
            "VIP рекламный сервис — это лучшее решение для тех, кто хочет получить "
            "максимальную отдачу от своего объявления. Ваше авто всегда наверху списка и "
            "заметно для всех покупателей."
        ),
    },
    {
        "slug": "turbo",
        "name": "Турбо-Продажа",
        "tagline": "Быстрая и эффективная продажа",
        "icon": "flash-outline",
        "price": 300,
        "duration_days": 14,
        "order": 3,
        "description": (
            "Продайте свою машину на «Турбо-Продаже»! Хотите получить максимальную "
            "стоимость за свой автомобиль? Наша платформа обеспечивает быструю и "
            "эффективную продажу вашего авто. Быстрый и продуманный процесс."
        ),
    },
    {
        "slug": "auction",
        "name": "Аукцион",
        "tagline": "Лучшая цена за ваш автомобиль",
        "icon": "hammer-outline",
        "price": 400,
        "duration_days": 7,
        "order": 4,
        "description": (
            "Хотите получить лучшую цену за свой автомобиль? Участвуйте в нашем "
            "инновационном онлайн-аукционе для быстрой и выгодной продажи! Максимальная "
            "экспозиция: ваш автомобиль будет представлен широкой аудитории."
        ),
    },
]


def seed(apps, schema_editor):
    Tariff = apps.get_model("tariffs", "Tariff")
    for item in TARIFFS:
        Tariff.objects.update_or_create(slug=item["slug"], defaults=item)


def unseed(apps, schema_editor):
    Tariff = apps.get_model("tariffs", "Tariff")
    Tariff.objects.filter(slug__in=[t["slug"] for t in TARIFFS]).delete()


class Migration(migrations.Migration):
    dependencies = [("tariffs", "0002_tariff_description_tariff_icon_tariff_tagline")]
    operations = [migrations.RunPython(seed, unseed)]
