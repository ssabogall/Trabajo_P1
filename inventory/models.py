from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# Create your models here.

class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=50)
    exp_date = models.DateField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    picture = models.ImageField(upload_to='', blank=True, null=True)

    raw_materials = models.ManyToManyField(
        RawMaterial,
        through='ProductRawMaterial',
        related_name='products'
    )

    def __str__(self):
        return self.name

class ProductRawMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.FloatField()
    
    def __str__(self):
        return f"{self.product.name} - {self.raw_material.name} ({self.quantity})"

    class Meta:
        unique_together = ('product', 'raw_material')
        verbose_name = 'contador de materia prima'
        verbose_name_plural = 'contadores de materia prima'


class CountRawMaterial(models.Model):
    raw_material = models.OneToOneField(RawMaterial, on_delete=models.CASCADE, related_name='counter')  # ✅ OneToOne para relación 1:1
    total_quantity = models.FloatField(default=0)
    minimum_stock = models.FloatField(default=5)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.raw_material.name} - Stock: {self.total_quantity} {self.raw_material.units}"

    def is_low_stock(self):
        return self.total_quantity <= self.minimum_stock
    
    class Meta:
        verbose_name = "Contador de Materia Prima"
        verbose_name_plural = "Contadores de Materias Primas"

# Señales para actualizar automáticamente cuando se agrega/elimina ProductRawMaterial
@receiver(post_save, sender=ProductRawMaterial)
def update_raw_material_count_on_add(sender, instance, created, **kwargs):
    """Actualizar contador cuando se agrega relación producto-materia prima"""
    if created:
        counter = CountRawMaterial.get_or_create_counter(instance.raw_material)
        # No reducir automáticamente, solo asegurar que existe el contador

@receiver(post_delete, sender=ProductRawMaterial)
def update_raw_material_count_on_delete(sender, instance, **kwargs):
    """Actualizar contador cuando se elimina relación"""
    try:
        counter = CountRawMaterial.objects.get(raw_material=instance.raw_material)
        # Mantener el contador, solo notificar que se eliminó la relación
    except CountRawMaterial.DoesNotExist:
        pass
    
class ProductInventory(models.Model):
    product = models.OneToOneField (Product, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField (default=0)
    minimum_stock = models.IntegerField (default=2)
    last_updated = models.DateTimeField (auto_now=True)

    def __str__(self):
        return f"{self.product.name} - Stock: {self.stock_quantity}"
    
    def is_low_stock(self):
        return self.stock_quantity <= self.minimum_stock

