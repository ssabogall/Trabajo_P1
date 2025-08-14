from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
import json



# Create your views here.
def product(request):
    products = Product.objects.all()
    return render(request,"products.html",{ 'products': products})



def pos(request):
    products = Product.objects.all()
    return render(request,"pos.html",{ 'products': products})


#se esta usando esta parte
def show_available_products(request):
    q = (request.GET.get("q") or "").strip()
    base = Product.objects.filter(quantity__gt=0)

    if q:
        try:
            match = base.get(name__iexact=q)
            products = [match]  # solo 1
        except Product.DoesNotExist:
            products = base.none()
        except MultipleObjectsReturned:
            match = base.filter(name__iexact=q).order_by("id").first()
            products = [match] if match else base.none()

        return render(request, "products.html", {
            "products": products,
            "q": q,
            "results_count": len(products),
        })

    products = base
    return render(request, "products.html", {
        "products": products,
        "q": q,
        "results_count": products.count(),
    })


@csrf_exempt  # For testing only! Use proper CSRF token handling in production
@require_POST
def save_order(request):
    data = json.loads(request.body)
    orders = data.get('orders', [])

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