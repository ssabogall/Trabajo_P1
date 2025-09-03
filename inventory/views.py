from django.shortcuts import get_object_or_404, redirect, render
from .models import RawMaterial
from django.contrib.auth.decorators import login_required, permission_required

def inventory(request):
    materias_primas = RawMaterial.objects.all()
    return render(request, 'inventory/inventory.html', {
        'materias_primas': materias_primas
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

