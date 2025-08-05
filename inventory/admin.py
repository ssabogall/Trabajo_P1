from django.contrib import admin
from .models import RawMaterial, Product, ProductRawMaterial
# Register your models here.


admin.site.register(RawMaterial)
admin.site.register(Product)
admin.site.register(ProductRawMaterial)