from django.urls import path
from . import views

urlpatterns = [
    # POS público
    path("", views.pos, name="pos"),                          # /pos/
    path("checkout/", views.save_order, name="pos_checkout"), # /pos/checkout/

    # Alias de compatibilidad (por si en algún lugar usan create_order)
    path("create_order/", views.save_order, name="create_order"),

    # Listado de órdenes y reporte diario (si los usas en templates)
    path("orders/", views.orders, name="orders"),
    path("daily-report/", views.daily_sales_report, name="daily_sales_report"),

    # Admin / dashboard (las tuyas)
    path("admin/baneton/", views.baneton_dashboard, name="baneton_dashboard"),
    path("admin/baneton/kpis/", views.baneton_kpis, name="baneton_kpis"),
]
