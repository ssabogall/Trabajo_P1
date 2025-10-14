from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

from django.utils import timezone
from django.db.models import Sum, Count, F, DecimalField, Value, ExpressionWrapper, DateTimeField
from django.db.models.functions import Coalesce, TruncDate

from datetime import date, datetime
from decimal import Decimal
import json
from collections import defaultdict

# Models
from products.models import Product
from inventory.models import Order, OrderItem
try:
    from inventory.models import Customer
    HAS_CUSTOMER = True
except Exception:
    HAS_CUSTOMER = False

# Descuentos/Promos
from inventory.services.discounts import best_product_unit_price, price_cart

# -------------------------------
# Helpers
# -------------------------------
MONEY = DecimalField(max_digits=12, decimal_places=2)
REVENUE_EXPR = ExpressionWrapper(
    (Coalesce(F("unit_price"), F("product__price"))) * F("quantity"),
    output_field=MONEY,
)

def _sum_money(qs):
    return qs.aggregate(
        total=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY)
    )["total"] or Decimal("0.00")


# -------------------------------
# POS UI
# -------------------------------
def pos(request):
    products = list(Product.objects.all())
    for p in products:
        eff, _, _ = best_product_unit_price(p, qty=1)
        setattr(p, "final_price", eff)
    return render(request, "pos.html", {"products": products})


def orders(request):
    """
    Lista las órdenes mostrando:
      - Fecha/hora (usa __str__ de Order)
      - Método de pago
      - Productos (uno por línea: 'Nombre xCantidad')
      - Total (suma line_total o, si falta, unit_price*qty o price*qty)
      - Cliente (template ya muestra nombre y cédula)
    """
    orders_qs = (
        Order.objects
        .select_related("customer")
        .prefetch_related("orderitem_set__product")
        .order_by("-date")
    )

    # Inyectar 'products' y 'total_amount' a cada Order
    for o in orders_qs:
        items = list(o.orderitem_set.all())

        total = Decimal("0.00")
        lines = []
        for it in items:
            if it.line_total and it.line_total != Decimal("0.00"):
                line_total = it.line_total
            elif it.unit_price and it.unit_price != Decimal("0.00"):
                line_total = it.unit_price * it.quantity
            else:
                line_total = Decimal(getattr(it.product, "price", 0)) * it.quantity

            total += line_total
            pname = getattr(it.product, "name", str(it.product))
            lines.append(f"{pname} x{it.quantity}")

        setattr(o, "products", "\n".join(lines))
        setattr(o, "total_amount", total)

    return render(request, "orders.html", {"orders": orders_qs})


# -------------------------------
# Guardar orden (POS)
# -------------------------------
@csrf_exempt   # en producción usar CSRF correctamente
@require_POST
def save_order(request):
    """
    Espera JSON:
    {
      "orders": [{"id": <product_id>, "quantity": <int>}, ...],
      "paymentMethod": "Cash" | "Card" | "Transfer",
      "customer": {"cedula": "...", "nombre"/"firstName": "...", "correo": "..."}
    }
    """
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)

    raw_items = data.get("orders") or []
    if not raw_items:
        return JsonResponse({"status": "error", "message": "No hay items en la orden"}, status=400)

    # 1) Normalizar cantidades por producto (acumular si vienen repetidos)
    qty_map = defaultdict(int)
    for it in raw_items:
        try:
            pid = int(it.get("id"))
            q = int(it.get("quantity", 1))
        except (TypeError, ValueError):
            continue
        if pid and q > 0:
            qty_map[pid] += q

    if not qty_map:
        return JsonResponse({"status": "error", "message": "Carrito vacío"}, status=400)

    # 2) Cliente y método de pago
    payment_method = (data.get("paymentMethod") or "Cash").strip() or "Cash"

    customer_obj = None
    if HAS_CUSTOMER:
        cust = data.get("customer") or {}
        cedula = (cust.get("cedula") or "").strip()
        nombre = (cust.get("nombre") or cust.get("firstName") or "").strip()
        correo = (cust.get("correo") or "").strip()
        if cedula or nombre or correo:
            customer_obj = Customer.objects.create(
                cedula=cedula, nombre=nombre, correo=correo
            )

    # 3) Orden
    order = Order.objects.create(
        paymentMethod=payment_method,
        **({"customer": customer_obj} if customer_obj else {})
    )

    # 4) Valorar carrito con promos
    products_map = {p.id: p for p in Product.objects.filter(id__in=qty_map.keys())}
    cart = [{"product": products_map[pid], "qty": qty} for pid, qty in qty_map.items() if pid in products_map]

    detailed, order_disc, totals = price_cart(cart, order_level_promos=True)

    # Fallback por si no llega 'totals' completo
    if not totals or any(k not in totals for k in ("subtotal", "discount_total", "total")):
        subtotal = Decimal("0.00")
        discount_total = Decimal("0.00")
        total = Decimal("0.00")
        detailed = []
        for pid, qty in qty_map.items():
            prod = products_map.get(pid)
            if not prod:
                continue
            unit, disc_unit, _ = best_product_unit_price(prod, qty=qty)
            line_sub = Decimal(prod.price) * qty
            line_tot = Decimal(unit) * qty
            line_disc = line_sub - line_tot
            subtotal += line_sub
            discount_total += line_disc
            total += line_tot
            detailed.append({
                "product": prod, "qty": qty, "unit_price": unit,
                "line_subtotal": line_sub, "line_discount": line_disc, "line_total": line_tot
            })
        totals = {"subtotal": subtotal, "discount_total": discount_total, "total": total}

    # 5) Guardar líneas
    items_to_create = []
    for d in detailed:
        items_to_create.append(OrderItem(
            order=order,
            product=d["product"],
            quantity=int(d["qty"]),
            unit_price=Decimal(d["unit_price"]),
            line_subtotal=Decimal(d["line_subtotal"]),
            line_discount=Decimal(d["line_discount"]),
            line_total=Decimal(d["line_total"]),
        ))
    OrderItem.objects.bulk_create(items_to_create)

    # 6) Guardar totales en la orden
    order.subtotal = Decimal(totals["subtotal"])
    order.discount_total = Decimal(totals["discount_total"])
    order.total = Decimal(totals["total"])
    order.save(update_fields=["subtotal", "discount_total", "total"])

    return JsonResponse({
        "status": "success",
        "order_id": order.id,
        "totals": {
            "subtotal": str(order.subtotal),
            "discount_total": str(order.discount_total),
            "total": str(order.total),
        }
    })


# ---------------------------------
# Reporte diario
# ---------------------------------
def daily_sales_report(request):
    report_date_param = request.GET.get("date")
    if report_date_param:
        try:
            report_date = datetime.strptime(report_date_param, "%Y-%m-%d").date()
        except ValueError:
            report_date = date.today()
    else:
        report_date = date.today()

    date_field = Order._meta.get_field("date")
    tz = timezone.get_current_timezone()

    # Filtrar órdenes e ítems del día
    if isinstance(date_field, DateTimeField):
        start_day = timezone.make_aware(datetime.combine(report_date, datetime.min.time()), tz)
        end_day = start_day + timezone.timedelta(days=1)
        orders_day = Order.objects.filter(date__gte=start_day, date__lt=end_day)
        items_day = OrderItem.objects.filter(order__in=orders_day)
    else:
        orders_day = Order.objects.filter(date=report_date)
        items_day = OrderItem.objects.filter(order__in=orders_day)

    # Métricas agregadas
    total_orders = orders_day.count()
    total_revenue = _sum_money(items_day)

    # Top productos (cantidad y ventas)
    top_products_qs = (
        items_day.values("product__name")
        .annotate(
            total_quantity=Coalesce(Sum("quantity"), Value(0)),
            total_sales=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY),
        )
        .order_by("-total_quantity")[:5]
    )
    most_sold_products = [
        (
            r["product__name"],
            {"total_quantity": int(r["total_quantity"]), "total_sales": r["total_sales"]},
        )
        for r in top_products_qs
    ]

    # Métodos de pago: total y conteo de órdenes
    pay_qs = (
        items_day.values("order__paymentMethod")
        .annotate(
            total_amount=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY),
            count=Count("order", distinct=True),
        )
        .order_by("-total_amount")
    )
    payment_methods = [
        (r["order__paymentMethod"] or "N/D", {"count": r["count"], "total_amount": r["total_amount"]})
        for r in pay_qs
    ]

    # ---- Enriquecer órdenes del día con productos y total ----
    # Mapa: order_id -> "Nombre xCantidad\n..."
    product_lines = defaultdict(list)
    for it in items_day.select_related("product"):
        pname = getattr(it.product, "name", str(it.product))
        product_lines[it.order_id].append(f"{pname} x{it.quantity}")

    # Mapa: order_id -> total
    totals_by_order = {
        r["order_id"]: r["total"]
        for r in items_day.values("order_id").annotate(
            total=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY)
        )
    }

    # Prefetch para mostrar cliente en otras pantallas si se requiere
    orders_day = orders_day.select_related("customer").order_by("date")

    # Inyectar atributos usados por la plantilla
    for o in orders_day:
        setattr(o, "products", "\n".join(product_lines.get(o.id, [])))
        setattr(o, "total_amount", totals_by_order.get(o.id, Decimal("0.00")))

    average_per_order = (total_revenue / total_orders) if total_orders else Decimal("0.00")

    context = {
        "report_date": report_date,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "average_per_order": average_per_order,
        "most_sold_products": most_sold_products,
        "payment_methods": payment_methods,
        "daily_orders": orders_day,
    }
    return render(request, "daily_sales_report.html", context)


# ---------------------------------
# Dashboard / KPIs
# ---------------------------------
@staff_member_required
def baneton_dashboard(request):
    return render(request, "admin/baneton_dashboard.html")


@staff_member_required
def baneton_kpis(request):
    tz = timezone.get_current_timezone()
    now = timezone.localtime()
    today = timezone.localdate()

    date_field = Order._meta.get_field("date")
    if isinstance(date_field, DateTimeField):
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_tomorrow = start_today + timezone.timedelta(days=1)
        start_yesterday = start_today - timezone.timedelta(days=1)
        last_7_start = start_today - timezone.timedelta(days=6)

        items_today = OrderItem.objects.filter(order__date__gte=start_today, order__date__lt=start_tomorrow)
        items_yesterday = OrderItem.objects.filter(order__date__gte=start_yesterday, order__date__lt=start_today)
        range_last_7 = OrderItem.objects.filter(order__date__gte=last_7_start, order__date__lt=start_tomorrow)
        trunc_for_series = TruncDate("order__date", tzinfo=tz)
    else:
        yesterday = today - timezone.timedelta(days=1)
        last_7_start = today - timezone.timedelta(days=6)

        items_today = OrderItem.objects.filter(order__date=today)
        items_yesterday = OrderItem.objects.filter(order__date=yesterday)
        range_last_7 = OrderItem.objects.filter(order__date__gte=last_7_start, order__date__lte=today)
        trunc_for_series = TruncDate("order__date")

    revenue_today = _sum_money(items_today)
    units_today = items_today.aggregate(units=Coalesce(Sum("quantity"), Value(0)))["units"] or 0

    top_qs = (
        items_today.values("product__name")
        .annotate(total_qty=Coalesce(Sum("quantity"), Value(0)))
        .order_by("-total_qty")[:5]
    )
    top_products = {
        "labels": [r["product__name"] for r in top_qs],
        "data": [int(r["total_qty"]) for r in top_qs],
    }

    pay_qs = (
        items_today.values("order__paymentMethod")
        .annotate(amount=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY))
        .order_by("-amount")
    )
    revenue_by_payment = {
        "labels": [r["order__paymentMethod"] or "N/D" for r in pay_qs],
        "data": [float(r["amount"]) for r in pay_qs],
    }

    by_day_rev = (
        range_last_7.annotate(day=trunc_for_series)
        .values("day")
        .annotate(amount=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY))
        .order_by("day")
    )
    revenue_by_day = {
        "labels": [d["day"].strftime("%d-%b") for d in by_day_rev],
        "data": [float(d["amount"]) for d in by_day_rev],
    }

    by_day_units = (
        range_last_7.annotate(day=trunc_for_series)
        .values("day")
        .annotate(units=Coalesce(Sum("quantity"), Value(0)))
        .order_by("day")
    )
    units_by_day = {
        "labels": [d["day"].strftime("%d-%b") for d in by_day_units],
        "data": [int(d["units"]) for d in by_day_units],
    }

    revenue_yesterday = _sum_money(items_yesterday)
    units_yesterday = items_yesterday.aggregate(units=Coalesce(Sum("quantity"), Value(0)))["units"] or 0

    def pct(curr, prev):
        return float(((curr - prev) / prev) * 100) if prev else None

    trends = {
        "revenue_change_pct": pct(revenue_today, revenue_yesterday),
        "units_change_pct": pct(units_today, units_yesterday),
        "revenue_yesterday": float(revenue_yesterday),
        "units_yesterday": int(units_yesterday),
    }

    sales_by_day = revenue_by_day

    return JsonResponse({
        "revenue_today": float(revenue_today),
        "units_today": int(units_today),
        "top_products": top_products,
        "revenue_by_payment": revenue_by_payment,
        "revenue_by_day": revenue_by_day,
        "units_by_day": units_by_day,
        "trends": trends,
        "trending_products": {"labels": [], "delta": [], "growth": []},
        "sales_by_day": sales_by_day,
    })
