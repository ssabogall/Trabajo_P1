from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.admin.views.decorators import staff_member_required

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from django.db.models import Sum, Count, F, DecimalField, Value, ExpressionWrapper, DateTimeField, DateField
from django.db.models.functions import Coalesce, TruncDate

from datetime import date, datetime
from decimal import Decimal
import json

# Models
from inventory.models import Product, Order, OrderItem
# Customer es opcional: si tu app lo tiene, lo usaremos al guardar una orden
try:
    from inventory.models import Customer  # del primer código
    HAS_CUSTOMER = True
except Exception:
    HAS_CUSTOMER = False


# -------------------------------
# Utilidades comunes / agregados
# -------------------------------
MONEY = DecimalField(max_digits=12, decimal_places=2)
REVENUE_EXPR = ExpressionWrapper(F("product__price") * F("quantity"), output_field=MONEY)

def _sum_money(qs):
    """Suma de ingresos: precio actual del producto * cantidad."""
    return qs.aggregate(
        total=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY)
    )["total"] or Decimal("0.00")


# -------------------------------
# Vistas comunes de POS / Órdenes
# -------------------------------
def pos(request):
    products = Product.objects.all()
    return render(request, "pos.html", {"products": products})


def orders(request):
    orders_qs = Order.objects.all()
    items = OrderItem.objects.all()
    return render(request, "orders.html", {"orders": orders_qs, "items": items})



@csrf_exempt  
@require_POST
def save_order(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)

    orders = data.get("orders")
    if not orders:
        return JsonResponse({"status": "error", "message": "No hay productos en la orden"}, status=400)

    payment_method = data.get("paymentMethod", "Cash")
    customer_data = data.get("customer", {})

    # Crear cliente si se envió alguno
    customer_obj = None
    if HAS_CUSTOMER and (customer_data.get("cedula") or customer_data.get("nombre") or customer_data.get("correo")):
        customer_obj = Customer.objects.create(
            cedula=customer_data.get("cedula", ""),
            nombre=customer_data.get("nombre", ""),
            correo=customer_data.get("correo", ""),
        )

    # Crear la orden
    order = Order.objects.create(
        paymentMethod=payment_method,
        customer=customer_obj if HAS_CUSTOMER else None
    )

    # Crear OrderItems respetando cantidades
    for item in orders:
        pid = item.get("id")
        qty = int(item.get("quantity", 1))

        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            continue  # Ignora productos inválidos

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty
        )

    return JsonResponse({"status": "success", "order_id": order.id})





# ---------------------------------
# Reporte diario (PB-02 consolidado)
# ---------------------------------
def daily_sales_report(request):
    """
    Reporte diario de ventas (PB-02), compatible con DateField y DateTimeField.
    No depende de métodos del modelo; calcula todo vía agregaciones.
    """
    # Fecha solicitada o hoy
    report_date_param = request.GET.get("date")
    if report_date_param:
        try:
            report_date = datetime.strptime(report_date_param, "%Y-%m-%d").date()
        except ValueError:
            report_date = date.today()
    else:
        report_date = date.today()

    # Detectar tipo del campo Order.date
    date_field = Order._meta.get_field("date")
    tz = timezone.get_current_timezone()

    if isinstance(date_field, DateTimeField):
        start_day = timezone.make_aware(datetime.combine(report_date, datetime.min.time()), tz)
        end_day = start_day + timezone.timedelta(days=1)
        orders_day = Order.objects.filter(date__gte=start_day, date__lt=end_day)
        items_day = OrderItem.objects.filter(order__in=orders_day)
        trunc_date_expr = TruncDate("order__date", tzinfo=tz)
    else:  # DateField
        orders_day = Order.objects.filter(date=report_date)
        items_day = OrderItem.objects.filter(order__in=orders_day)
        trunc_date_expr = TruncDate("order__date")

    total_orders = orders_day.count()
    total_revenue = _sum_money(items_day)

    # Productos más vendidos (top 5)
    top_products_qs = (
        items_day.values("product__name")
        .annotate(
            total_quantity=Coalesce(Sum("quantity"), Value(0)),
            total_sales=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY),
        )
        .order_by("-total_quantity")[:5]
    )
    # Transformar a lista de tuplas como en el primer código
    most_sold_products = [
        (
            r["product__name"],
            {"total_quantity": int(r["total_quantity"]), "total_sales": r["total_sales"]},
        )
        for r in top_products_qs
    ]

    # Ventas por método de pago (se suma por OrderItem usando REVENUE_EXPR)
    pay_qs = (
        items_day.values("order__paymentMethod")
        .annotate(
            total_amount=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY),
            count=Count("order", distinct=True),
        )
        .order_by("-total_amount")
    )
    payment_methods = [(r["order__paymentMethod"] or "N/D", {"count": r["count"], "total_amount": r["total_amount"]}) for r in pay_qs]

    average_per_order = (total_revenue / total_orders) if total_orders else Decimal("0.00")

    context = {
        "report_date": report_date,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "average_per_order": average_per_order,
        "most_sold_products": most_sold_products,
        "payment_methods": payment_methods,  # iterable como en el primer código
        "daily_orders": orders_day,
    }
    return render(request, "daily_sales_report.html", context)


# ---------------------------------
# Dashboard / KPIs (del segundo código)
# ---------------------------------
@staff_member_required
def baneton_dashboard(request):
    return render(request, "admin/baneton_dashboard.html")


@staff_member_required
def baneton_kpis(request):
    tz = timezone.get_current_timezone()
    now = timezone.localtime()
    today = timezone.localdate()

    # Detectar tipo del campo Order.date
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
    else:  # DateField
        yesterday = today - timezone.timedelta(days=1)
        last_7_start = today - timezone.timedelta(days=6)

        items_today = OrderItem.objects.filter(order__date=today)
        items_yesterday = OrderItem.objects.filter(order__date=yesterday)
        range_last_7 = OrderItem.objects.filter(order__date__gte=last_7_start, order__date__lte=today)
        trunc_for_series = TruncDate("order__date")

    # KPIs base
    revenue_today = _sum_money(items_today)
    units_today = items_today.aggregate(units=Coalesce(Sum("quantity"), Value(0)))["units"] or 0

    # Top productos (hoy)
    top_qs = (
        items_today.values("product__name")
        .annotate(total_qty=Coalesce(Sum("quantity"), Value(0)))
        .order_by("-total_qty")[:5]
    )
    top_products = {
        "labels": [r["product__name"] for r in top_qs],
        "data": [int(r["total_qty"]) for r in top_qs],
    }

    # Distribución por método de pago (hoy)
    pay_qs = (
        items_today.values("order__paymentMethod")
        .annotate(
            amount=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY), Value(Decimal("0.00")), output_field=MONEY)
        )
        .order_by("-amount")
    )
    revenue_by_payment = {
        "labels": [r["order__paymentMethod"] or "N/D" for r in pay_qs],
        "data": [float(r["amount"]) for r in pay_qs],
    }

    # Series últimos 7 días
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

    # Tendencia (vs ayer)
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

    # Productos en tendencia (últimos 7 días vs 7 previos)
    prev7_start = (range_last_7.first().order.date if range_last_7.exists() else today)  # solo para evitar var no definida
    if isinstance(date_field, DateTimeField):
        prev7_start = last_7_start - timezone.timedelta(days=7)
        prev7_end = last_7_start
        prev_range = OrderItem.objects.filter(order__date__gte=prev7_start, order__date__lt=prev7_end)
    else:  # DateField
        prev7_start = today - timezone.timedelta(days=13)
        prev7_end = today - timezone.timedelta(days=6)
        prev_range = OrderItem.objects.filter(order__date__gte=prev7_start, order__date__lt=prev7_end)

    if isinstance(date_field, DateTimeField):
        prev_range = OrderItem.objects.filter(order__date__gte=prev7_start, order__date__lt=prev7_end)
    else:
        prev_range = OrderItem.objects.filter(order__date__gte=prev7_start, order__date__lt=prev7_end)

    curr7 = range_last_7.values("product__name").annotate(q=Coalesce(Sum("quantity"), Value(0)))
    prev7 = prev_range.values("product__name").annotate(q=Coalesce(Sum("quantity"), Value(0)))
    c_map = {r["product__name"]: int(r["q"]) for r in curr7}
    p_map = {r["product__name"]: int(r["q"]) for r in prev7}
    names = set(c_map) | set(p_map)

    trending = []
    for name in names:
        c = c_map.get(name, 0)
        p = p_map.get(name, 0)
        delta = c - p
        growth = ((delta / p) * 100) if p else (None if c == 0 else 100.0)
        trending.append({"name": name, "delta": delta, "growth": growth})
    trending.sort(key=lambda x: x["delta"], reverse=True)
    trending_products = {
        "labels": [t["name"] for t in trending[:5]],
        "delta": [t["delta"] for t in trending[:5]],
        "growth": [t["growth"] for t in trending[:5]],
    }

    # Compat: el template usa sales_by_day
    sales_by_day = revenue_by_day

    return JsonResponse({
        "revenue_today": float(revenue_today),
        "units_today": int(units_today),
        "top_products": top_products,
        "revenue_by_payment": revenue_by_payment,
        "revenue_by_day": revenue_by_day,
        "units_by_day": units_by_day,
        "trends": trends,
        "trending_products": trending_products,
        "sales_by_day": sales_by_day,
    })
