from django.urls import path
from . import views

urlpatterns = [
    path('<int:product_id>/rate/', views.rate_product, name='rate_product'),  # [[AGREGADO PB-27]]
    path('', views.show_available_products, name='products_home'),
    path('forms/', views.forms, name='products_forms'),
    path('save_order_online/', views.save_order_online, name='save_order_online'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/comment/', views.add_comment, name='add_comment'),
]
