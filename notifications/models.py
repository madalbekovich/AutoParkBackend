from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Уведомление пользователю."""

    class Kind(models.TextChoices):
        SYSTEM = "system", "Системное"
        MESSAGE = "message", "Сообщение"
        LISTING = "listing", "Объявление"
        TARIFF = "tariff", "Тариф"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.SYSTEM)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} · {self.title}"
