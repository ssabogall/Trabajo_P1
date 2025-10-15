from django.shortcuts import render,redirect
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem, Customer, Comment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
import json
from decimal import Decimal
from inventory.promo_utils import price_after_discount, get_active_promotion_for

# Create your views here.


# [[AGREGADO]] Helper de filtrado/orden usando precio efectivo (con promo)
def _filter_and_order_products(request):
    qs = Product.objects.all()
    # buscar por nombre (parcial, case-insensitive)
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    products = list(qs)

    # Función precio efectivo
    def eff(p):
        return price_after_discount(p)

    # filtros de precio
    min_price = (request.GET.get('min_price') or '').strip()
    max_price = (request.GET.get('max_price') or '').strip()
    if min_price:
        try:
            m = Decimal(min_price)
            products = [p for p in products if eff(p) >= m]
        except Exception:
            pass
    if max_price:
        try:
            M = Decimal(max_price)
            products = [p for p in products if eff(p) <= M]
        except Exception:
            pass

    # solo promoción
    only_promo = (request.GET.get('only_promo') or '') in ['on','1','true','True']

    if only_promo:
        products = [p for p in products if get_active_promotion_for(p)]

    # orden
    order = (request.GET.get('order') or 'name_az')
    if order == 'price_asc':
        products.sort(key=lambda p: (eff(p), p.name.lower()))
    elif order == 'price_desc':
        products.sort(key=lambda p: (eff(p), p.name.lower()), reverse=True)
    else:
        products.sort(key=lambda p: p.name.lower())

    ctx = {
        'products': products,
        'q': q,
        'min_price': min_price,
        'max_price': max_price,
        'order': order,
        'only_promo': '1' if only_promo else '',
    }
    return ctx

def product(request):
    # [[MODIFICADO]] Agregado filtrado y ordenamiento por GET params (q, min_price, max_price, only_promo, order)
    qs = Product.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    # Convert to list for Python-side filtering by precio efectivo
    products = list(qs)

    # Filtros por precio mínimo y máximo usando precio efectivo (con promo)
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    def eff(p): 
        return price_after_discount(p)

    if min_price:
        try:
            m = Decimal(min_price)
            products = [p for p in products if eff(p) >= m]
        except Exception:
            pass
    if max_price:
        try:
            M = Decimal(max_price)
            products = [p for p in products if eff(p) <= M]
        except Exception:
            pass

    # Solo productos en promoción
    only_promo = request.GET.get('only_promo') in ['on', '1', 'true', 'True']
    if only_promo:
        products = [p for p in products if get_active_promotion_for(p)]

    # Orden: nombre A-Z (default), precio asc, precio desc (con promo)
    order = request.GET.get('order', 'name_az')
    if order == 'price_asc':
        products.sort(key=lambda p: (eff(p), p.name.lower()))
    elif order == 'price_desc':
        products.sort(key=lambda p: (eff(p), p.name.lower()), reverse=True)
    else:
        products.sort(key=lambda p: p.name.lower())

    ctx = {
        'products': products,
        'q': q,
        'min_price': min_price,
        'max_price': max_price,
        'order': order,
        'only_promo': '1' if only_promo else '',
    }
    return render(request, "products.html", ctx)

def forms(request):
    # products = Product.objects.all()
    return render(request,"forms.html",{})

#se esta usando esta parte
def show_available_products(request):
    # [[MODIFICADO]] usar helper de filtrado/orden y mantener valores elegidos
    ctx = _filter_and_order_products(request)
    return render(request, "products.html", ctx)

    products = base
    return render(request, "products.html", {
        "products": products,
        "q": q,
        "results_count": products.count(),
    })



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

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    comments = product.comments.all()
    return render(request, 'product_detail.html', {'product': product,'comments': comments})


@csrf_exempt
@require_POST
def add_comment(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        name = request.POST.get('name')
        comment_text = request.POST.get('comment')
        
        if name and comment_text:
            Comment.objects.create(
                product=product,
                name=name,
                text=comment_text
            )
        return redirect('product_detail', product_id=product_id)
    
    return redirect('products_home')