from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_available_products, name='products_home'),
    path('forms/', views.forms, name='products_forms'),
    path('save_order_online/', views.save_order_online, name='save_order_online'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
]
