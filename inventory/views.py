from django.shortcuts import get_object_or_404, redirect, render
from .models import RawMaterial
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from datetime import timedelta

def inventory(request):
    today = timezone.now().date()
    warning_date = today + timedelta(days=5)

    materias_primas = RawMaterial.objects.all()
    expiring_soon = RawMaterial.objects.filter(exp_date__lte=warning_date, exp_date__gte=today).order_by('exp_date')

    return render(request, 'inventory/inventory.html', {
        'materias_primas': materias_primas,
        'expiring_soon': expiring_soon
    })

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

