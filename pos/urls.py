from django.urls import path
from . import views

urlpatterns = [
    path("admin/baneton/", views.baneton_dashboard, name="baneton_dashboard"),
    path("admin/baneton/kpis/", views.baneton_kpis, name="baneton_kpis"),
]