"""
URL configuration for Bakery_proyect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include

from inventory import views as viewsInventory
from products import views as viewsProduct
from core import views as viewsCore
from pos import views as viewsPOS

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',viewsCore.landingPage),
    path("", include("pos.urls")),
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('pos/',viewsPOS.pos),
    path('pos/orders',viewsPOS.orders, name='orders'),
    path('pos/daily-report',viewsPOS.daily_sales_report, name='daily_sales_report'),
    path('save_order/', viewsPOS.save_order),
    path('save_order_online/', viewsProduct.save_order_online),
    path('inventory/', include('inventory.urls')),
   

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
