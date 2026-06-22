from django.conf import settings
from django.db import models


class Chat(models.Model):
    """Диалог покупатель ↔ продавец (опционально по объявлению)."""

    listing = models.ForeignKey(
        "catalog.Listing",
        related_name="chats",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Чат #{self.pk}"


class Message(models.Model):
    """Сообщение в чате."""

    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="messages", on_delete=models.CASCADE
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"
