from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Уведомления текущего пользователя: список, счётчик непрочитанных, отметить прочитанным."""

    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"detail": "ok"})

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notif = self.get_queryset().filter(pk=pk).first()
        if notif and not notif.is_read:
            notif.is_read = True
            notif.save(update_fields=["is_read"])
        return Response({"detail": "ok"})
