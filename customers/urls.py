"""
URL configuration for customers app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='customer_register'),
    path('login/', views.login_view, name='customer_login'),
    path('logout/', views.logout_view, name='customer_logout'),
    path('profile/', views.profile_view, name='customer_profile'),
    
    # Cookie consent
    path('cookies/accept/', views.accept_cookies, name='accept_cookies'),
    path('cookies/check/', views.check_cookies, name='check_cookies'),
]
