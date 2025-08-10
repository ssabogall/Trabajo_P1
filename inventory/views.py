from django.shortcuts import render
from django.http import HttpResponse

def inventory(request):
    return render(request, 'inventory/inventory.html')
