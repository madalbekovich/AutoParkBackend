"""Отправка push-уведомлений через Expo Push API (безопасно, ошибки гасим)."""

import json
import urllib.request

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def send_push(token: str, title: str, body: str, data: dict | None = None) -> None:
    if not token:
        return
    payload = {
        "to": token,
        "title": title,
        "body": body,
        "sound": "default",
        # Канал, который приложение создаёт на Android (см. lib/notifications.ts).
        "channelId": "default",
    }
    if data:
        payload["data"] = data
    try:
        req = urllib.request.Request(
            EXPO_PUSH_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # push не критичен
