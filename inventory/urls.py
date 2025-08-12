from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('editar/<int:pk>/', views.editar_materia_prima, name='editar_materia'),
]