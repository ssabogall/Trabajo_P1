from django.shortcuts import render
from django.http import HttpResponse
from .models import Product

def inventory(request):
    products = Product.objects.all() 
    return render(request, 'inventory.html', {'products': products})
