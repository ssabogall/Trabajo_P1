from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem, Customer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
import json
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F, DecimalField, Value, ExpressionWrapper, DateTimeField, DateField, Count
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from datetime import date, datetime



MONEY = DecimalField(max_digits=12, decimal_places=2)
REVENUE_EXPR = ExpressionWrapper(F("product__price") * F("quantity"), output_field=MONEY)

def pos(request):
    products = Product.objects.all()
    return render(request,"pos.html",{ 'products': products})


def orders(request):
    orders = Order.objects.all()
    items = OrderItem.objects.all()
    return render(request,"orders.html",{ 'orders': orders,'items':items})

@csrf_exempt  # For testing only! Use proper CSRF token handling in production
@require_POST
def save_order(request):
    data = json.loads(request.body)
    orders = data.get('orders', [])

    print(orders[0]['id'])

     # print(data)

    print(orders[0]['cedula'])
    client = Customer.objects.create(cedula=orders[0]['cedula'],nombre=orders[0]['nombre'],correo=orders[0]['correo'])
    product_quantity = {}

    # count by ids
    for item in orders:
        product_quantity[item['id']] = product_quantity.get(item['id'], 0) + 1
    
    # # create order
    order = Order.objects.create(customer =client, paymentMethod=orders[0]['paymentMethod'])

    # # create products and adding them to order
    for id,quantity in product_quantity.items():
        product = Product.objects.get(id=id)
        OrderItem.objects.create(order=order, product=product, quantity=quantity)

    return JsonResponse({'status': 'success'})





def _revenue_expr():
    # ingreso = precio_actual_del_producto * cantidad del OrderItem
    return F("product__price") * F("quantity")

@staff_member_required
def baneton_dashboard(request):
    return render(request, "admin/baneton_dashboard.html")

def _sum_money(qs):
    return qs.aggregate(
        total=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY),
                       Value(Decimal("0.00")), output_field=MONEY)
    )["total"] or Decimal("0.00")

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

        items_today      = OrderItem.objects.filter(order__date__gte=start_today, order__date__lt=start_tomorrow)
        items_yesterday  = OrderItem.objects.filter(order__date__gte=start_yesterday, order__date__lt=start_today)
        range_last_7     = OrderItem.objects.filter(order__date__gte=last_7_start, order__date__lt=start_tomorrow)
        trunc_for_series = TruncDate("order__date", tzinfo=tz)
    else:  # DateField
        yesterday = today - timezone.timedelta(days=1)
        last_7_start = today - timezone.timedelta(days=6)

        items_today      = OrderItem.objects.filter(order__date=today)
        items_yesterday  = OrderItem.objects.filter(order__date=yesterday)
        range_last_7     = OrderItem.objects.filter(order__date__gte=last_7_start, order__date__lte=today)
        trunc_for_series = TruncDate("order__date")  # sin tzinfo para DateField

    # ---- KPIs base ----
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
        .annotate(amount=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY),
                                  Value(Decimal("0.00")), output_field=MONEY))
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
        .annotate(amount=Coalesce(Sum(REVENUE_EXPR, output_field=MONEY),
                                  Value(Decimal("0.00")), output_field=MONEY))
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
    prev7_start = last_7_start - timezone.timedelta(days=7)
    if isinstance(date_field, DateTimeField):
        prev_range = OrderItem.objects.filter(order__date__gte=prev7_start, order__date__lt=last_7_start)
    else:
        prev_range = OrderItem.objects.filter(order__date__gte=prev7_start, order__date__lt=last_7_start)

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
def daily_sales_report(request):
    """
    Vista para generar el reporte diario de ventas
    Cumple con el requerimiento PB-02
    """
    # Obtener la fecha solicitada o usar fecha actual
    report_date = request.GET.get('date')
    if report_date:
        try:
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        except ValueError:
            report_date = date.today()
    else:
        report_date = date.today()
    
    # Filtrar órdenes del día específico
    daily_orders = Order.objects.filter(
        date__date=report_date
    )
    
    # Calcular métricas del reporte según PB-02
    total_orders = daily_orders.count()
    
    # Calcular revenue total
    total_revenue = 0
    for order in daily_orders:
        total_revenue += order.total_amount()
    
    # Productos más vendidos del día
    product_sales = {}
    for order in daily_orders:
        for item in order.orderitem_set.all():
            if item.product.name not in product_sales:
                product_sales[item.product.name] = {
                    'total_quantity': 0,
                    'total_sales': 0
                }
            product_sales[item.product.name]['total_quantity'] += item.quantity
            product_sales[item.product.name]['total_sales'] += item.quantity * item.product.price
    
    # Ordenar productos por cantidad vendida
    most_sold_products = sorted(
        product_sales.items(), 
        key=lambda x: x[1]['total_quantity'], 
        reverse=True
    )[:5]
    
    # Ventas por método de pago
    payment_methods = {}
    for order in daily_orders:
        method = order.paymentMethod
        if method not in payment_methods:
            payment_methods[method] = {
                'count': 0,
                'total_amount': 0
            }
        payment_methods[method]['count'] += 1
        payment_methods[method]['total_amount'] += order.total_amount()
    
    # Calcular promedio por orden
    average_per_order = total_revenue / total_orders if total_orders > 0 else 0
    
    # Preparar contexto para el template
    context = {
        'report_date': report_date,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_per_order': average_per_order,
        'most_sold_products': most_sold_products,
        'payment_methods': payment_methods.items(),
        'daily_orders': daily_orders
    }
    
    return render(request, 'daily_sales_report.html', context)
