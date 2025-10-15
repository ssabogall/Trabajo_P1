from django.contrib import admin
from .models import RawMaterial, Product, ProductRawMaterial, Order, OrderItem, Customer,Comment
# Register your models here.


admin.site.register(RawMaterial)
admin.site.register(Product)
admin.site.register(ProductRawMaterial)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Customer)
admin.site.register(Comment)

# [[AGREGADO]] Registrar modelo Promotion en el admin
from .models import Promotion
admin.site.register(Promotion)
