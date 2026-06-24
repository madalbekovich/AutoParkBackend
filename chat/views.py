from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

User = get_user_model()


def broadcast(chat_id, payload):
    """Отправить событие всем подключённым участникам чата (realtime)."""
    layer = get_channel_layer()
    if layer:
        async_to_sync(layer.group_send)(f"chat_{chat_id}", payload)


class ChatViewSet(viewsets.ModelViewSet):
    """Диалоги текущего пользователя + история + старт чата."""

    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return (
            Chat.objects.filter(participants=self.request.user)
            .prefetch_related("participants", "messages")
            .order_by("-updated_at")
        )

    def create(self, request, *args, **kwargs):
        """Старт чата: POST {peer: <user_id>, listing?: <id>} → найти/создать диалог."""
        peer_id = request.data.get("peer")
        listing_id = request.data.get("listing") or None
        peer = User.objects.filter(id=peer_id).first()
        if not peer or peer == request.user:
            return Response({"detail": "Некорректный собеседник"}, status=status.HTTP_400_BAD_REQUEST)

        qs = Chat.objects.filter(participants=request.user).filter(participants=peer)
        qs = qs.filter(listing_id=listing_id) if listing_id else qs.filter(listing__isnull=True)
        chat = qs.first()
        created = False
        if not chat:
            chat = Chat.objects.create(listing_id=listing_id)
            chat.participants.add(request.user, peer)
            created = True

        data = ChatSerializer(chat, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """История сообщений; входящие непрочитанные помечаем прочитанными."""
        chat = self.get_object()
        chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        msgs = chat.messages.order_by("created_at")
        return Response(MessageSerializer(msgs, many=True).data)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """Надёжная отправка сообщения через REST (всегда сохраняет в БД).

        WebSocket используется для realtime-доставки, но если он не подключился
        (нет прокси ws:// и т.п.), сообщение всё равно сохранится и дойдёт через
        историю. После сохранения дублируем broadcast — подключённые получат мгновенно.
        """
        chat = self.get_object()
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "Пустое сообщение"}, status=status.HTTP_400_BAD_REQUEST)

        msg = Message.objects.create(chat=chat, sender=request.user, text=text)
        Chat.objects.filter(id=chat.id).update(updated_at=msg.created_at)
        data = MessageSerializer(msg).data

        # Realtime тем, кто онлайн (отправителю не навредит — фронт дедуплицирует по id).
        broadcast(chat.id, {"type": "chat.message", "message": data})

        # Push второму участнику.
        from accounts.push import send_push

        for u in chat.participants.exclude(id=request.user.id):
            if u.push_token:
                send_push(
                    u.push_token,
                    request.user.display_name,  # ФИО отправителя в заголовке
                    text,
                    {"chatId": chat.id},
                )

        return Response(data, status=status.HTTP_201_CREATED)


class MessageViewSet(
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """Изменение/удаление своего сообщения (с realtime-рассылкой)."""

    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Менять/удалять можно только свои сообщения.
        return Message.objects.filter(sender=self.request.user)

    def perform_update(self, serializer):
        msg = serializer.save()
        broadcast(
            msg.chat_id,
            {"type": "chat.edited", "message": MessageSerializer(msg).data},
        )

    def perform_destroy(self, instance):
        chat_id, mid = instance.chat_id, instance.id
        instance.delete()
        broadcast(chat_id, {"type": "chat.deleted", "id": mid})
