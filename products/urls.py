from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_available_products, name='product_list'),
]
