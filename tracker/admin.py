from django.contrib import admin
from .models import InventoryItem, Build, BuildItem, Sale, Consumable, BuildConsumable, PurchasePlan

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "purchase_price", "status")
    list_filter = ("category", "status")

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "cost")

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("build", "sold_price", "profit", "sold_at")

@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "purchase_price")

@admin.register(PurchasePlan)
class PurchasePlanAdmin(admin.ModelAdmin):
    list_display = ("item_name", "expected_price", "is_bought", "created_at")
    list_editable = ("is_bought",)

admin.site.register(BuildItem)
admin.site.register(BuildConsumable)