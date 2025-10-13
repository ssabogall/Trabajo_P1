from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem, Customer
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

def forms(request):
    # products = Product.objects.all()
    return render(request,"forms.html",{ })

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
def save_order_online(request):
    data = json.loads(request.body)
    print(data)
    customer = Customer.objects.create( cedula=data['customer']['cedula'], nombre=data['customer']['firstName'],correo="")
    order = Order.objects.create(customer = customer,paymentMethod='Transfer')
    
    for item in data['orders']:
        product = Product.objects.get(id=item['id'])
        OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])

    return JsonResponse({'status': 'success'})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'product_detail.html', {'product': product})