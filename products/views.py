from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem, Customer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
from inventory.utils.pagination_helper import PaginationHelper
import json



# Create your views here.
def product(request):
    # Apply pagination
    queryset = Product.objects.all()
    pagination = PaginationHelper(
        queryset=queryset,
        request=request,
        items_per_page=10,
        order_by='name'  # Alphabetical order
    )

    context = {
        'products': pagination.get_items(),
        **pagination.get_context()
    }
    return render(request, "products.html", context)

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
            products_list = [match]  # solo 1
            results_count = 1
        except Product.DoesNotExist:
            products_list = []
            results_count = 0
        except MultipleObjectsReturned:
            match = base.filter(name__iexact=q).order_by("id").first()
            products_list = [match] if match else []
            results_count = len(products_list)

        return render(request, "products.html", {
            "products": products_list,
            "q": q,
            "results_count": results_count,
        })

    # Apply pagination for all products
    pagination = PaginationHelper(
        queryset=base,
        request=request,
        items_per_page=10,
        order_by='name'
    )

    context = {
        "products": pagination.get_items(),
        "q": q,
        "results_count": base.count(),
        **pagination.get_context()
    }
    return render(request, "products.html", context)



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
