from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Sum, Count, F
from datetime import date, datetime
from django.db.models.functions import TruncDate
import json


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
    # print(data)

    print(orders[0]['id'])
    product_quantity = {}

    # count by ids
    for item in orders:
        product_quantity[item['id']] = product_quantity.get(item['id'], 0) + 1
    
    # # create order
    order = Order.objects.create(paymentMethod=orders[0]['paymentMethod'])

    # # create products and adding them to order
    for id,quantity in product_quantity.items():
        product = Product.objects.get(id=id)
        OrderItem.objects.create(order=order, product=product, quantity=quantity)

    return JsonResponse({'status': 'success'})

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