from django.shortcuts import render
from django.http import HttpResponse
from .models import Product

def inventory(request):
    return render(request, 'inventory/inventory.html')
def available_products(request):
    products = Product.objects.filter(stock__gt=0)
    return render(request, "inventory/inventory.html", {'products': products})
