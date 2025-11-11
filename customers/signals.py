"""
Signals for customers app.
Handles automatic creation of related objects.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# Signals can be added here later if needed
# For example: automatically create CustomerProfile when User is created via admin

@receiver(post_save, sender=User)
def create_customer_profile_for_admin_users(sender, instance, created, **kwargs):
    """
    This signal is for future use.
    Currently, CustomerProfile is created in the registration form.
    This could be used if admins create users directly in the admin panel.
    """
    pass
