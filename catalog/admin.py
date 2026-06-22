from django.contrib import admin

from .models import (
    BodyType,
    Brand,
    CarModel,
    CurrencyRate,
    Favorite,
    Generation,
    Listing,
    ListingPhoto,
    PartsShop,
    ViewHistory,
)


@admin.register(BodyType)
class BodyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 0


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "vehicle_type", "is_popular", "order")
    list_filter = ("vehicle_type", "is_popular")
    list_editable = ("vehicle_type", "is_popular", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    inlines = [CarModelInline]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "is_popular")
    list_filter = ("brand", "is_popular")
    list_editable = ("is_popular",)
    search_fields = ("name",)


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = ("name", "car_model", "year_from", "year_to")
    list_filter = ("car_model__brand",)
    search_fields = ("name",)


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "currency", "brand", "status", "is_urgent", "created_at")
    list_filter = ("status", "vehicle_type", "condition", "is_urgent", "brand")
    search_fields = ("title", "description")
    inlines = [ListingPhotoInline]
    autocomplete_fields = ("brand", "car_model", "generation", "seller")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "created_at")


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ("code", "flag", "buy", "sell", "order", "updated_at")
    list_editable = ("buy", "sell", "order")


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "viewed_at")
    list_filter = ("user",)


@admin.register(PartsShop)
class PartsShopAdmin(admin.ModelAdmin):
    list_display = ("title", "schedule", "color", "is_active", "order")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("title",)}
