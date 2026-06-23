from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tariffs", "0005_seed_payment_methods")]

    operations = [
        migrations.AddField(
            model_name="paymentmethod",
            name="logo",
            field=models.ImageField(
                "Логотип", upload_to="payments/", blank=True, null=True
            ),
        ),
    ]
