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
from django.urls import path, include

from core import views as viewsCore

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Core pages
    path('', viewsCore.landingPage, name='landing'),
    path('adminbaneton/', viewsCore.landingPageAdmin, name='admin_landing'),
    path('about/', viewsCore.about, name='about'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps
    path('products/', include('products.urls')),
    path('pos/', include('pos.urls')),
    path('inventory/', include('inventory.urls')),
    path('customers/', include('customers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
