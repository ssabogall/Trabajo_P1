from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
import json



# Create your views here.
def product(request):
    # searchTerm = request.GET.get('searchProduct')
    # if searchTerm:
    #     products = product.objects.filter(title__icontains=searchTerm)
    # else:
    products = Product.objects.all()
    # return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': products})
    return render(request,"index.html",{ 'products': products})



def pos_view(request):
    # searchTerm = request.GET.get('searchProduct')
    # if searchTerm:
    #     products = product.objects.filter(title__icontains=searchTerm)
    # else:
    products = Product.objects.all()
    # return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': products})
    return render(request,"pos.html",{ 'products': products})



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