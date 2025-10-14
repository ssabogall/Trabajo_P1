# inventory/services/discounts.py
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone

# Import directo (tu modelo está en inventory.models)
from inventory.models import Promotion

# Redondeo homogéneo a 2 decimales
CENT = Decimal("0.01")
def money(x: Decimal) -> Decimal:
    return (Decimal(x) if not isinstance(x, Decimal) else x).quantize(CENT, rounding=ROUND_HALF_UP)


def _is_active(promo: Promotion) -> bool:
    if not promo.is_active:
        return False
    now = timezone.now()
    if promo.starts_at and now < promo.starts_at:
        return False
    if promo.ends_at and now > promo.ends_at:
        return False
    return True


def _promo_applies_to_product(promo: Promotion, product) -> bool:
    """
    Regla de alcance:
      - applies_to_all = True → aplica a todos
      - products M2M → aplica si el producto está seleccionado
      - categories M2M → aplica si product.category ∈ categorías (si el campo existe)
    """
    if promo.applies_to_all:
        return True

    # Por producto
    try:
        if promo.products.filter(pk=product.pk).exists():
            return True
    except Exception:
        pass

    # Por categoría (si el producto tiene category)
    try:
        if getattr(product, "category_id", None) is not None:
            return promo.categories.filter(pk=product.category_id).exists()
    except Exception:
        pass

    return False


def _apply_rule(base_unit: Decimal, promo: Promotion) -> Decimal:
    """
    Tipos soportados por tu modelo:
      - "percent": value=10 -> -10%
      - "fixed":   value=2000 -> -$2000
    """
    value = Decimal(promo.value or 0)
    if promo.discount_type == "percent":
        return max(Decimal("0.00"), base_unit * (Decimal("1.00") - (value / Decimal("100"))))
    if promo.discount_type == "fixed":
        return max(Decimal("0.00"), base_unit - value)
    # Fallback por si en el futuro agregas más tipos
    return base_unit


def best_product_unit_price(product, qty: int = 1):
    """
    Calcula el MEJOR precio unitario aplicable al producto hoy:
      - toma el precio base (product.price)
      - evalúa todas las promos activas que le apliquen
      - devuelve el mínimo (mejor) precio unitario.
    Retorna: (final_unit_price, discount_amount_unit, percent_int)
    """
    base = money(Decimal(getattr(product, "price", 0) or 0))
    best = base

    # Promos candidatas (filtra por activas y alcance)
    promos = Promotion.objects.all()
    active_applicable = [p for p in promos if _is_active(p) and _promo_applies_to_product(p, product)]

    for p in active_applicable:
        candidate = money(_apply_rule(base, p))
        if candidate < best:
            best = candidate

    disc_u = money(base - best)
    percent = int((disc_u / base * 100).quantize(Decimal("1"))) if base else 0
    return best, disc_u, percent


def price_cart(cart, order_level_promos: bool = False):
    """
    Valora un carrito de la forma:
      cart = [{"product": <Product>, "qty": <int>}, ...]
    Calcula por línea:
      - unit_price (mejor precio con promo)
      - line_subtotal = (precio base) * qty
      - line_total    = unit_price * qty
      - line_discount = line_subtotal - line_total
    y totales de la orden:
      - subtotal, discount_total, total
    Retorna:
      (detailed_list, order_level_discount, totals_dict)
    """
    detailed = []
    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")
    total = Decimal("0.00")

    for item in cart:
        product = item["product"]
        qty = int(item.get("qty", 1) or 1)

        base_unit = money(Decimal(getattr(product, "price", 0) or 0))
        final_unit, _, _ = best_product_unit_price(product, qty=qty)

        line_subtotal = money(base_unit * qty)
        line_total = money(final_unit * qty)
        line_discount = money(line_subtotal - line_total)

        detailed.append({
            "product": product,
            "qty": qty,
            "unit_price": final_unit,
            "line_subtotal": line_subtotal,
            "line_discount": line_discount,
            "line_total": line_total,
        })

        subtotal += line_subtotal
        discount_total += line_discount
        total += line_total

    # Descuentos a nivel de orden (si en el futuro agregas reglas de orden)
    order_disc = Decimal("0.00")
    if order_level_promos:
        # Por ahora no hay reglas a nivel orden; conserva la firma de retorno
        order_disc = Decimal("0.00")

    totals = {
        "subtotal": money(subtotal),
        "discount_total": money(discount_total + order_disc),
        "total": money(total - order_disc) if order_disc > 0 else money(total),
    }
    return detailed, order_disc, totals
