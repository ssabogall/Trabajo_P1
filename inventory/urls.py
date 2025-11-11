from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('expiring/', views.expiring_materials, name='expiring_materials'),
    path('editar/<int:pk>/', views.editar_materia_prima, name='editar_materia'),
    path('create/', views.create_raw_material, name='create_raw_material'),
    path('history/', views.inventory_history, name='inventory_history'),

]