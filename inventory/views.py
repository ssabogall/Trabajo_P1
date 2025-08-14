from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from .models import RawMaterial, CountRawMaterial, Product
import json

def inventory(request):
    """Vista principal del inventario"""
    raw_materials_with_count = []
    
    # Obtener todas las materias primas y sus contadores
    for raw_material in RawMaterial.objects.all():
        counter, created = CountRawMaterial.objects.get_or_create(
            raw_material=raw_material,
            defaults={'total_quantity': 0, 'minimum_stock': 0}
        )
        raw_materials_with_count.append({
            'raw_material': raw_material,
            'counter': counter,
            'products_using': raw_material.products.count()
        })
    
    # Debug: Imprimir para verificar estructura
    print("DEBUG - Datos enviados:", raw_materials_with_count)
    
    context = {
        'raw_materials_with_count': raw_materials_with_count,
        'total_products': Product.objects.count(),
        'materias_primas': RawMaterial.objects.all(),  # Para compatibilidad con template básico
    }
    
    return render(request, 'inventory/inventory.html', context)

@csrf_exempt
def update_stock(request):
    """Actualizar stock via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            raw_material_id = data.get('raw_material_id')
            action = data.get('action')
            quantity = float(data.get('quantity', 1))
            
            raw_material = get_object_or_404(RawMaterial, id=raw_material_id)
            counter, created = CountRawMaterial.objects.get_or_create(
                raw_material=raw_material,
                defaults={'total_quantity': 0, 'minimum_stock': 0}
            )
            
            if action == 'add':
                counter.total_quantity += quantity
                counter.save()
                success = True
                message = f"Se agregaron {quantity} {raw_material.units}"
            elif action == 'remove':
                if counter.total_quantity >= quantity:
                    counter.total_quantity -= quantity
                    counter.save()
                    success = True
                    message = f"Se redujeron {quantity} {raw_material.units}"
                else:
                    success = False
                    message = "Stock insuficiente"
            else:
                success = False
                message = "Acción no válida"
            
            return JsonResponse({
                'success': success,
                'message': message,
                'new_quantity': counter.total_quantity,
                'is_low_stock': counter.total_quantity <= counter.minimum_stock
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def editar_materia_prima(request, pk):
    """Vista para editar una materia prima desde el inventario"""
    from django.contrib import messages
    
    raw_material = get_object_or_404(RawMaterial, pk=pk)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('name', '').strip()
        units = request.POST.get('units', '').strip()
        exp_date = request.POST.get('exp_date')
        
        if name and units and exp_date:
            # Actualizar la materia prima
            raw_material.name = name
            raw_material.units = units
            raw_material.exp_date = exp_date
            raw_material.save()
            
            messages.success(request, f'✅ Materia prima "{name}" actualizada correctamente')
            return redirect('inventory:inventory')
        else:
            messages.error(request, '❌ Todos los campos son obligatorios')
    
    context = {
        'raw_material': raw_material
    }
    return render(request, 'inventory/editar_materia_prima.html', context)
