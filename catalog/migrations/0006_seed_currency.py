from django.db import migrations

# Стартовые курсы (зеркалят мок приложения). Редактируются из админки.
RATES = [
    ("USD", "🇺🇸", "88.50", "89.50", 0),
    ("EUR", "🇪🇺", "90.50", "91.50", 1),
    ("KZT", "🇰🇿", "0.1215", "0.190", 2),
    ("RUB", "🇷🇺", "0.950", "0.990", 3),
]


def seed(apps, schema_editor):
    CurrencyRate = apps.get_model("catalog", "CurrencyRate")
    for code, flag, buy, sell, order in RATES:
        CurrencyRate.objects.update_or_create(
            code=code, defaults={"flag": flag, "buy": buy, "sell": sell, "order": order}
        )


def unseed(apps, schema_editor):
    CurrencyRate = apps.get_model("catalog", "CurrencyRate")
    CurrencyRate.objects.filter(code__in=[r[0] for r in RATES]).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0005_currencyrate_viewhistory")]
    operations = [migrations.RunPython(seed, unseed)]
