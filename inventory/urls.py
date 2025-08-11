from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('update-stock/', views.update_stock, name='update_stock'),
]