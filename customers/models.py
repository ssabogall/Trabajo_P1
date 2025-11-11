"""
Customer management models.
This app extends the existing Customer model in inventory without modifying it.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CustomerProfile(models.Model):
    """
    Extended profile for registered customers.
    Links the inventory.Customer model with Django's User authentication.
    
    This allows customers to:
    - Register and login
    - Have secure authentication
    - Access their purchase history
    - Use automatic shopping lists
    """
    customer = models.OneToOneField(
        'inventory.Customer',
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Link to existing Customer model in inventory"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        help_text="Django User for authentication"
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Profile for {self.customer.nombre} ({self.user.username})"
    
    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"
        ordering = ['-registration_date']


class CookieConsent(models.Model):
    """
    Store cookie consent preferences.
    Can be linked to a customer or tracked by session for non-registered users.
    """
    customer = models.OneToOneField(
        'inventory.Customer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cookie_consent',
        help_text="Customer who gave consent (if registered)"
    )
    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Session ID for non-registered users"
    )
    accepted = models.BooleanField(default=False)
    date_accepted = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, help_text="Browser information")
    
    def __str__(self):
        if self.customer:
            return f"Consent for {self.customer.nombre}"
        return f"Consent for session {self.session_key}"
    
    class Meta:
        verbose_name = "Cookie Consent"
        verbose_name_plural = "Cookie Consents"
        ordering = ['-date_accepted']


class ShoppingList(models.Model):
    """
    Automatic shopping list based on customer purchase history.
    Generated weekly with suggested products and quantities.
    """
    customer = models.ForeignKey(
        'inventory.Customer',
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(
        default=True,
        help_text="True if list is editable, False if confirmed"
    )
    is_confirmed = models.BooleanField(default=False)
    week_number = models.IntegerField(
        help_text="Week number of the year this list was generated"
    )
    year = models.IntegerField()
    
    def __str__(self):
        status = "Draft" if self.is_draft else "Confirmed"
        return f"Shopping List for {self.customer.nombre} - Week {self.week_number}/{self.year} ({status})"
    
    class Meta:
        verbose_name = "Shopping List"
        verbose_name_plural = "Shopping Lists"
        ordering = ['-created_at']
        unique_together = ['customer', 'week_number', 'year']


class ShoppingListItem(models.Model):
    """
    Individual items in an automatic shopping list.
    Contains suggested quantity based on history and allows user modification.
    """
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE
    )
    suggested_quantity = models.PositiveIntegerField(
        help_text="Quantity suggested by the system based on purchase history"
    )
    user_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity modified by the user (optional)"
    )
    average_frequency = models.FloatField(
        default=0.0,
        help_text="How often this product is purchased (times per week)"
    )
    
    @property
    def final_quantity(self):
        """Returns user quantity if set, otherwise suggested quantity"""
        return self.user_quantity if self.user_quantity is not None else self.suggested_quantity
    
    def __str__(self):
        return f"{self.product.name} - Qty: {self.final_quantity}"
    
    class Meta:
        verbose_name = "Shopping List Item"
        verbose_name_plural = "Shopping List Items"
        unique_together = ['shopping_list', 'product']
