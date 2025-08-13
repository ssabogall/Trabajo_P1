from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('update-stock/', views.update_stock, name='update_stock'),
    path('editar/<int:pk>/', views.editar_materia_prima, name='editar_materia'),
]