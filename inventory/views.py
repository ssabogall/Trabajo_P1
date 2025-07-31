from django.shortcuts import render
from django.http import HttpResponse

def inventory(request):
    return HttpResponse("<h1>inventario</h1>")
