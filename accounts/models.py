from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Менеджер пользователей с авторизацией по номеру телефона."""

    use_in_migrations = True

    def _create_user(self, phone, password=None, **extra):
        if not phone:
            raise ValueError("Номер телефона обязателен")
        user = self.model(phone=phone, **extra)
        user.set_password(password)  # password может быть None (вход по OTP)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra)

    def create_superuser(self, phone, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(phone, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """Пользователь Auto Park (идентификатор — номер телефона)."""

    class Gender(models.TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"

    phone = models.CharField("Телефон", max_length=20, unique=True)
    name = models.CharField("Имя", max_length=120, blank=True)
    full_name = models.CharField("ФИО", max_length=200, blank=True)
    email = models.EmailField("Email", blank=True)
    gender = models.CharField("Пол", max_length=6, choices=Gender.choices, blank=True)
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    location = models.CharField("Город / локация", max_length=120, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    phone_verified = models.BooleanField("Телефон подтверждён", default=False)
    push_token = models.CharField("Expo push-токен", max_length=255, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []  # phone уже USERNAME_FIELD

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.name or self.phone

    @property
    def display_name(self) -> str:
        """Имя для показа (в т.ч. в push-уведомлениях): ФИО → имя → телефон."""
        return self.full_name or self.name or self.phone


class OTPCode(models.Model):
    """Одноразовый код подтверждения телефона (регистрация/вход)."""

    phone = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "OTP-код"
        verbose_name_plural = "OTP-коды"
        ordering = ["-created_at"]

    def is_valid(self) -> bool:
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.phone} · {self.code}"
