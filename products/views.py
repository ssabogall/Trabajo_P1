from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned, FieldDoesNotExist, FieldError
from django.db.models import Q

from products.models import Product
from inventory.models import Order, OrderItem, Customer
from inventory.services.discounts import best_product_unit_price, price_cart

import json

# ---------------------------
# Páginas catálago / filtros
# ---------------------------
def product(request):
    products_qs = Product.objects.all()
    products = list(products_qs)
    for p in products:
        final_unit, disc_u, percent = best_product_unit_price(p, qty=1)
        setattr(p, "final_price", final_unit)
        setattr(p, "discount_percent", percent)
    return render(request, "products.html", {"products": products})

def forms(request):
    return render(request, "forms.html", {})

def show_available_products(request):
    def has_field(model, field_name: str) -> bool:
        try:
            model._meta.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False

    qs = Product.objects.all()
    if has_field(Product, "quantity"):
        qs = qs.filter(quantity__gt=0)

    q        = (request.GET.get("q") or "").strip()
    pmin     = request.GET.get("price_min")
    pmax     = request.GET.get("price_max")
    promo    = request.GET.get("promotion")
    type_val = request.GET.get("type")
    cats     = request.GET.getlist("category")
    order    = request.GET.get("order", "name")

    if q:
        try:
            match = qs.get(name__iexact=q)
            qs = Product.objects.filter(pk=match.pk)
        except Product.DoesNotExist:
            qs = qs.filter(name__icontains=q)
        except MultipleObjectsReturned:
            match = qs.filter(name__iexact=q).order_by("id").first()
            qs = Product.objects.filter(pk=match.pk) if match else qs.none()

    if has_field(Product, "price"):
        if pmin:
            try: qs = qs.filter(price__gte=float(pmin))
            except ValueError: pass
        if pmax:
            try: qs = qs.filter(price__lte=float(pmax))
            except ValueError: pass

    if promo == "1" and has_field(Product, "promotion"):
        qs = qs.filter(promotion=True)

    if type_val:
        applied = False
        for lookup in [
            "product_type__iexact", "type__iexact", "tipo__iexact",
            "kind__iexact", "category__slug__iexact", "category__name__iexact",
        ]:
            try:
                qs = qs.filter(**{lookup: type_val})
                applied = True
                break
            except (FieldError, ValueError):
                continue
        if not applied:
            synonyms = {
                "sanduche": ["sanduche"],
                "pan_tajada": ["tajada", "tajadas", "pan tajada"],
                "otro": ["otro"],
            }
            keywords = synonyms.get(type_val, [type_val])
            name_q = Q()
            for kw in keywords:
                name_q |= Q(name__icontains=kw)
            qs = qs.filter(name_q)

    if cats:
        try:
            qs = qs.filter(category__slug__in=cats)
        except Exception:
            qs = qs.filter(category_id__in=cats)

    if order:
        try: qs = qs.order_by(order)
        except Exception: qs = qs.order_by("name")

    products = list(qs)
    for p in products:
        final_unit, disc_u, percent = best_product_unit_price(p, qty=1)
        setattr(p, "final_price", final_unit)
        setattr(p, "discount_percent", percent)

    return render(request, "products.html", {
        "products": products,
        "q": q,
        "results_count": len(products),
        "selected": {
            "q": q, "pmin": pmin, "pmax": pmax,
            "promo": promo, "type": type_val, "cats": cats, "order": order
        }
    })

# ---------------------------------------------------
# Helper: leer payload (form-data o JSON) del carrito
# ---------------------------------------------------
def _read_order_payload(request):
    data = {}
    ctype = (request.content_type or "").lower()
    if "application/json" in ctype:
        # JSON (fetch)
        try:
            data = json.loads(request.body or "{}")
        except Exception:
            data = {}
    else:
        # POST normal (form-data)
        data["paymentMethod"] = request.POST.get("paymentMethod", "Transfer")
        data["customer"] = {
            "cedula": request.POST.get("cedula", ""),
            "firstName": request.POST.get("firstName") or request.POST.get("nombre", ""),
            "correo": request.POST.get("correo", ""),
        }
        raw = request.POST.get("orders") or request.POST.get("cart") or "[]"
        try:
            data["orders"] = json.loads(raw)
        except Exception:
            data["orders"] = []
    # Normalizar items
    norm_orders = []
    for it in data.get("orders", []):
        try:
            pid = int(it.get("id") if isinstance(it, dict) else it["product"])
            qty = int(it.get("quantity", 1))
            if qty > 0:
                norm_orders.append({"id": pid, "quantity": qty})
        except Exception:
            continue
    data["orders"] = norm_orders
    return data

# ------------------------------
# Guardar orden (online / forms)
# ------------------------------
@csrf_exempt   # si quitas esto, agrega CSRF en JS
@require_POST
def save_order_online(request):
    """
    Persiste una orden desde Products (carrito o formulario), con
    precios de líneas ya rebajados por promoción y totales calculados.
    Acepta:
      - JSON: {customer:{...}, orders:[{id,quantity}], paymentMethod}
      - form-data: inputs 'orders' (JSON string), 'cedula', 'firstName|nombre', 'correo', 'paymentMethod'
    """
    data = _read_order_payload(request)

    if not data.get("orders"):
        return JsonResponse({"status": "error", "message": "Carrito vacío"}, status=400)

    # 1) Cliente y orden
    cust = data.get("customer", {}) or {}
    customer = Customer.objects.create(
        cedula=cust.get("cedula", ""),
        nombre=cust.get("firstName", ""),
        correo=cust.get("correo", ""),
    )
    order = Order.objects.create(
        customer=customer,
        paymentMethod=data.get("paymentMethod", "Transfer"),
    )

    # 2) Valorar carrito con servicio de descuentos
    cart = []
    for item in data["orders"]:
        product = Product.objects.get(id=item["id"])
        qty = int(item.get("quantity", 1))
        cart.append({"product": product, "qty": qty})

    detailed, order_disc, totals = price_cart(cart, order_level_promos=True)

    # 3) Guardar líneas con precio efectivo + totales de línea
    for d in detailed:
        OrderItem.objects.create(
            order=order,
            product=d["product"],
            quantity=d["qty"],
            unit_price=d["unit_price"],
            line_subtotal=d["line_subtotal"],
            line_discount=d["line_discount"],
            line_total=d["line_total"],
        )

    # 4) Persistir totales de la orden
    order.subtotal = totals["subtotal"]
    order.discount_total = totals["discount_total"]
    order.total = totals["total"]
    order.save(update_fields=["subtotal", "discount_total", "total"])

    # Responder (si vino por formulario, puedes redirigir)
    if "application/json" in (request.content_type or "").lower():
        return JsonResponse({"status": "success", "order_id": order.id, "totals": totals})
    return redirect("/products/?ok=1")
