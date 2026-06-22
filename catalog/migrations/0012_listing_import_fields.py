from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0011_seed_models")]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="source",
            field=models.CharField("Источник", max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name="listing",
            name="external_id",
            field=models.CharField("Внешний ID", max_length=64, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name="listingphoto",
            name="external_url",
            field=models.URLField("Внешний URL", max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name="listingphoto",
            name="image",
            field=models.ImageField(upload_to="listings/", blank=True, null=True),
        ),
    ]
