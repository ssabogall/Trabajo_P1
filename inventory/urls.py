from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_view, name='inventory'),
    path('', views.available_products, name='available_products'),
]