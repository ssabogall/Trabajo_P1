from django.urls import path
from . import views

urlpatterns = [
    # Home de productos con filtros (igual que antes)
    path('', views.show_available_products, name='products_home'),

    # Alias explícito para usar en templates (p.ej. {% url 'product_list' %})
    path('list/', views.show_available_products, name='product_list'),

    # Vista simple (opcional), por si quieres ver el listado básico sin filtros
    path('simple/', views.product, name='product_simple'),

    # Lo que ya tenías
    path('forms/', views.forms, name='products_forms'),
    path('save_order_online/', views.save_order_online, name='save_order_online'),
]
