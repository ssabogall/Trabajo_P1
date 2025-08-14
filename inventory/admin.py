from django.contrib import admin
from .models import RawMaterial, Product, ProductRawMaterial, Order, OrderItem

# Configuración mejorada para RawMaterial
@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'units', 'exp_date')
    list_filter = ('exp_date', 'units')
    search_fields = ('name',)
    ordering = ('name',)

# Configuración mejorada para Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description')
    list_filter = ('price',)
    search_fields = ('name', 'description')
    ordering = ('name',)

# Configuración para ProductRawMaterial
@admin.register(ProductRawMaterial)  
class ProductRawMaterialAdmin(admin.ModelAdmin):
    list_display = ('product', 'raw_material', 'quantity')
    list_filter = ('product', 'raw_material')
    ordering = ('product',)





"""
Comentando los modelos que no necesitamos en el admin:
- CountRawMaterial: Se maneja desde la vista de inventario
- ProductInventory: No se está usando actualmente

@admin.register(CountRawMaterial)
class CountRawMaterialAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'total_quantity', 'minimum_stock', 'last_updated']
    list_filter = ['raw_material',]
    search_fields = ['raw_material__name']

    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Stock Bajo'

@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'stock_quantity', 'minimum_stock', 'is_low_stock', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['product__name']

    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Stock Bajo'
"""
