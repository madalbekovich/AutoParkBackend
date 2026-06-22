from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0013_catalog_external_fields")]

    operations = [
        migrations.AddField(
            model_name="brand",
            name="is_popular",
            field=models.BooleanField("Популярная", default=False),
        ),
        migrations.AddField(
            model_name="carmodel",
            name="is_popular",
            field=models.BooleanField("Популярная", default=False),
        ),
        migrations.AlterModelOptions(
            name="brand",
            options={
                "ordering": ["-is_popular", "order", "name"],
                "verbose_name": "Марка",
                "verbose_name_plural": "Марки",
            },
        ),
        migrations.AlterModelOptions(
            name="carmodel",
            options={
                "ordering": ["-is_popular", "name"],
                "verbose_name": "Модель",
                "verbose_name_plural": "Модели",
            },
        ),
    ]
