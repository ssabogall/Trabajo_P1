from django.shortcuts import get_object_or_404, redirect, render
from .models import RawMaterial
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.utils.timezone import now, timedelta
from .utils.pagination_helper import PaginationHelper

def inventory(request):
    today = now().date()
    soon = today + timedelta(days=5)
    expiring_soon = RawMaterial.objects.filter(exp_date__lte=soon, exp_date__gte=today)

    dismissed = request.GET.get("dismissed") == "1"
    show_modal = bool(expiring_soon) and not dismissed

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
        **pagination.get_context()  # Add pagination context
    }

    return render(request, "inventory/inventory.html", context)

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
        materia.name = request.POST.get('name')
        materia.units = request.POST.get('units')
        materia.exp_date = request.POST.get('exp_date')
        materia.save()
        return redirect('inventory')

    return render(request, 'inventory/editar_materia.html', {'materia': materia})

@login_required
@permission_required('inventory.add_rawmaterial', raise_exception=True)
def create_raw_material(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        exp_date = request.POST.get('exp_date')

        RawMaterial.objects.create(
            name=name,
            units=units,
            exp_date=exp_date
        )
        return redirect('inventory')

    return render(request, 'inventory/create_raw_material.html')

