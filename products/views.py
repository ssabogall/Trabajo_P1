from django.shortcuts import render,redirect
from django.http import HttpResponse
from inventory.models import Product, Order,OrderItem, Customer, Comment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
from inventory.utils.pagination_helper import PaginationHelper
import json


# Create your views here.
def forms(request):
    """
    Vista para mostrar el formulario de registro de clientes
    """
    return render(request, "forms.html", {})


def show_available_products(request):
    """
    Vista para mostrar los productos disponibles con búsqueda y paginación
    """
    q = (request.GET.get("q") or "").strip()
    base = Product.objects.filter(quantity__gt=0)

    if q:
        try:
            match = base.get(name__iexact=q)
            products_list = [match]  # solo 1
            results_count = 1
        except Product.DoesNotExist:
            products_list = []
            results_count = 0
        except MultipleObjectsReturned:
            match = base.filter(name__iexact=q).order_by("id").first()
            products_list = [match] if match else []
            results_count = len(products_list)

        return render(request, "products.html", {
            "products": products_list,
            "q": q,
            "results_count": results_count,
        })

    # Apply pagination for all products
    pagination = PaginationHelper(
        queryset=base,
        request=request,
        items_per_page=10,
        order_by='name'
    )

    context = {
        "products": pagination.get_items(),
        "q": q,
        "results_count": base.count(),
        **pagination.get_context()
    }
    return render(request, "products.html", context)


@csrf_exempt  # For testing only! Use proper CSRF token handling in production
@require_POST
def save_order_online(request):
    """
    Vista para guardar órdenes realizadas en línea
    """
    data = json.loads(request.body)
    print(data)
    customer = Customer.objects.create(
        cedula=data['customer']['cedula'],
        nombre=data['customer']['firstName'],
        correo=""
    )
    order = Order.objects.create(customer=customer, paymentMethod='Transfer')
    
    for item in data['orders']:
        product = Product.objects.get(id=item['id'])
        OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])

    return JsonResponse({'status': 'success'})


def product_detail(request, product_id):
    """
    Vista para mostrar los detalles de un producto individual
    """
    product = Product.objects.get(id=product_id)
    comments = product.comments.all()
    return render(request, 'product_detail.html', {'product': product, 'comments': comments})


@csrf_exempt
@require_POST
def add_comment(request, product_id):
    """
    Vista para agregar comentarios a un producto
    """
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
