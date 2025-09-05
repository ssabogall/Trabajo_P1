from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem, Customer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
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