from django.shortcuts import render
from .models import RawMaterial

def inventory(request):
    materias_primas = RawMaterial.objects.all()
    return render(request, 'inventory/inventory.html', {
        'materias_primas': materias_primas
    })