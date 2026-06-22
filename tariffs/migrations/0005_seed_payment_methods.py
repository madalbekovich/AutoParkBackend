from django.db import migrations

# Способы оплаты (зеркалят мок приложения).
METHODS = [
    ("visa", "VISA", "Банковские карты", "#1A1F71", "VISA", 0),
    ("elcart", "ЭЛКАРТ", "Банковские карты", "#1E88C7", "ЭЛКАРТ", 1),
    ("megapay", "Мегапей", "Перевод на мегапей", "#36B655", "M", 2),
    ("mbank", "Mbank", "Mbank", "#0E8C6B", "M", 3),
    ("odengi", "О! Деньги", "Pay24 терминал", "#E5007D", "O!", 4),
    ("balance", "Balance", "Balance", "#F7C32C", "B", 5),
]


def seed(apps, schema_editor):
    PaymentMethod = apps.get_model("tariffs", "PaymentMethod")
    for slug, title, subtitle, accent, emblem, order in METHODS:
        PaymentMethod.objects.update_or_create(
            slug=slug,
            defaults={
                "title": title,
                "subtitle": subtitle,
                "accent": accent,
                "emblem": emblem,
                "order": order,
                "is_active": True,
            },
        )


def unseed(apps, schema_editor):
    PaymentMethod = apps.get_model("tariffs", "PaymentMethod")
    PaymentMethod.objects.filter(slug__in=[m[0] for m in METHODS]).delete()


class Migration(migrations.Migration):
    dependencies = [("tariffs", "0004_paymentmethod")]
    operations = [migrations.RunPython(seed, unseed)]
