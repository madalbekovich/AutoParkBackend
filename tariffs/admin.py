from django.contrib import admin

from .models import PaymentMethod, Purchase, Tariff


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "currency", "duration_days", "is_popular", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "logo", "is_active", "order")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "tariff", "amount", "status", "started_at", "expires_at")
    list_filter = ("status", "tariff")
