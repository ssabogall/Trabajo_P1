from django import template
from decimal import Decimal
from django.utils.safestring import mark_safe
from inventory.promo_utils import price_after_discount, get_active_promotion_for

register = template.Library()

@register.filter
def effective_price(product):
    """Return product price after applying active promotion (if any)."""
    return price_after_discount(product)

@register.filter
def has_promo(product):
    return get_active_promotion_for(product) is not None

@register.simple_tag
def price_block(product):
    """Return HTML showing old price striked and new price if promo; otherwise normal price."""
    promo = get_active_promotion_for(product)
    if promo:
        new_price = price_after_discount(product)
        html = f'<span class="text-muted text-decoration-line-through">${{product.price}}</span> ' \
               f'<span class="fw-bold">${{new_price}}</span>'
        return mark_safe(html)
    return f"${{product.price}}"
