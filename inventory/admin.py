from django.contrib import admin

from .models import (
    RawMaterial,
    ProductRawMaterial,
    Order,
    OrderItem,
    Customer,
    Promotion,
)

# Product vive en la app products
from products.models import Product

admin.site.register(RawMaterial)
admin.site.register(Product)             # opcional, registrar también en products/admin.py
admin.site.register(ProductRawMaterial)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Customer)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "name", "scope", "discount_type", "value",
        "is_active", "starts_at", "ends_at",
    )
    filter_horizontal = ("products", "categories")
