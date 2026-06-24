import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Chat, Message
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    """Realtime-чат: подключение к группе chat_<id>, рассылка сообщений участникам."""

    async def connect(self):
        self.user = self.scope["user"]
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group = f"chat_{self.chat_id}"

        if not self.user.is_authenticated or not await self.is_participant():
            await self.close()
            return

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return

        # Индикатор «печатает…»
        if data.get("type") == "typing":
            await self.channel_layer.group_send(
                self.group,
                {"type": "chat.typing", "user": self.user.id, "typing": bool(data.get("typing"))},
            )
            return

        text = (data.get("text") or "").strip()
        if not text:
            return
        message = await self.save_message(text)
        # Рассылаем всем участникам группы (включая отправителя — для подтверждения).
        await self.channel_layer.group_send(
            self.group, {"type": "chat.message", "message": message}
        )
        # Push другому участнику (после broadcast — чтобы не тормозить realtime).
        await self.push_to_others(text)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"event": "message", "message": event["message"]}))

    async def chat_typing(self, event):
        await self.send(
            text_data=json.dumps(
                {"event": "typing", "user": event["user"], "typing": event["typing"]}
            )
        )

    async def chat_deleted(self, event):
        await self.send(text_data=json.dumps({"event": "delete", "id": event["id"]}))

    async def chat_edited(self, event):
        await self.send(text_data=json.dumps({"event": "edit", "message": event["message"]}))

    @database_sync_to_async
    def is_participant(self):
        return Chat.objects.filter(id=self.chat_id, participants=self.user).exists()

    @database_sync_to_async
    def save_message(self, text):
        msg = Message.objects.create(chat_id=self.chat_id, sender=self.user, text=text)
        Chat.objects.filter(id=self.chat_id).update(updated_at=msg.created_at)
        return MessageSerializer(msg).data

    @database_sync_to_async
    def push_to_others(self, text):
        from accounts.push import send_push

        chat = Chat.objects.prefetch_related("participants").get(id=self.chat_id)
        for u in chat.participants.exclude(id=self.user.id):
            if u.push_token:
                send_push(
                    u.push_token,
                    self.user.display_name,  # ФИО отправителя в заголовке
                    text,
                    {"chatId": self.chat_id},
                )
