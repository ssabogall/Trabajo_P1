from django.shortcuts import render
from .models import Product, RawMaterial

def inventory(request):
    productos = Product.objects.all()
    materias_primas = RawMaterial.objects.all()
    return render(request, 'inventory/inventory.html', {
        'productos': productos,
        'materias_primas': materias_primas
    })