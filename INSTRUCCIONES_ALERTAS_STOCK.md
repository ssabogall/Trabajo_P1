# 🚨 Sistema de Alertas de Stock Bajo - Banetón

## 📋 Resumen del Requisito Implementado

**Requisito:** 
> THE Baneton system SHALL PROVIDE operations WITH THE ABILITY TO RECEIVE low-stock alerts FOR EACH product AT EACH MOMENT WHEN quantity IS BELOW the reorder threshold

## ✅ Lo que se implementó:

### 1. Modelo de Datos (inventory/models.py)
Se agregó al modelo `Product`:
- **Campo `reorder_threshold`**: Define el umbral mínimo de stock (default: 10 unidades)
- **Método `is_low_stock()`**: Retorna True si el producto está bajo stock
- **Método `stock_percentage()`**: Calcula el % de stock actual respecto al umbral

### 2. Vista de Alertas (inventory/views.py)
- **Función `low_stock_alerts()`**: Muestra todos los productos con stock bajo
  - Filtra productos donde `quantity < reorder_threshold`
  - Calcula alertas críticas (< 50% del umbral)
  - Ordena por cantidad ascendente

### 3. URL (inventory/urls.py)
- Nueva ruta: `/inventory/low-stock/`
- Nombre: `low_stock_alerts`

### 4. Template HTML (inventory/templates/inventory/low_stock_alerts.html)
Interfaz visual con:
- 📊 Dashboard con estadísticas (Total alertas, Críticas, Advertencias)
- 🎨 Tarjetas de productos con código de colores
- 📈 Barra de progreso visual del stock
- 🏷️ Badges de severidad (Crítico/Advertencia)

### 5. Integración en Dashboard Principal
- Banner de alerta en `/inventory/` cuando hay productos con stock bajo
- Link directo a la página de alertas

## 🔧 Pasos para Activar el Sistema

### 1. Aplicar las Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Configurar Umbrales de Reorden
Puedes hacerlo de 3 formas:

**A) Desde el Admin de Django:**
```python
# Accede a http://localhost:8000/admin/
# Ve a Inventory > Products
# Edita cada producto y establece el "Reorder threshold"
```

**B) Desde la shell de Django:**
```bash
python manage.py shell
```
```python
from inventory.models import Product

# Establecer umbral para un producto específico
producto = Product.objects.get(name="Croissant")
producto.reorder_threshold = 15
producto.save()

# Establecer umbral para todos los productos
Product.objects.all().update(reorder_threshold=20)

# Umbral personalizado por producto
products_config = {
    "Croissant": 25,
    "Pan Francés": 30,
    "Galleta de Chocolate": 15,
}

for name, threshold in products_config.items():
    Product.objects.filter(name=name).update(reorder_threshold=threshold)
```

**C) Crear un script de gestión:**
```python
# Crea: inventory/management/commands/set_thresholds.py
from django.core.management.base import BaseCommand
from inventory.models import Product

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Product.objects.filter(name__contains="Pan").update(reorder_threshold=30)
        Product.objects.filter(name__contains="Galleta").update(reorder_threshold=15)
        self.stdout.write("Umbrales actualizados")
```

### 3. Acceder al Sistema de Alertas

**URLs disponibles:**
- `/inventory/` - Dashboard principal (muestra banner si hay alertas)
- `/inventory/low-stock/` - Página dedicada de alertas

## 📊 Cómo Funciona

### Criterios de Alerta:
1. **Advertencia** 🟡: `quantity < reorder_threshold` pero `>= reorder_threshold / 2`
2. **Crítico** 🔴: `quantity < reorder_threshold / 2`

### Ejemplo:
```
Producto: Croissant
Umbral de reorden: 20 unidades
Stock actual: 8 unidades

Estado: CRÍTICO ⚠️
Razón: 8 < 10 (50% de 20)
Acción: Reabastecer urgentemente
```

## 🎯 Casos de Uso

### Caso 1: Operador revisa alertas al iniciar el día
```
1. Login → Dashboard
2. Ve banner: "⚠️ 3 productos con stock bajo"
3. Click en "View Details"
4. Revisa cada producto
5. Ordena reabastecimiento para productos críticos
```

### Caso 2: Sistema muestra alertas en tiempo real
```
- Cada venta reduce el stock
- Si después de una venta: quantity < reorder_threshold
- El sistema automáticamente lo muestra en /low-stock/
- No requiere refresh manual
```

## 🔍 Verificación del Sistema

### Test Manual:
```python
# En Django shell
from inventory.models import Product

# Crear producto de prueba
p = Product.objects.create(
    name="Test Product",
    quantity=5,
    reorder_threshold=10,
    price=1000
)

# Verificar que aparece en alertas
print(p.is_low_stock())  # Debe retornar True

# Acceder a /inventory/low-stock/ y verificar que aparece
```

## 🛠️ Personalización

### Cambiar colores de severidad:
Edita `low_stock_alerts.html`:
```css
.badge-critical {
    background: #tu-color-critico;
}
.badge-warning {
    background: #tu-color-advertencia;
}
```

### Cambiar umbrales de criticidad:
Edita `views.py` línea ~95:
```python
# Cambiar de 50% a 30%
critical_count = low_stock_products.filter(
    quantity__lt=models.F('reorder_threshold') * 0.3
).count()
```

## 📝 Notas Importantes

1. **Permisos**: La vista `low_stock_alerts` requiere login (`@login_required`)
2. **Performance**: Usa queries optimizadas con `F()` expressions
3. **Escalabilidad**: Soporta miles de productos sin problemas
4. **Responsive**: La interfaz se adapta a móviles y tablets

## 🐛 Troubleshooting

### Error: "No module named 'inventory.models'"
```bash
# Verifica que estés en el directorio correcto
cd /path/to/Trabajo_P1
python manage.py shell
```

### Alertas no aparecen:
1. Verifica que los productos tengan `reorder_threshold` configurado
2. Verifica que `quantity < reorder_threshold`
3. Revisa los logs: `python manage.py runserver --verbosity 3`

### Template no se encuentra:
```bash
# Verifica la estructura:
inventory/
  templates/
    inventory/
      low_stock_alerts.html
```

## 📚 Documentación Relacionada

- Django QuerySets: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- F() expressions: https://docs.djangoproject.com/en/stable/ref/models/expressions/
- Template tags: https://docs.djangoproject.com/en/stable/ref/templates/builtins/

---

## 🎉 ¡Sistema Listo!

El sistema de alertas de stock bajo está completamente implementado y listo para usar.
Para cualquier duda o personalización adicional, revisa este documento o consulta el código fuente.
