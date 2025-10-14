"""
URL configuration for Bakery_proyect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

from core import views as viewsCore
# (Opcional: puedes dejar estos imports si los usas en otros lugares)
from inventory import views as viewsInventory  # noqa: F401
from products import views as viewsProduct     # noqa: F401
from pos import views as viewsPOS              # noqa: F401

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home
    path("", viewsCore.landingPage, name="home"),

    # Admin
    path("", include("pos.urls")),
    path("admin/", admin.site.urls),

    # Apps delegadas a sus propios routers
    path("products/", include("products.urls")),
    path("pos/", include("pos.urls")),
    path('pos/orders',viewsPOS.orders, name='orders'),
    path('pos/daily-report',viewsPOS.daily_sales_report, name='daily_sales_report'),
    path('save_order/', viewsPOS.save_order),
    path('save_order_online/', viewsProduct.save_order_online),
    path("inventory/", include("inventory.urls")),
]

# Archivos estáticos/media en DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
