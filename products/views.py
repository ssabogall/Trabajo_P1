from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Product
from django.core.exceptions import MultipleObjectsReturned



# Create your views here.
def product(request):
    # searchTerm = request.GET.get('searchProduct')
    # if searchTerm:
    #     products = product.objects.filter(title__icontains=searchTerm)
    # else:
    products = Product.objects.all()
    # return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': products})
    return render(request,"index.html",{ 'products': products})


#se esta usando esta parte
def show_available_products(request):
    q = (request.GET.get("q") or "").strip()
    base = Product.objects.filter(stock__gt=0)

    if q:
        try:
            match = base.get(name__iexact=q)
            products = [match]  # solo 1
        except Product.DoesNotExist:
            products = base.none()
        except MultipleObjectsReturned:
            match = base.filter(name__iexact=q).order_by("id").first()
            products = [match] if match else base.none()

        return render(request, "index.html", {
            "products": products,
            "q": q,
            "results_count": len(products),
        })

    products = base
    return render(request, "index.html", {
        "products": products,
        "q": q,
        "results_count": products.count(),
    })