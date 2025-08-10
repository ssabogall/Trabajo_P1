from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product

# Create your views here.
def product(request):
    # searchTerm = request.GET.get('searchProduct')
    # if searchTerm:
    #     products = product.objects.filter(title__icontains=searchTerm)
    # else:
    products = Product.objects.all()
    # return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': products})
    return render(request,"index.html",{ 'products': products})