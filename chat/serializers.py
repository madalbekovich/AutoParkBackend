from rest_framework import serializers

from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.name", read_only=True)

    class Meta:
        model = Message
        fields = ("id", "chat", "sender", "sender_name", "text", "is_read", "created_at")
        read_only_fields = ("id", "chat", "sender", "is_read", "created_at")


class ChatSerializer(serializers.ModelSerializer):
    """Чат для списка диалогов: собеседник, последнее сообщение, непрочитанные."""

    peer = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    listing_title = serializers.CharField(source="listing.title", read_only=True, default=None)
    listing_info = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            "id",
            "listing",
            "listing_title",
            "listing_info",
            "peer",
            "last_message",
            "unread_count",
            "updated_at",
        )

    def get_listing_info(self, obj):
        """Карточка объявления, по которому начат диалог (фото/цена/title)."""
        listing = obj.listing
        if not listing:
            return None
        request = self.context.get("request")
        photo = listing.photos.first()
        cover = None
        if photo:
            cover = request.build_absolute_uri(photo.image.url) if request else photo.image.url
        return {
            "id": listing.id,
            "title": listing.title,
            "price": str(listing.price),
            "currency": listing.currency,
            "cover": cover,
        }

    def _me(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def get_peer(self, obj):
        me = self._me()
        other = next((u for u in obj.participants.all() if u.id != getattr(me, "id", None)), None)
        if not other:
            return None
        request = self.context.get("request")
        avatar = None
        if other.avatar:
            avatar = request.build_absolute_uri(other.avatar.url) if request else other.avatar.url
        return {"id": other.id, "name": other.name or other.phone, "avatar": avatar}

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        return {"text": msg.text, "created_at": msg.created_at, "sender": msg.sender_id}

    def get_unread_count(self, obj):
        me = self._me()
        if not me:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=me).count()
