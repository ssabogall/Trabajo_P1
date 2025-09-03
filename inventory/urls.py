from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('editar/<int:pk>/', views.editar_materia_prima, name='editar_materia'),
    path('create/', views.create_raw_material, name='create_raw_material'),
]