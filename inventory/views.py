from django.shortcuts import get_object_or_404, redirect, render
from .models import RawMaterial
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.utils.timezone import now, timedelta
from .utils.pagination_helper import PaginationHelper
from .models import MovimientosInventario
from django.db import models

def inventory(request):
    from inventory.models import Product
    
    today = now().date()
    soon = today + timedelta(days=5)
    expiring_soon = RawMaterial.objects.filter(exp_date__lte=soon, exp_date__gte=today)

    dismissed = request.GET.get("dismissed") == "1"
    show_modal = bool(expiring_soon) and not dismissed

    # Check for low stock products
    low_stock_count = Product.objects.filter(
        quantity__lt=models.F('reorder_threshold')
    ).count()

    # Apply pagination
    queryset = RawMaterial.objects.all()
    pagination = PaginationHelper(
        queryset=queryset,
        request=request,
        items_per_page=10,
        order_by='name'  # Alphabetical order
    )

    context = {
        "materias_primas": pagination.get_items(),
        "show_modal": show_modal,
        "low_stock_count": low_stock_count,
        **pagination.get_context()  # Add pagination context
    }

    return render(request, "inventory/inventory.html", context)

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import RawMaterial
from django.utils import timezone
from datetime import timedelta

def generate_shopping_list(request):
    today = timezone.now().date()
    warning_date = today + timedelta(days=5)

    # Filter raw materials that are expiring soon (within 5 days)
    expiring_soon = RawMaterial.objects.filter(
        exp_date__lte=warning_date, 
        exp_date__gte=today
    ).order_by('exp_date')

    # Create the HTTP response with content type as PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'

    # Create the PDF using ReportLab
    p = canvas.Canvas(response, pagesize=letter)

    # Set up the title
    p.setFont("Helvetica", 16)
    p.drawString(200, 750, "Shopping List: Items Expiring Soon")

    # Set up table headers
    p.setFont("Helvetica", 12)
    p.drawString(50, 700, "Name")
    p.drawString(200, 700, "Units")
    p.drawString(350, 700, "Expiration Date")

    # Draw the list of expiring items
    y_position = 680
    for mp in expiring_soon:
        p.drawString(50, y_position, mp.name)
        p.drawString(200, y_position, str(mp.units))
        p.drawString(350, y_position, str(mp.exp_date))
        y_position -= 20  # Move to next line

    # Save the PDF (only once)
    p.showPage()  # Finish the current page (if more pages are needed)
    p.save()  # Finalize the PDF document

    return response




def expiring_materials(request):
    today = timezone.now().date()
    warning_date = today + timedelta(days=5)

    expiring_soon = RawMaterial.objects.filter(exp_date__lte=warning_date, exp_date__gte=today).order_by('exp_date')

    return render(request, 'inventory/expiring_materials.html', {
        'expiring_soon': expiring_soon
    })

@login_required
@permission_required('inventory.change_rawmaterial', raise_exception=True)
def editar_materia_prima(request, pk):
    materia = get_object_or_404(RawMaterial, pk=pk)

    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('units'))
        anterior_cantidad = materia.units

        # Actualizar materia prima
        materia.name = request.POST.get('name')
        materia.units = nueva_cantidad
        materia.exp_date = request.POST.get('exp_date')
        materia.save()

        # Comparar cantidades para registrar entrada o salida
        diferencia = nueva_cantidad - anterior_cantidad
        if diferencia > 0:
            registrar_entrada(materia, diferencia)
        elif diferencia < 0:
            registrar_salida(materia, abs(diferencia))

        return redirect('inventory')

    return render(request, 'inventory/editar_materia.html', {'materia': materia})

@login_required
@permission_required('inventory.add_rawmaterial', raise_exception=True)
def create_raw_material(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        exp_date = request.POST.get('exp_date')

        rawMaterial = RawMaterial.objects.create(
            name=name,
            units=units,
            exp_date=exp_date
        )
        registrar_entrada(rawMaterial, units)
        return redirect('inventory')

    return render(request, 'inventory/create_raw_material.html')


def registrar_entrada(material, cantidad):
    MovimientosInventario.objects.create(
        material=material,
        movement_type='IN',
        quantity=cantidad
    )

def registrar_salida(material, cantidad):
    MovimientosInventario.objects.create(
        material=material,
        movement_type='OUT',
        quantity=cantidad
    )


def inventory_history(request):
    movimientos = MovimientosInventario.objects.all().order_by('-date')
    return render(request, 'inventory/inventory_history.html', {'movements': movimientos})
@login_required
def low_stock_alerts(request):
    """
    Vista para mostrar productos con stock bajo.
    Muestra productos donde quantity < reorder_threshold
    """
    from inventory.models import Product
    
    # Obtener productos con stock bajo
    low_stock_products = Product.objects.filter(
        quantity__lt=models.F('reorder_threshold')
    ).order_by('quantity')
    
    # Contar alertas críticas (menos del 50% del umbral)
    critical_count = low_stock_products.filter(
        quantity__lt=models.F('reorder_threshold') / 2
    ).count()
    
    context = {
        'low_stock_products': low_stock_products,
        'total_alerts': low_stock_products.count(),
        'critical_count': critical_count,
    }
    
    return render(request, 'inventory/low_stock_alerts.html', context)
