from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_user_push_token")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="full_name",
            field=models.CharField("ФИО", max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="email",
            field=models.EmailField("Email", max_length=254, blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="gender",
            field=models.CharField(
                "Пол",
                max_length=6,
                blank=True,
                choices=[("male", "Мужской"), ("female", "Женский")],
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="birth_date",
            field=models.DateField("Дата рождения", blank=True, null=True),
        ),
    ]
