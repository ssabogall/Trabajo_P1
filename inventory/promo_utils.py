from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from .models import Promotion, Product

def get_active_promotion_for(product: Product):
    """Find the first active promotion that applies to the product."""
    now = timezone.now()
    qs = Promotion.objects.filter(is_active=True).filter(
        Q(starts_at__isnull=True) | Q(starts_at__lte=now),
        Q(ends_at__isnull=True) | Q(ends_at__gte=now),
    ).filter(
        Q(applies_to_all=True) | Q(products=product)
    ).order_by('-id')
    return qs.first()

def price_after_discount(product: Product) -> Decimal:
    promo = get_active_promotion_for(product)
    if not promo:
        return product.price
    if promo.discount_type == 'fixed':
        return max(Decimal('0.00'), product.price - promo.value)
    # percent
    return max(Decimal('0.00'), (product.price * (Decimal('100') - promo.value) / Decimal('100')).quantize(Decimal('0.01')))
