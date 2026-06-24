"""
Django settings — Auto Park backend.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из backend/.env (если есть).
load_dotenv(BASE_DIR / ".env")


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def env_bool(key: str, default: bool = False) -> bool:
    return env(key, str(default)).lower() in ("1", "true", "yes", "on")


SECRET_KEY = env(
    "SECRET_KEY",
    "django-insecure-*ed4c&&u_i1#h@si4zec2jg=b7q9s@rt)l396t$m#q)(v0-n&v",
)

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
# В dev разрешаем любой хост — чтобы телефон ходил по LAN-IP мака (и при смене сети не ломалось).
if DEBUG:
    ALLOWED_HOSTS = ["*"]

# --- За обратным прокси (Nginx) ---
# Nginx передаёт X-Forwarded-Proto — чтобы Django знал, что соединение по HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Домены, которым доверяем для CSRF (админка по HTTPS). Берётся из .env.
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in env("CSRF_TRUSTED_ORIGINS", "https://api.autopark-app.com").split(",")
    if o.strip()
]


# Application definition
INSTALLED_APPS = [
    "daphne",  # ASGI runserver (WebSockets) — должен быть выше staticfiles
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние
    "channels",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "storages",
    # Приложения Auto Park
    "accounts",
    "catalog",
    "chat",
    "tariffs",
    "notifications",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # отдаёт статику без nginx (фолбэк)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Channel layer для realtime-чата.
# ВАЖНО: API (gunicorn) и WebSocket (daphne) — РАЗНЫЕ процессы. Чтобы broadcast
# из REST-вью доходил до WS-консьюмеров (и наоборот), нужен ОБЩИЙ слой — Redis.
# In-memory работает только внутри одного процесса (локальный runserver).
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            # PubSub-слой надёжнее для долгоживущих WS-соединений: не использует
            # блокирующее чтение с таймаутом (из-за него ловили "Timeout reading
            # from redis" на простаивающих чатах). Доставка broadcast — мгновенная.
            "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        },
    }
else:
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }


# Database — Postgres (с фолбэком на SQLite, если USE_SQLITE=1).
if env_bool("USE_SQLITE", False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", "autopark"),
            "USER": env("DB_USER", os.environ.get("USER", "postgres")),
            "PASSWORD": env("DB_PASSWORD", ""),
            "HOST": env("DB_HOST", "localhost"),
            "PORT": env("DB_PORT", "5432"),
        }
    }


AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]


# Internationalization
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True


# Static & media
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- Хранилище медиа (фото объявлений, логотипы, аватары) ---
# Если в .env заданы ключи S3 (Cloudflare R2 / любое S3-совместимое) — медиа уходит
# на S3 и отдаётся через CDN-домен. Иначе (локальная разработка) — файлы в backend/media.
USE_S3 = env_bool("USE_S3", False)

if USE_S3:
    AWS_ACCESS_KEY_ID = env("S3_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("S3_BUCKET_NAME")
    # Endpoint провайдера. Для Cloudflare R2: https://<account_id>.r2.cloudflarestorage.com
    AWS_S3_ENDPOINT_URL = env("S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = env("S3_REGION", "auto")  # R2 → "auto"
    # CDN-домен (cdn.твой-домен) — все ссылки на медиа пойдут через него.
    AWS_S3_CUSTOM_DOMAIN = env("S3_CUSTOM_DOMAIN") or None

    # Публичный доступ к файлам (читаются по прямой ссылке, без подписи).
    AWS_DEFAULT_ACL = None  # R2 не поддерживает ACL — права задаются на бакете
    AWS_QUERYSTRING_AUTH = False  # ссылки без подписи (?X-Amz-...)
    AWS_S3_FILE_OVERWRITE = False  # одинаковые имена не перезатираются
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}  # кэш CDN на сутки
    AWS_S3_SIGNATURE_VERSION = "s3v4"

    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3.S3Storage"},
        # Статика админки — локально (whitenoise со сжатием + хэшем), медиа на R2.
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

    # MEDIA_URL для построения абсолютных ссылок (через CDN или endpoint бакета).
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    else:
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# CORS — в dev открыто для приложения; в проде сузить.
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL", True)
