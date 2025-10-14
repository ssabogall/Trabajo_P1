"""
Admin configuration for customers app.
"""

from django.contrib import admin
from .models import CustomerProfile, CookieConsent, ShoppingList, ShoppingListItem


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin interface for CustomerProfile"""
    list_display = ['customer', 'user', 'phone', 'registration_date', 'is_active']
    list_filter = ['is_active', 'registration_date']
    search_fields = ['customer__nombre', 'customer__cedula', 'user__username', 'phone']
    readonly_fields = ['registration_date']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'customer')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Status', {
            'fields': ('is_active', 'registration_date')
        }),
    )


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    """Admin interface for CookieConsent"""
    list_display = ['get_identifier', 'accepted', 'date_accepted', 'ip_address']
    list_filter = ['accepted', 'date_accepted']
    search_fields = ['customer__nombre', 'session_key', 'ip_address']
    readonly_fields = ['date_accepted', 'ip_address', 'user_agent']
    
    def get_identifier(self, obj):
        """Display customer name or session key"""
        if obj.customer:
            return f"Customer: {obj.customer.nombre}"
        return f"Session: {obj.session_key[:20]}..."
    get_identifier.short_description = 'Identifier'


class ShoppingListItemInline(admin.TabularInline):
    """Inline admin for shopping list items"""
    model = ShoppingListItem
    extra = 0
    readonly_fields = ['suggested_quantity', 'average_frequency']
    fields = ['product', 'suggested_quantity', 'user_quantity', 'average_frequency']


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Admin interface for ShoppingList"""
    list_display = ['customer', 'week_number', 'year', 'is_draft', 'is_confirmed', 'created_at']
    list_filter = ['is_draft', 'is_confirmed', 'year', 'created_at']
    search_fields = ['customer__nombre', 'customer__cedula']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ShoppingListItemInline]
    
    fieldsets = (
        ('Customer', {
            'fields': ('customer',)
        }),
        ('Period', {
            'fields': ('week_number', 'year')
        }),
        ('Status', {
            'fields': ('is_draft', 'is_confirmed', 'created_at', 'updated_at')
        }),
    )


@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    """Admin interface for ShoppingListItem"""
    list_display = ['shopping_list', 'product', 'suggested_quantity', 'user_quantity', 'final_quantity']
    list_filter = ['shopping_list__is_draft', 'shopping_list__is_confirmed']
    search_fields = ['product__name', 'shopping_list__customer__nombre']
    readonly_fields = ['suggested_quantity', 'average_frequency']
    
    def final_quantity(self, obj):
        """Display the final quantity that will be used"""
        return obj.final_quantity
    final_quantity.short_description = 'Final Quantity'
