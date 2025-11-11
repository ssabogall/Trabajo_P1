from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from inventory.models import Product, Order, OrderItem, Customer, Comment, Rating
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.core.exceptions import MultipleObjectsReturned
from inventory.utils.pagination_helper import PaginationHelper
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
import json
from decimal import Decimal
from inventory.promo_utils import price_after_discount, get_active_promotion_for


# ===============================
# Listado / filtro de productos
# ===============================
def _filter_and_order_products(request):
    qs = Product.objects.all()
    # buscar por nombre (parcial, case-insensitive)
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    products = list(qs)

    # Función precio efectivo (aplicando promo si hay)
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
    only_promo = (request.GET.get('only_promo') or '') in ['on', '1', 'true', 'True']
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
    # (Dejamos tu lógica de filtrado/orden en esta vista)
    qs = Product.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    products = list(qs)

    def eff(p):
        return price_after_discount(p)

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
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

    only_promo = request.GET.get('only_promo') in ['on', '1', 'true', 'True']
    if only_promo:
        products = [p for p in products if get_active_promotion_for(p)]

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
    return render(request, "forms.html", {})


def show_available_products(request):
    # usar helper de filtrado/orden y mantener valores elegidos
    ctx = _filter_and_order_products(request)
    return render(request, "products.html", ctx)

    # Nota: tu bloque de paginación quedaba tras el return; lo mantengo sin tocar.


# ============================================
# Guardar órdenes realizadas en línea (API)
# ============================================
@csrf_exempt  # For testing only! Usa CSRF real en producción si es necesario
@require_POST
def save_order_online(request):
    """
    Crea/actualiza cliente y guarda una orden con sus ítems.
    Estructura esperada (ejemplo):
    {
      "customer": {"cedula": "109", "firstName": "Carlos", "email": "c@c.com"},
      "orders": [{"id": 16, "quantity": 1}, {"id": 5, "quantity": 2}]
    }
    """
    data = json.loads(request.body)

    cust_data = data.get('customer', {}) or {}
    cedula = str(cust_data.get('cedula', '')).strip()
    first_name = (cust_data.get('firstName') or '').strip()
    email = (cust_data.get('email') or '').strip()

    if not cedula:
        return JsonResponse({'status': 'error', 'message': 'Falta cédula del cliente'}, status=400)

    # [[MEJORA]] Reutiliza el mismo Customer si ya existe (evita duplicados)
    customer, _ = Customer.objects.get_or_create(
        cedula=cedula,
        defaults={'nombre': first_name or cedula, 'correo': email}
    )
    # Si existe pero queremos actualizar correo/nombre si vienen:
    changed = False
    if first_name and (customer.nombre or '') != first_name:
        customer.nombre = first_name
        changed = True
    if email and (customer.correo or '') != email:
        customer.correo = email
        changed = True
    if changed:
        customer.save()

    order = Order.objects.create(customer=customer, paymentMethod='Transfer')

    for item in data.get('orders', []):
        pid = item.get('id')
        qty = int(item.get('quantity', 1) or 1)
        product = Product.objects.get(id=pid)
        OrderItem.objects.create(order=order, product=product, quantity=qty)

    return JsonResponse({'status': 'success', 'order_id': order.id})


# ===============================
# Detalle de producto + ratings
# ===============================
def product_detail(request, product_id):
    """
    Muestra el detalle del producto + comentarios + datos de rating.
    """
    product = Product.objects.get(id=product_id)
    comments = product.comments.all()

    avg_rating = product.ratings.aggregate(avg=Avg('stars'))['avg'] or 0
    my_rating = 0
    can_rate = False

    if request.user.is_authenticated:
        customer = _get_customer_for_user(request.user)
        if customer:
            existing = Rating.objects.filter(product=product, customer=customer).first()
            my_rating = existing.stars if existing else 0

            # Verificación PB-27: el producto debe pertenecer a alguna orden del customer
            has_bought = OrderItem.objects.filter(order__customer=customer, product=product).exists()
            can_rate = has_bought or request.user.is_superuser  # [[CAMBIO PARA ADMIN]]

    ctx = {
        'product': product,
        'comments': comments,
        'avg_rating': avg_rating,
        'my_rating': my_rating,
        'can_rate': can_rate,
    }
    return render(request, 'product_detail.html', ctx)


@csrf_exempt
@require_POST
def add_comment(request, product_id):
    """
    Agrega comentarios a un producto
    """
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


# ============================================
# Helpers / Endpoints para calificaciones
# ============================================

def _get_customer_for_user(user):
    """
    [[ARREGLADO PB-27]] Mapea request.user -> inventory.Customer de forma robusta.
    1) Si existe CustomerProfile -> úsalo.
    2) Si no, busca Customer por correo del usuario.
    3) Si no, busca por nombre completo / username / cédula == username.
    4) Si no existe, crea un Customer y lo devuelve (esto habilita también a admin).
    """
    # 1) CustomerProfile (asumimos related_name='customer_profile')
    try:
        profile = getattr(user, "customer_profile", None)
        if profile and getattr(profile, "customer_id", None):
            return profile.customer
    except Exception:
        pass

    # 2) Por correo
    if getattr(user, "email", None):
        cust = Customer.objects.filter(correo__iexact=user.email).first()
        if cust:
            return cust

    # 3) Por nombre/username
    full_name = (user.get_full_name() or "").strip()
    if full_name:
        cust = Customer.objects.filter(nombre__iexact=full_name).first()
        if cust:
            return cust

    cust = Customer.objects.filter(
        Q(nombre__iexact=user.username) | Q(cedula__iexact=str(user.username))
    ).first()
    if cust:
        return cust

    # 4) Crear si no existe ninguno
    return Customer.objects.create(
        cedula=str(user.id),
        nombre=full_name or user.username,
        correo=user.email or None
    )


@csrf_exempt
@require_POST
@login_required
def rate_product(request, product_id):
    """
    Crea/actualiza la calificación (1..5) del usuario para un producto.
    Regla PB-27: Solo si el producto pertenece a una orden del mismo customer.
    [[CAMBIO PARA ADMIN]]: si es superusuario, también puede calificar (útil en pruebas).
    Respuesta JSON: { ok, my_rating, avg_rating } (o { ok: False, error })
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Producto no encontrado'}, status=404)

    try:
        stars = int(request.POST.get('stars', 0))
    except ValueError:
        stars = 0
    stars = max(1, min(5, stars))  # clamp 1..5

    customer = _get_customer_for_user(request.user)
    if not customer:
        return JsonResponse({'ok': False, 'error': 'Perfil de cliente no asociado'}, status=400)

    has_bought = OrderItem.objects.filter(order__customer=customer, product=product).exists()

    # Si quieres hacer cumplir PB-27 estrictamente, quita el "and not request.user.is_superuser"
    if not has_bought and not request.user.is_superuser:
        return JsonResponse({'ok': False, 'error': 'Solo puedes calificar productos de tus pedidos'}, status=403)

    rating, _ = Rating.objects.update_or_create(
        product=product, customer=customer, defaults={'stars': stars}
    )
    avg = product.ratings.aggregate(avg=Avg('stars'))['avg'] or 0
    return JsonResponse({'ok': True, 'my_rating': rating.stars, 'avg_rating': round(float(avg), 2)})
