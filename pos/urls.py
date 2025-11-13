from django.urls import path
from . import views

urlpatterns = [
    # POS y órdenes
    path('', views.pos, name='pos'),
    path('orders/', views.orders, name='orders'),
    path('daily-report/', views.daily_sales_report, name='daily_sales_report'),
    path('save_order/', views.save_order, name='save_order'),
    
    # Admin dashboard
    path("admin/baneton/", views.baneton_dashboard, name="baneton_dashboard"),
    path("admin/baneton/kpis/", views.baneton_kpis, name="baneton_kpis"),
]
