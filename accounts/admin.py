from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import OTPCode, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("phone",)
    list_display = ("phone", "name", "location", "phone_verified", "is_staff")
    search_fields = ("phone", "name")
    list_filter = ("is_staff", "phone_verified", "is_active")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Профиль", {"fields": ("name", "avatar", "location", "phone_verified")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone", "name", "password1", "password2")}),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "is_used", "created_at", "expires_at")
    search_fields = ("phone",)
