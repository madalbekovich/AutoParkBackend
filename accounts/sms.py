"""Отправка SMS. В dev — заглушка (логируем код в консоль).

Для прода замени тело send_sms на вызов реального шлюза
(например, Nikita.kg / smspro.kg / Twilio) — интерфейс не меняется.
"""

import logging

logger = logging.getLogger(__name__)


def send_sms(phone: str, text: str) -> None:
    # TODO: подключить реальный SMS-провайдер.
    logger.warning("SMS → %s: %s", phone, text)
    print(f"[DEV SMS] {phone}: {text}")
