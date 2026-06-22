from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0012_listing_import_fields")]

    operations = [
        migrations.AddField(
            model_name="carmodel",
            name="external_id",
            field=models.CharField("Внешний ID", max_length=32, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name="generation",
            name="external_id",
            field=models.CharField("Внешний ID", max_length=32, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name="generation",
            name="external_image",
            field=models.URLField("Фото (внешний URL)", max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name="generation",
            name="name",
            field=models.CharField("Название", max_length=120),
        ),
    ]
