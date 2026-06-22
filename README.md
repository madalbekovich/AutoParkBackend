# Auto Park — Backend (Django + DRF + PostgreSQL)

REST API для мобильного приложения Auto Park (авторынок Кыргызстана).

## Стек
- Django 5.1 + Django REST Framework
- PostgreSQL
- JWT-авторизация (`djangorestframework-simplejwt`)
- Фильтры (`django-filter`), CORS, медиа (фото)

## Приложения
- `accounts` — пользователь по телефону (custom User) + OTP-коды
- `catalog` — бренды, модели, поколения, объявления, фото, избранное
- `chat` — диалоги и сообщения
- `tariffs` — тарифы продвижения + покупки
- `notifications` — уведомления

## Запуск (dev)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# PostgreSQL должен быть запущен; создать БД:
createdb autopark

# .env уже есть (см. .env.example). Миграции + сидинг:
python manage.py migrate
python manage.py seed                    # бренды, тарифы, демо-объявления
python manage.py createsuperuser --phone +996555000000

# Запустить (0.0.0.0 — чтобы достучаться с телефона по LAN)
python manage.py runserver 0.0.0.0:8000
```

Админка: http://localhost:8000/admin/

## API (основное)
| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/brands/` | марки |
| GET | `/api/models/?brand=<id>` | модели марки |
| GET | `/api/generations/?car_model=<id>` | поколения |
| GET | `/api/listings/` | объявления (фильтры: `brand`, `vehicle_type`, `condition`, `is_urgent`; `search=`, `ordering=price\|-created_at`) |
| GET | `/api/listings/?mine=1` | мои объявления (нужен токен) |
| GET/POST/PATCH/DELETE | `/api/listings/<id>/` | CRUD объявления (изменять может только владелец) |
| POST | `/api/auth/token/` | получить JWT (phone + password) |
| POST | `/api/auth/token/refresh/` | обновить токен |

## Связь с приложением
RN-приложение ходит сюда через `src/api/` (client + repository). Базовый URL — в
`src/api/config.ts` (`API_BASE_URL`), на устройстве это LAN-IP мака, не localhost.

## TODO (следующие шаги)
- OTP-флоу авторизации (отправка SMS, проверка кода) → выдача JWT
- Эндпоинты: favorites, chat (+ realtime через Channels), tariffs/purchase, notifications
- Загрузка фото объявлений (multipart)
- Анализ рынка (агрегация цен по марке/модели)
