# inventory/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, ProductRawMaterial

@receiver(post_save, sender=OrderItem)
def deduct_raw_material_inventory(sender, instance, created, **kwargs):
    if created:  # Only run when new OrderItem is created
        product = instance.product
        quantity_ordered = instance.quantity

        # Get all raw materials for this product
        product_materials = ProductRawMaterial.objects.filter(product=product)

        for pm in product_materials:
            required_amount = pm.material_quantity * quantity_ordered
            raw_material = pm.material

            print(f"Deducting {required_amount} {raw_material.units} of {raw_material.name}")

            raw_material.units -= required_amount
            raw_material.save()


# [[AGREGADO]] Set unit_price usando precio efectivo (con promoción) al crear OrderItem
from django.db.models.signals import pre_save
from inventory.promo_utils import price_after_discount
from .models import OrderItem

@receiver(pre_save, sender=OrderItem)
def set_unit_price_from_promo(sender, instance, **kwargs):
    try:
        # Si ya viene unit_price (>0), no lo tocamos
        if instance.unit_price and float(instance.unit_price) > 0:
            return
    except Exception:
        pass
    # Precio efectivo del producto en el momento actual
    effective = price_after_discount(instance.product)
    instance.unit_price = effective
